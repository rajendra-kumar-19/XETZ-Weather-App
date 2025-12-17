// AUTO LOCATION
function getLocation() {
    navigator.geolocation.getCurrentPosition(pos => {
        document.getElementById("lat").value = pos.coords.latitude;
        document.getElementById("lon").value = pos.coords.longitude;
        document.forms[0].submit();
    });
}

// UNIT SWITCH
function toggleUnit() {
    let unit = localStorage.getItem("unit") || "metric";
    unit = unit === "metric" ? "imperial" : "metric";
    localStorage.setItem("unit", unit);

    document.getElementById("unit").value = unit;

    alert(unit === "metric" ? "Switched to Celsius (°C)" : "Switched to Fahrenheit (°F)");
}

// FAVORITES
function saveFavorite(city) {
    let favs = JSON.parse(localStorage.getItem("favs") || "[]");
    if (!favs.includes(city)) {
        favs.push(city);
        localStorage.setItem("favs", JSON.stringify(favs));
        alert("Saved ⭐");
    }
}
