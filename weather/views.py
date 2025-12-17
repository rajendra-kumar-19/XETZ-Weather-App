from django.shortcuts import render
import requests
import datetime
from django.http import JsonResponse

API_KEY = "bb1761414ce49287cd8dccb67adfc3bd"

# ---------------- CITY AUTOCOMPLETE ----------------
def city_suggest(request):
    q = request.GET.get('q')
    if not q:
        return JsonResponse([], safe=False)

    url = f"http://api.openweathermap.org/geo/1.0/direct?q={q}&limit=5&appid={API_KEY}"
    data = requests.get(url).json()

    cities = []
    for c in data:
        cities.append({
            'name': f"{c['name']}, {c.get('state','')}, {c['country']}",
            'lat': c['lat'],
            'lon': c['lon']
        })

    return JsonResponse(cities, safe=False)


# ---------------- US AQI CALCULATION (PM2.5) ----------------
def calculate_us_aqi_pm25(pm25):
    # US EPA breakpoints
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.4, 301, 500),
    ]

    for c_low, c_high, aqi_low, aqi_high in breakpoints:
        if c_low <= pm25 <= c_high:
            return round(
                ((aqi_high - aqi_low) / (c_high - c_low)) *
                (pm25 - c_low) + aqi_low
            )

    return 500


# ---------------- MAIN WEATHER ----------------
def home(request):

    if request.method == 'POST' and request.POST.get('lat'):
        lat = request.POST.get('lat')
        lon = request.POST.get('lon')
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
        data = requests.get(weather_url).json()

    elif request.method == 'POST':
        city = request.POST.get('city')
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
        data = requests.get(weather_url).json()

        if data.get('cod') != 200:
            return render(request, 'weather/index.html', {'error': 'City not found'})
    else:
        return render(request, 'weather/index.html')

    # BASIC WEATHER
    condition = data['weather'][0]['main']
    temp = data['main']['temp']
    humidity = data['main']['humidity']
    wind = data['wind']['speed']
    lat = data['coord']['lat']
    lon = data['coord']['lon']

    # LOCAL TIME
    timezone_offset = data['timezone']
    local_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=timezone_offset)

    # BACKGROUND
    bg = "sunny"
    if condition == "Clouds":
        bg = "cloudy"
    elif condition == "Rain":
        bg = "rainy"
    elif condition == "Snow":
        bg = "snowy"
    elif condition == "Thunderstorm":
        bg = "thunder"

    # ---------------- AQI ----------------
    aqi_url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    aqi_data = requests.get(aqi_url).json()

    aqi_index = aqi_data['list'][0]['main']['aqi']
    pm25 = aqi_data['list'][0]['components']['pm2_5']

    us_aqi = calculate_us_aqi_pm25(pm25)

    aqi_map = {
        1: ("Good", "#22c55e"),
        2: ("Fair", "#eab308"),
        3: ("Moderate", "#f97316"),
        4: ("Poor", "#ef4444"),
        5: ("Very Poor", "#7c3aed")
    }

    aqi_text, aqi_color = aqi_map[aqi_index]

    return render(request, 'weather/weather.html', {
        'city': data['name'],
        'temp': round(temp, 1),
        'feels': round(data['main']['feels_like'], 1),
        'humidity': humidity,
        'wind': wind,
        'bg': bg,
        'local_time': local_time.strftime("%I:%M %p"),
        'aqi_index': aqi_index,
        'aqi_text': aqi_text,
        'aqi_color': aqi_color,
        'us_aqi': us_aqi,
        'lat': lat,
        'lon': lon,
        'icon': "🌤️"
    })
