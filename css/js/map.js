// ==========================================
// RAKSHAK - AUTOMATIC CURRENT LOCATION
// ==========================================

function getCurrentLocation() {

    if (!navigator.geolocation) {
        alert("❌ Your browser does not support location.");
        return;
    }

    navigator.geolocation.getCurrentPosition(

        function(position) {

            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;

            console.log("Latitude:", latitude);
            console.log("Longitude:", longitude);

            // Location input शोधणे
            const locationInput =
                document.getElementById("location");

            if (locationInput) {

                locationInput.value =
                    latitude + ", " + longitude;

                console.log(
                    "✅ Current location added automatically."
                );
            }

            // Google Maps link तयार करणे
            const mapLink =
                document.getElementById("mapLink");

            if (mapLink) {

                mapLink.href =
                    "https://www.google.com/maps?q=" +
                    latitude +
                    "," +
                    longitude;

                mapLink.style.display = "inline-block";
            }

        },

        function(error) {

            if (error.code === 1) {

                alert(
                    "📍 Location permission denied. Please allow location access."
                );

            } else if (error.code === 2) {

                alert(
                    "❌ Location could not be determined."
                );

            } else if (error.code === 3) {

                alert(
                    "⏳ Location request timed out."
                );

            } else {

                alert(
                    "❌ Unable to get your current location."
                );
            }
        },

        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}


// ==========================================
// PAGE LOAD
// ==========================================

document.addEventListener(
    "DOMContentLoaded",
    function() {

        // Page उघडल्यावर location automatically मागेल
        getCurrentLocation();

    }
);