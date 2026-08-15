import os
import sqlite3
from datetime import datetime

from flask import (
    Flask,
    request,
    send_from_directory,
    session,
    redirect
)

# ==================================================
# FLASK APP
# ==================================================

app = Flask(__name__)
app.secret_key = "rakshak_secret_key_2026"

# ==================================================
# PROJECT PATH
# ==================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../.."))

TEMPLATES_DIR = os.path.join(PROJECT_DIR, "templates")
DATABASE = os.path.join(PROJECT_DIR, "rakshak.db")

# ==================================================
# DATABASE
# ==================================================

def init_db():
    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            location TEXT NOT NULL,
            latitude TEXT,
            longitude TEXT,
            accident_type TEXT NOT NULL,
            description TEXT NOT NULL,
            report_date TEXT,
            report_time TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            user_type TEXT NOT NULL
        )
    """)

    columns = conn.execute("PRAGMA table_info(reports)").fetchall()
    column_names = [column[1] for column in columns]

    required_columns = {
        "latitude": "ALTER TABLE reports ADD COLUMN latitude TEXT",
        "longitude": "ALTER TABLE reports ADD COLUMN longitude TEXT",
        "report_date": "ALTER TABLE reports ADD COLUMN report_date TEXT",
        "report_time": "ALTER TABLE reports ADD COLUMN report_time TEXT",
        "status": "ALTER TABLE reports ADD COLUMN status TEXT DEFAULT 'Pending'"
    }

    for column_name, sql in required_columns.items():
        if column_name not in column_names:
            try:
                conn.execute(sql)
            except sqlite3.OperationalError:
                pass

    conn.commit()
    conn.close()


init_db()

# ==================================================
# HOME / STATIC PAGES
# ==================================================

@app.route("/")
def home():
    return send_from_directory(TEMPLATES_DIR, "index.html")


@app.route("/about.html")
def about():
    return send_from_directory(TEMPLATES_DIR, "about.html")


@app.route("/contact.html")
def contact():
    return send_from_directory(TEMPLATES_DIR, "contact.html")


@app.route("/emergency.html")
def emergency():
    return send_from_directory(TEMPLATES_DIR, "emergency.html")


@app.route("/hospital.html")
def hospital():
    return send_from_directory(TEMPLATES_DIR, "hospital.html")


@app.route("/login.html")
def login():
    return send_from_directory(TEMPLATES_DIR, "login.html")


@app.route("/register.html")
def register():
    return send_from_directory(TEMPLATES_DIR, "register.html")

# ==================================================
# REGISTER USER
# ==================================================

@app.route("/register-user", methods=["POST"])
def register_user():

    name = request.form.get("name")
    mobile = request.form.get("mobile")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirmPassword")
    user_type = request.form.get("user_type")

    if not all([
        name,
        mobile,
        email,
        password,
        confirm_password,
        user_type
    ]):
        return """
        <div style="text-align:center;font-family:Arial;padding-top:100px;">
            <h2 style="color:red;">❌ Please fill all required fields.</h2>
            <a href="/register.html">Go Back</a>
        </div>
        """

    if password != confirm_password:
        return """
        <div style="text-align:center;font-family:Arial;padding-top:100px;">
            <h2 style="color:red;">❌ Passwords do not match</h2>
            <a href="/register.html">Go Back</a>
        </div>
        """

    conn = sqlite3.connect(DATABASE)

    try:
        conn.execute("""
            INSERT INTO users
            (name, mobile, email, password, user_type)
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            mobile,
            email,
            password,
            user_type
        ))

        conn.commit()

    except sqlite3.IntegrityError:
        conn.close()

        return """
        <div style="text-align:center;font-family:Arial;padding-top:100px;">
            <h2 style="color:red;">❌ Email Already Registered</h2>
            <a href="/login.html">Go to Login</a>
        </div>
        """

    conn.close()

    return """
    <div style="text-align:center;font-family:Arial;padding-top:100px;">
        <h1 style="color:green;">✅ Registration Successful!</h1>
        <p>Your RAKSHAK account has been created.</p>
        <a href="/login.html">🔐 Login Now</a>
    </div>
    """

