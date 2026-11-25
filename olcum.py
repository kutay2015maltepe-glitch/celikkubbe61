import csv
from pathlib import Path

csv_yolu = Path(__file__).parent / "data" / "etiketler.csv"
modlar = ["rgb_filtresiz", "rgb_filtreli", "hsv_filtresiz", "hsv_filtreli"]

with open(csv_yolu, mode="r", encoding="utf-8") as f:
    satirlar = list(csv.DictReader(f))

print(f"Toplam kayit: {len(satirlar)}\n")

for mod in modlar:
    dogru = 0
    for s in satirlar:
        gercek = s["gercek_sinif"].strip().lower()
        tahmin = s[mod].strip().lower()
        if tahmin == gercek:
            dogru += 1
    oran = (dogru / len(satirlar)) * 100 if satirlar else 0
    print(f"{mod:15} -> Dogru: {dogru}/{len(satirlar)} (%{oran:.1f})")
