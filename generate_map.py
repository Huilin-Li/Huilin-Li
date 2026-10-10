import json

WIDTH = 1200

MAP_TOP = 70
MAP_BOTTOM = 600

TITLE = "Say hello to 🌏"

# =========================
# 1. Read cities
# =========================

with open("cities.csv", "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

headers = lines[0].split(",")

cities = []

for line in lines[1:]:

    values = line.split(",")

    city = {}

    for i, header in enumerate(headers):
        city[header] = values[i]

    cities.append(city)


city_count = len(cities)

country_count = len(
    set(city["country"] for city in cities)
)


country_city_counts = {}

for city in cities:
    country = city["country"]
    country_city_counts[country] = (
        country_city_counts.get(country, 0) + 1
    )

country_items = sorted(
    country_city_counts.items(),
    key=lambda item: item[1],
    reverse=True
)


def country_to_flag(country):
    country_codes = {
        "China": "CN",
        "Denmark": "DK",
        "United Kingdom": "GB",
        "United States": "US",
        "Japan": "JP",
        "Germany": "DE",
        "France": "FR",
        "Canada": "CA",
        "China": "CN",
        "Australia": "AU",
        "Sweden": "SE",
        "Italy": "IT",
        "Portugal": "PT",
        "Netherlands": "NL",
        "Belgium": "BE",
        "Monaco": "MC",
    }

    code = country_codes.get(country)

    if not code:
        return "🌍"

    return "".join(
        chr(ord(char) + 127397)
        for char in code
    )

COLS = 3
ROW_HEIGHT = 24

START_Y = 645

country_rows = (len(country_items) + COLS - 1) // COLS

HEIGHT = START_Y + country_rows * ROW_HEIGHT + 40

# =========================
# 2. Read world map
# =========================

with open("world.geojson", "r", encoding="utf-8") as f:
    world = json.load(f)


# =========================
# 3. Map projection
# =========================

def project(lng, lat):
    x = (lng + 180) / 360 * WIDTH
    y = MAP_TOP + (90 - lat) / 180 * (MAP_BOTTOM - MAP_TOP)

    return x, y


# =========================
# 4. Polygon → SVG path
# =========================

def polygon_to_path(polygon):
    path = []

    for ring in polygon:

        if not ring:
            continue

        lng, lat = ring[0]
        x, y = project(lng, lat)

        path.append(f"M {x:.2f} {y:.2f}")

        for lng, lat in ring[1:]:

            x, y = project(lng, lat)

            path.append(
                f"L {x:.2f} {y:.2f}"
            )

        path.append("Z")

    return " ".join(path)


# =========================
# 5. Polygon / MultiPolygon
# =========================

def geometry_to_paths(geometry):

    geometry_type = geometry["type"]
    coordinates = geometry["coordinates"]

    if geometry_type == "Polygon":

        return [
            polygon_to_path(coordinates)
        ]

    if geometry_type == "MultiPolygon":

        return [
            polygon_to_path(polygon)
            for polygon in coordinates
        ]

    return []


# =========================
# 6. Generate countries
# =========================

land = []

for feature in world["features"]:

    geometry = feature["geometry"]

    paths = geometry_to_paths(geometry)

    for d in paths:

        land.append(
            f'''
            <path
                d="{d}"
                fill="#161b22"
                stroke="#30363d"
                stroke-width="0.6"
                fill-rule="evenodd"
            />
            '''
        )


# =========================
# 7. Generate city markers
# =========================

markers = []


for city in cities:
    x, y = project(
        float(city["lng"]),
        float(city["lat"])
    )

    city_name = city["city"]

    marker = f'''
        <!-- {city_name} -->

        <circle
            cx="{x:.2f}"
            cy="{y:.2f}"
            r="4"
            fill="#58a6ff"
            opacity="0.15"
        />

        <circle
            cx="{x:.2f}"
            cy="{y:.2f}"
            r="1.5"
            fill="#58a6ff"
        />
    '''
    markers.append(marker)


# =========================
# 8. Generate country list
# =========================

country_list = []

COL_WIDTH = 180

START_X = 60

for i, (country, count) in enumerate(country_items):

    col = i % COLS
    row = i // COLS

    x = START_X + col * COL_WIDTH
    y = START_Y + row * ROW_HEIGHT

    flag = country_to_flag(country)

    label = "hello" if count == 1 else "hellos"

    country_list.append(
        f'''
        <text
            x="{x}"
            y="{y}"
            fill="#c9d1d9"
            font-family="Arial, sans-serif"
            font-size="12"
        >{flag}</text>

        <text
            x="{x + 90}"
            y="{y}"
            text-anchor="end"
            fill="#8b949e"
            font-family="Arial, sans-serif"
            font-size="12"
        >{count} {label}</text>
        '''
    )
# =========================
# 9. Build SVG
# =========================

svg = f'''
<svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 {WIDTH} {HEIGHT}"
>

    <!-- Background -->

    <rect
        width="100%"
        height="100%"
        fill="#0d1117"
    />


    <!-- Header -->

    <text
        x="30"
        y="40"
        fill="#c9d1d9"
        font-family="Arial, sans-serif"
        font-size="24"
        font-weight="600"
    >{TITLE}</text>


    <!-- Cities -->

    <text
        x="950"
        y="36"
        text-anchor="end"
        fill="#8b949e"
        font-family="Arial, sans-serif"
        font-size="11"
    >Hellos</text>

    <text
        x="975"
        y="40"
        fill="#c9d1d9"
        font-family="Arial, sans-serif"
        font-size="16"
        font-weight="600"
    >{city_count}</text>


    <!-- Divider -->

    <line
        x1="1010"
        y1="20"
        x2="1010"
        y2="50"
        stroke="#30363d"
        stroke-width="1"
    />


    <!-- Countries -->

    <text
        x="1040"
        y="36"
        fill="#8b949e"
        font-family="Arial, sans-serif"
        font-size="11"
    >Countries</text>

    <text
        x="1150"
        y="40"
        text-anchor="end"
        fill="#c9d1d9"
        font-family="Arial, sans-serif"
        font-size="16"
        font-weight="600"
    >{country_count}</text>


    <!-- World -->

    {''.join(land)}


    <!-- Cities markers -->

    {''.join(markers)}


    <!-- Country statistics -->

    <line
        x1="60"
        y1="610"
        x2="1140"
        y2="610"
        stroke="#30363d"
        stroke-width="1"
    />

    {''.join(country_list)}

</svg>
'''


# =========================
# 9. Write SVG
# =========================

with open("world-map.svg", "w", encoding="utf-8") as f:

    f.write(svg)

