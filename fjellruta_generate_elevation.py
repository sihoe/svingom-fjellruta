import gpxpy
import time
import requests
import json

# ---- FILNAVN PÅ GPX-FILEN ----
gpx_file = "Fjellruta_over_Vegglifjell_og_Imingfjell.gpx"

# ---- HVOR OFTE SKAL VI SAMLE PUNKTER ----
sampling_interval = 10  # Hver 10. punkt for å begrense antall forespørsler

# ---- STEG 1: Les GPX og trekk ut punkter ----
with open(gpx_file, "r", encoding="utf-8") as f:
    gpx = gpxpy.parse(f)

all_points = []
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            all_points.append((point.latitude, point.longitude))

# ---- STEG 2: Filtrer punkter for å redusere antall forespørsler ----
filtered_points = all_points[::sampling_interval]

print(f"Totalt punkter etter filtrering: {len(filtered_points)}")

# ---- STEG 3: Hent høyde fra OpenTopodata ----
elevation_data = []
for i, (lat, lon) in enumerate(filtered_points):
    try:
        url = f"https://api.opentopodata.org/v1/srtm90m?locations={lat},{lon}"
        response = requests.get(url)
        data = response.json()
        elevation = data["results"][0]["elevation"]
        elevation_data.append({
            "distance": round(i * 0.1, 3),  # Grovt estimat (0.1 km per punkt)
            "elevation": elevation
        })
        print(f"{i+1}/{len(filtered_points)}: {lat}, {lon} = {elevation} m")
        time.sleep(1.2)  # Vent for å unngå rate limit
    except Exception as e:
        print(f"Feil ved punkt {i+1}: {e}")
        elevation_data.append({
            "distance": round(i * 0.1, 3),
            "elevation": None
        })

# ---- STEG 4: Lagre som JSON ----
with open("fjellruta_elevation.json", "w", encoding="utf-8") as f:
    json.dump(elevation_data, f, indent=2)

print("✅ Lagret fil: fjellruta_elevation.json")
