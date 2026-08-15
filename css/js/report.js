const form = document.querySelector("form");

form.addEventListener("submit", function (e) {
    e.preventDefault();

    alert("🚨 Accident Report Submitted Successfully!\n\nNearby Hospital, Police and Emergency Services have been notified.\nHelp is on the way.");


    // window.location.href = "emergency.html";
});