# ==================================================
# LOGIN USER
# ==================================================

@app.route("/login-user", methods=["POST"])
def login_user():

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()

    print("LOGIN EMAIL:", repr(email))
    print("LOGIN PASSWORD:", repr(password))
    print("DATABASE:", DATABASE)

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    user = conn.execute("""
        SELECT *
        FROM users
        WHERE TRIM(email) = ?
        AND password = ?
    """, (
        email,
        password
    )).fetchone()

    conn.close()

    print("LOGIN USER FOUND:", dict(user) if user else None)

    # LOGIN SUCCESS
    if user:

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]
        session["user_mobile"] = user["mobile"]
        session["user_type"] = user["user_type"]

        print("LOGIN SUCCESS:", user["user_type"])

        # Police
        if user["user_type"] == "Police":
            return redirect("/police")

        # Normal User
        return redirect("/dashboard")

    # LOGIN FAILED
    return """
    <div style="
        text-align:center;
        font-family:Arial;
        padding-top:100px;
    ">

        <h1 style="color:red;">
            ❌ Login Failed
        </h1>

        <p>
            Invalid email or password.
        </p>

        <a href="/login.html">
            🔐 Try Again
        </a>

    </div>
    """, 401
    
  
# ==================================================
# USER DASHBOARD
# ==================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login.html")

    # Logged-in user's mobile
    user_mobile = session.get("user_mobile")

    # Database
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    # Get user's reports
    user_reports = conn.execute("""
        SELECT *
        FROM reports
        WHERE mobile = ?
        ORDER BY id DESC
    """, (user_mobile,)).fetchall()

    conn.close()

    # Open dashboard HTML
    dashboard_html = open(
        os.path.join(TEMPLATES_DIR, "dashboard.html"),
        encoding="utf-8"
    ).read()

    # Create report section
    reports_html = """
    <div class="info-box">

        <h2>🚨 My Accident Reports</h2>

    """

    if not user_reports:

        reports_html += """
        <p>
            📋 You have not submitted any accident reports yet.
        </p>
        """

    else:

        for report in user_reports:

            status = report["status"] or "Pending"

            if status == "Pending":
                status_color = "#856404"
                status_bg = "#fff3cd"
                icon = "🟡"

            elif status == "In Progress":
                status_color = "#084298"
                status_bg = "#cfe2ff"
                icon = "🔵"

            else:
                status_color = "#0f5132"
                status_bg = "#d1e7dd"
                icon = "🟢"

            reports_html += f"""

            <div style="
                background:#f8f9fa;
                padding:20px;
                margin-top:20px;
                border-radius:12px;
                border-left:5px solid #c62828;
            ">

                <h3 style="color:#c62828;">
                    🚨 Report #{report["id"]}
                </h3>

                <p>
                    🚨 <b>Accident Type:</b>
                    {report["accident_type"]}
                </p>

                <p>
                    📍 <b>Location:</b>
                    {report["location"]}
                </p>

                <p>
                    📅 <b>Date:</b>
                    {report["report_date"] or "Not Available"}
                </p>

                <p>
                    ⏰ <b>Time:</b>
                    {report["report_time"] or "Not Available"}
                </p>

                <p>
                    📝 <b>Description:</b>
                    {report["description"]}
                </p>

                <div style="
                    background:{status_bg};
                    color:{status_color};
                    padding:12px;
                    border-radius:8px;
                    font-weight:bold;
                    margin-top:15px;
                ">

                    {icon}
                    Current Status: {status}

                </div>

            </div>

            """

    reports_html += "</div>"

    # Add reports before safety information
    dashboard_html = dashboard_html.replace(
        '<!-- ============================= -->\n<!-- SAFETY INFORMATION -->',
        reports_html + '\n\n<!-- ============================= -->\n<!-- SAFETY INFORMATION -->'
    )

    return dashboard_html

# ==================================================
# LOGOUT
# ==================================================

@app.route("/logout")
def logout():

    session.clear()
    return redirect("/login.html")

# ==================================================
# REPORT PAGE
# ==================================================

