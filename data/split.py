import json
from pathlib import Path


cities_file = Path("./cities500.json")


output_dir = Path("./cities")
output_dir.mkdir(parents=True, exist_ok=True)


with cities_file.open("r", encoding="utf-8") as f:
    cities = json.load(f)


countries = {}
for city in cities:
    iso = city.get("country")
    if not iso:
        continue
    if iso not in countries:
        countries[iso] = []
    countries[iso].append({
        "id": city.get("id"),
        "name": city.get("name"),
        "lat": float(city.get("lat")),
        "lon": float(city.get("lon")),
       # "pop": int(city.get("pop", 0))
    })


for iso, city_list in countries.items():
    out_file = output_dir / f"{iso}.json"
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(city_list, f, ensure_ascii=False, indent=2)

print(f"✅ Finished! {len(countries)} countries saved in {output_dir}")