@app.route("/report")
def report():

    if "user_id" not in session:
        return redirect("/login.html")

    return send_from_directory(TEMPLATES_DIR, "report.html")

# ==================================================
# SUBMIT ACCIDENT REPORT
# ==================================================

@app.route("/submit-report", methods=["POST"])
def submit_report():

    name = request.form.get("name")
    mobile = request.form.get("mobile")
    location = request.form.get("location")
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")
    accident_type = request.form.get("accident_type")
    description = request.form.get("description")

    if not all([
        name,
        mobile,
        location,
        latitude,
        longitude,
        accident_type,
        description
    ]):
        return """
        <div style="text-align:center;font-family:Arial;padding-top:100px;">
            <h1 style="color:red;">❌ Location or required data missing</h1>
            <p>Please allow location access and try again.</p>
            <a href="/report">🚨 Go Back</a>
        </div>
        """, 400

    now = datetime.now()

    report_date = now.strftime("%d-%m-%Y")
    report_time = now.strftime("%I:%M:%S %p")

    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        INSERT INTO reports
        (
            name,
            mobile,
            location,
            latitude,
            longitude,
            accident_type,
            description,
            report_date,
            report_time,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        mobile,
        location,
        latitude,
        longitude,
        accident_type,
        description,
        report_date,
        report_time,
        "Pending"
    ))

    conn.commit()
    conn.close()

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>RAKSHAK</title>
    </head>

    <body style="
        text-align:center;
        font-family:Arial;
        padding-top:80px;
        background:#f5f5f5;
    ">

        <div style="
            background:white;
            max-width:600px;
            margin:auto;
            padding:40px;
            border-radius:15px;
            box-shadow:0 5px 20px rgba(0,0,0,0.15);
        ">

            <h1 style="color:green;">
                ✅ Report Submitted Successfully!
            </h1>

            <p>🚑 Your accident report has been saved.</p>

            <p>
                📅 Date:
                <b>{report_date}</b>
            </p>

            <p>
                ⏰ Time:
                <b>{report_time}</b>
            </p>

            <p>
                📍 Location:
                <b>{latitude}, {longitude}</b>
            </p>

            <p>
                🟡 Status:
                <b>Pending</b>
            </p>

            <br>

            <a href="/report" style="
                background:#c62828;
                color:white;
                padding:12px 20px;
                text-decoration:none;
                border-radius:7px;
            ">
                🚨 Submit Another Report
            </a>

            <br><br>

            <a href="/dashboard">🏠 Dashboard</a>

        </div>

    </body>
    </html>
    """

# ==================================================
# EMERGENCY SOS
# ==================================================

@app.route("/sos", methods=["POST"])
def sos():

    if "user_id" not in session:
        return redirect("/login.html")

    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")

    if not latitude or not longitude:
        return "Location not available", 400

    now = datetime.now()

    report_date = now.strftime("%d-%m-%Y")
    report_time = now.strftime("%I:%M:%S %p")

    location = f"{latitude}, {longitude}"

    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        INSERT INTO reports
        (
            name,
            mobile,
            location,
            latitude,
            longitude,
            accident_type,
            description,
            report_date,
            report_time,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "Emergency SOS",
        "Not Provided",
        location,
        latitude,
        longitude,
        "Emergency SOS",
        "Emergency SOS activated",
        report_date,
        report_time,
        "Pending"
    ))

    conn.commit()
    conn.close()

    return """
    <div style="
        text-align:center;
        font-family:Arial;
        padding-top:100px;
    ">
        <h1 style="color:green;">🚨 SOS Saved Successfully</h1>
        <p>Emergency SOS has been recorded.</p>
        <a href="/dashboard">🏠 Dashboard</a>
    </div>
    """

# ==================================================
# POLICE HTML PAGE
# ==================================================

@app.route("/police.html")
def police_page():

    if "user_id" not in session:
        return redirect("/login.html")

    if session.get("user_type") != "Police":
        return """
        <div style="
            text-align:center;
            font-family:Arial;
            padding-top:100px;
        ">
            <h1 style="color:red;">❌ Access Denied</h1>
            <h3>Police users only.</h3>
            <p>You do not have permission to access this page.</p>
            <a href="/dashboard">🏠 Back to Dashboard</a>
        </div>
        """, 403

    return redirect("/police")

# ==================================================
# POLICE DASHBOARD
# ==================================================

@app.route("/police")
def police():

    if "user_id" not in session:
        return redirect("/login.html")

    if session.get("user_type") != "Police":
        return """
        <div style="
            text-align:center;
            font-family:Arial;
            padding-top:100px;
        ">
            <h1 style="color:red;">❌ Access Denied</h1>
            <h3>Police users only.</h3>
            <p>You are logged in as a normal user.</p>
            <a href="/dashboard">🏠 Back to Dashboard</a>
        </div>
        """, 403

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    total_reports = conn.execute(
        "SELECT COUNT(*) FROM reports"
    ).fetchone()[0]

    pending_reports = conn.execute("""
        SELECT COUNT(*)
        FROM reports
        WHERE status = 'Pending'
    """).fetchone()[0]

    progress_reports = conn.execute("""
        SELECT COUNT(*)
        FROM reports
        WHERE status = 'In Progress'
    """).fetchone()[0]

    resolved_reports = conn.execute("""
        SELECT COUNT(*)
        FROM reports
        WHERE status = 'Resolved'
    """).fetchone()[0]

    recent_reports = conn.execute("""
        SELECT *
        FROM reports
        ORDER BY id DESC
        LIMIT 3
    """).fetchall()

    conn.close()

    recent_html = ""

    if recent_reports:

        for item in recent_reports:

            status = item["status"] or "Pending"

            if status == "Pending":
                status_class = "pending"
                icon = "🟡"
            elif status == "In Progress":
                status_class = "progress"
                icon = "🔵"
            else:
                status_class = "resolved"
                icon = "🟢"

            recent_html += f"""
            <div class="recent-report">

                <div>
                    <b>🚨 Report #{item["id"]}</b>
                    <br>
                    👤 {item["name"]}
                    <br>
                    🚨 {item["accident_type"]}
                    <br>
                    📅 {item["report_date"] or "Not Available"}
                    &nbsp;
                    ⏰ {item["report_time"] or "Not Available"}
                </div>

                <span class="mini-status {status_class}">
                    {icon} {status}
                </span>

            </div>
            """

    else:

        recent_html = """
        <div class="no-recent">
            📋 No accident reports available yet.
        </div>
        """

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>RAKSHAK Police Dashboard</title>

        <style>

            * {{
                box-sizing:border-box;
                font-family:Arial,sans-serif;
            }}

            body {{
                margin:0;
                background:#f4f6f8;
            }}

            nav {{
                background:#c62828;
                color:white;
                padding:18px 30px;
                display:flex;
                justify-content:space-between;
                align-items:center;
            }}

            nav h2 {{
                margin:0;
            }}

            .logout {{
                color:white;
                text-decoration:none;
                font-weight:bold;
            }}

            .container {{
                width:90%;
                max-width:1100px;
                margin:40px auto;
            }}

            h1 {{
                text-align:center;
                color:#c62828;
            }}

            .stats {{
                display:flex;
                gap:20px;
                justify-content:center;
                flex-wrap:wrap;
                margin:35px 0;
            }}

            .card {{
                background:white;
                width:210px;
                padding:25px;
                text-align:center;
                border-radius:15px;
                box-shadow:0 5px 20px rgba(0,0,0,0.12);
            }}

            .card h2 {{
                color:#c62828;
                font-size:38px;
                margin-bottom:0;
            }}

            .main,
            .recent-box {{
                background:white;
                padding:35px;
                border-radius:15px;
                text-align:center;
                margin-bottom:25px;
                box-shadow:0 5px 20px rgba(0,0,0,0.08);
            }}

            .btn {{
                display:inline-block;
                margin-top:20px;
                padding:14px 25px;
                background:#c62828;
                color:white;
                text-decoration:none;
                border-radius:7px;
                font-weight:bold;
            }}

            .recent-report {{
                display:flex;
                justify-content:space-between;
                align-items:center;
                gap:20px;
                text-align:left;
                background:#f8f9fa;
                padding:18px;
                margin:12px 0;
                border-radius:10px;
                border-left:5px solid #c62828;
            }}

            .mini-status {{
                padding:8px 12px;
                border-radius:7px;
                font-weight:bold;
                white-space:nowrap;
            }}

            .pending {{
                background:#fff3cd;
                color:#856404;
            }}

            .progress {{
                background:#cfe2ff;
                color:#084298;
            }}

            .resolved {{
                background:#d1e7dd;
                color:#0f5132;
            }}

            .no-recent {{
                padding:25px;
                background:#f8f9fa;
                border-radius:10px;
            }}

            @media(max-width:650px) {{

                .recent-report {{
                    flex-direction:column;
                    align-items:flex-start;
                }}

                .card {{
                    width:100%;
                    max-width:300px;
                }}

                .container {{
                    width:94%;
                }}

            }}

        </style>

    </head>

    <body>

        <nav>

            <h2>🚑 RAKSHAK</h2>

            <a href="/logout" class="logout">
                🚪 Logout
            </a>

        </nav>

        <div class="container">

            <h1>👮 Police Dashboard</h1>

            <div class="stats">

                <div class="card">
                    <p>🚨 Total Reports</p>
                    <h2>{total_reports}</h2>
                </div>

                <div class="card">
                    <p>🟡 Pending</p>
                    <h2>{pending_reports}</h2>
                </div>

                <div class="card">
                    <p>🔵 In Progress</p>
                    <h2>{progress_reports}</h2>
                </div>

                <div class="card">
                    <p>🟢 Resolved</p>
                    <h2>{resolved_reports}</h2>
                </div>

            </div>

            <div class="main">

                <h2>🚨 Accident Reports</h2>

                <p>
                    View accident location, date, time and status.
                </p>

                <a href="/reports" class="btn">
                    📋 View All Accident Reports
                </a>

            </div>

            <div class="recent-box">

                <h2>🚨 Recent Accident Reports</h2>

                <p>
                    Latest accident and emergency reports
                </p>

                {recent_html}

                <a href="/reports" class="btn">
                    📋 View All Reports
                </a>

            </div>

        </div>

    </body>

    </html>
    """

# ==================================================
# UPDATE REPORT STATUS
# ==================================================

@app.route("/update-status/<int:report_id>", methods=["POST"])
def update_status(report_id):

    if "user_id" not in session:
        return redirect("/login.html")

    if session.get("user_type") != "Police":
        return """
        <div style="
            text-align:center;
            font-family:Arial;
            padding-top:100px;
        ">
            <h1 style="color:red;">❌ Access Denied</h1>
            <p>Only Police users can update report status.</p>
            <a href="/dashboard">🏠 Back to Dashboard</a>
        </div>
        """, 403

    new_status = request.form.get("status")

    allowed_statuses = [
        "Pending",
        "In Progress",
        "Resolved"
    ]

    if new_status not in allowed_statuses:
        return "Invalid Status", 400

    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        UPDATE reports
        SET status = ?
        WHERE id = ?
    """, (
        new_status,
        report_id
    ))

    conn.commit()
    conn.close()

    return redirect("/reports")

# ==================================================
# ALL REPORTS
# ==================================================

@app.route("/reports")
def reports():

    if "user_id" not in session:
        return redirect("/login.html")

    if session.get("user_type") != "Police":
        return """
        <div style="
            text-align:center;
            font-family:Arial;
            padding-top:100px;
        ">
            <h1 style="color:red;">❌ Access Denied</h1>
            <h3>Police users only.</h3>
            <p>Only Police users can view accident reports.</p>
            <a href="/dashboard">🏠 Back to Dashboard</a>
        </div>
        """, 403

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    reports_data = conn.execute("""
        SELECT *
        FROM reports
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    html = """
    <!DOCTYPE html>

    <html lang="en">

    <head>

        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>RAKSHAK - Accident Reports</title>

        <style>

            * {
                box-sizing:border-box;
                font-family:Arial,sans-serif;
            }

            body {
                margin:0;
                background:#f4f6f8;
            }

            nav {
                background:#c62828;
                color:white;
                padding:18px 30px;
                display:flex;
                justify-content:space-between;
                align-items:center;
            }

            nav h2 {
                margin:0;
            }

            .logout {
                color:white;
                text-decoration:none;
                font-weight:bold;
            }

            .container {
                width:92%;
                max-width:1100px;
                margin:35px auto;
            }

            h1 {
                text-align:center;
                color:#c62828;
                margin-bottom:30px;
            }

            .filter-box {
                background:white;
                padding:20px;
                border-radius:12px;
                margin-bottom:25px;
                box-shadow:0 5px 15px rgba(0,0,0,0.08);
                display:flex;
                gap:15px;
                flex-wrap:wrap;
            }

            .filter-box input {
                flex:1;
                min-width:250px;
                padding:12px;
                border:1px solid #ccc;
                border-radius:7px;
                font-size:15px;
            }

            .filter-box select {
                padding:12px;
                border:1px solid #ccc;
                border-radius:7px;
                font-size:15px;
            }

            .report {
                background:white;
                padding:25px;
                margin-bottom:25px;
                border-radius:15px;
                box-shadow:0 5px 20px rgba(0,0,0,0.12);
            }

            .report h2 {
                color:#c62828;
                margin-top:0;
            }

            .status {
                padding:12px;
                border-radius:8px;
                font-weight:bold;
                margin:15px 0;
            }

            .pending {
                background:#fff3cd;
                color:#856404;
            }

            .progress {
                background:#cfe2ff;
                color:#084298;
            }

            .resolved {
                background:#d1e7dd;
                color:#0f5132;
            }

            .location {
                background:#e3f2fd;
                padding:18px;
                border-radius:10px;
                margin:20px 0;
            }

            .location h3 {
                color:#1976d2;
                margin-top:0;
            }

            .map-btn {
                display:inline-block;
                margin-top:12px;
                padding:11px 18px;
                background:#1976d2;
                color:white;
                text-decoration:none;
                border-radius:7px;
                font-weight:bold;
            }

            .info {
                line-height:1.8;
            }

            hr {
                border:none;
                border-top:1px solid #ddd;
                margin:25px 0;
            }

            select {
                padding:10px;
                border:1px solid #ccc;
                border-radius:7px;
                font-size:15px;
            }

            button {
                padding:10px 18px;
                background:#c62828;
                color:white;
                border:none;
                border-radius:7px;
                font-weight:bold;
                cursor:pointer;
            }

            .bottom-btn {
                display:block;
                width:fit-content;
                margin:20px auto;
                padding:12px 22px;
                background:#c62828;
                color:white;
                text-decoration:none;
                border-radius:7px;
                font-weight:bold;
            }

            .no-reports {
                background:white;
                padding:40px;
                text-align:center;
                border-radius:15px;
            }

        </style>

    </head>

    <body>

        <nav>

            <h2>🚑 RAKSHAK</h2>

            <a href="/logout" class="logout">
                🚪 Logout
            </a>

        </nav>

        <div class="container">

            <h1>🚨 Accident Reports</h1>

            <div class="filter-box">

                <input
                    type="text"
                    id="searchInput"
                    placeholder="🔎 Search by name, mobile or accident type..."
                    onkeyup="filterReports()"
                >

                <select
                    id="statusFilter"
                    onchange="filterReports()"
                >
                    <option value="All">All Status</option>
                    <option value="Pending">🟡 Pending</option>
                    <option value="In Progress">🔵 In Progress</option>
                    <option value="Resolved">🟢 Resolved</option>
                </select>

            </div>
    """

    if not reports_data:

        html += """
            <div class="no-reports">
                <h2>📋 No Accident Reports</h2>
                <p>
                    No accident or SOS reports
                    have been submitted yet.
                </p>
            </div>
        """

    else:

        for report_item in reports_data:

            current_status = report_item["status"] or "Pending"

            if current_status == "Pending":
                status_class = "pending"
                status_icon = "🟡"
            elif current_status == "In Progress":
                status_class = "progress"
                status_icon = "🔵"
            else:
                status_class = "resolved"
                status_icon = "🟢"

            latitude = report_item["latitude"]
            longitude = report_item["longitude"]

            if latitude and longitude:

                map_url = (
                    "https://www.google.com/maps/search/?api=1&query="
                    + str(latitude)
                    + ","
                    + str(longitude)
                )

            else:
                map_url = "#"

            html += f"""

            <div class="report">

                <h2>
                    🚨 Report #{report_item['id']}
                </h2>

                <div class="status {status_class}">
                    {status_icon}
                    Status: {current_status}
                </div>

                <div class="info">

                    <p>
                        👤 <b>Name:</b>
                        {report_item['name']}
                    </p>

                    <p>
                        📱 <b>Mobile:</b>
                        {report_item['mobile']}
                    </p>

                    <p>
                        🚨 <b>Accident Type:</b>
                        {report_item['accident_type']}
                    </p>

                    <p>
                        📝 <b>Description:</b>
                        {report_item['description']}
                    </p>

                    <p>
                        📅 <b>Date:</b>
                        {report_item['report_date'] or 'Not Available'}
                    </p>

                    <p>
                        ⏰ <b>Time:</b>
                        {report_item['report_time'] or 'Not Available'}
                    </p>

                </div>

                <div class="location">

                    <h3>📍 Accident Location</h3>

                    <p>
                        <b>Latitude:</b>
                        {latitude or 'Not Available'}
                    </p>

                    <p>
                        <b>Longitude:</b>
                        {longitude or 'Not Available'}
                    </p>

                    <p>
                        <b>Location:</b>
                        {report_item['location']}
                    </p>
            """

            if latitude and longitude:

                html += f"""

                    <a
                        href="{map_url}"
                        target="_blank"
                        class="map-btn"
                    >
                        🗺️ View Location on Google Maps
                    </a>
                """

            html += f"""

                </div>

                <hr>

                <form
                    method="POST"
                    action="/update-status/{report_item['id']}"
                >

                    <b>🔄 Update Report Status:</b>

                    <br><br>

                    <select name="status" required>

                        <option
                            value="Pending"
                            {"selected" if current_status == "Pending" else ""}
                        >
                            🟡 Pending
                        </option>

                        <option
                            value="In Progress"
                            {"selected" if current_status == "In Progress" else ""}
                        >
                            🔵 In Progress
                        </option>

                        <option
                            value="Resolved"
                            {"selected" if current_status == "Resolved" else ""}
                        >
                            🟢 Resolved
                        </option>

                    </select>

                    &nbsp;

                    <button type="submit">
                        Update Status
                    </button>

                </form>

            </div>
            """

    html += """

        </div>

        <a href="/police" class="bottom-btn">
            👮 Police Dashboard
        </a>

        <a href="/dashboard" class="bottom-btn">
            🏠 Dashboard
        </a>

        <script>

        function filterReports() {

            const search = document
                .getElementById("searchInput")
                .value
                .toLowerCase();

            const status = document
                .getElementById("statusFilter")
                .value;

            const reports =
                document.querySelectorAll(".report");

            reports.forEach(function(report) {

                const text =
                    report.innerText.toLowerCase();

                const reportStatus =
                    report.querySelector(".status").innerText;

                const matchesSearch =
                    text.includes(search);

                const matchesStatus =
                    status === "All" ||
                    reportStatus.includes(status);

                if (matchesSearch && matchesStatus) {
                    report.style.display = "block";
                } else {
                    report.style.display = "none";
                }

            });

        }

        </script>

    </body>

    </html>
    """

    return html

# ==================================================
# START SERVER
# ==================================================

if __name__ == "__main__":

    print("====================================")
    print("🚑 RAKSHAK SERVER STARTED")
    print("====================================")

    import os
    port = int(os.environ.get("PORT", 5000))

    print(f"🌐 Running on port {port}")
    print("====================================")

    app.run(host="0.0.0.0", port=port)