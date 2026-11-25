import csv
import time
from pathlib import Path
import cv2

MODES = ["rgb_filtresiz", "rgb_filtreli", "hsv_filtresiz", "hsv_filtreli"]
HEDEFLER = {"kirmizi", "mavi"}


def etiket_dosyasini_bul() -> Path | None:
    betik_klasoru = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()

    dogrudan_adaylar = [
        Path(r"C:\Users\USER\Desktop\Çelik Kubbe\Çelik Kubbe 61\data\etiketler.txt"),
        Path(r"C:\Users\USER\Desktop\Çelik Kubbe\Çelik Kubbe 61\data\etiketler.csv"),
        Path(r"C:\Users\USER\Desktop\Çelik Kubbe\Çelik Kubbe 61\data\etiketler.csv.txt"),
        betik_klasoru / "data" / "etiketler.txt",
        betik_klasoru / "etiketler.txt",
        betik_klasoru.parent / "data" / "etiketler.txt",
        Path.cwd() / "data" / "etiketler.txt",
        Path.cwd() / "etiketler.txt",
    ]

    for aday in dogrudan_adaylar:
        if aday.exists() and aday.is_file():
            return aday

    tarama_kokleri = [
        betik_klasoru,
        betik_klasoru.parent,
        Path.cwd(),
        Path(r"C:\Users\USER\Desktop"),
        Path(r"C:\Users\USER\OneDrive\Masaüstü"),
        Path(r"C:\Users\USER\OneDrive\Desktop"),
        Path(r"C:\Users\USER"),
    ]

    gorulen: set[Path] = set()
    for kok in tarama_kokleri:
        if not kok.exists() or kok in gorulen:
            continue
        gorulen.add(kok)
        try:
            for p in kok.rglob("*etiketler*"):
                if not p.is_file() or p.suffix.lower() == ".lnk":
                    continue
                parcalar = [x.lower().replace(" ", "") for x in p.parts]
                if "çelikkubbe" in parcalar and "çelikkubbe61" in parcalar:
                    return p
        except PermissionError:
            continue

    for kok in tarama_kokleri:
        if not kok.exists():
            continue
        try:
            for p in kok.rglob("*etiketler*"):
                if p.is_file() and p.suffix.lower() != ".lnk":
                    return p
        except PermissionError:
            continue

    return None


def satir_sozluklerini_oku(csv_path: Path) -> list[dict[str, str]]:
    with open(csv_path, mode="r", encoding="utf-8-sig", newline="") as f:
        ham_satirlar = [satir.strip() for satir in f if satir.strip()]

    if not ham_satirlar:
        return []

    ayrac = ";" if ham_satirlar[0].count(";") > ham_satirlar[0].count(",") else ","
    reader = csv.DictReader(ham_satirlar, delimiter=ayrac)
    satirlar: list[dict[str, str]] = []
    for row in reader:
        temiz_row = {
            (k or "").strip(): (v or "").strip()
            for k, v in row.items()
            if k is not None
        }
        if temiz_row:
            satirlar.append(temiz_row)
    return satirlar


def gorsel_yolunu_bul(data_dir: Path, dosya_adi: str) -> Path | None:
    temiz = dosya_adi.strip()
    if not temiz:
        return None

    ham = Path(temiz)
    adaylar = [
        data_dir / ham,
        data_dir.parent / ham,
        data_dir / ham.name,
    ]
    for yol in adaylar:
        if yol.exists() and yol.is_file():
            return yol

    hedef_ad = ham.name.lower()
    hedef_govde = ham.stem.lower()
    try:
        for p in data_dir.rglob("*"):
            if not p.is_file():
                continue
            if p.name.lower() == hedef_ad or p.stem.lower() == hedef_govde:
                return p
    except PermissionError:
        pass

    return None


def data_kare_sure_fps(satirlar: list[dict[str, str]], data_dir: Path) -> tuple[float | None, float | None, float, int]:
    """Kare başına okuma süresi (ms), FPS, toplam ölçüm süresi (ms) ve ölçülen kare sayısını döndürür."""
    t_basla = time.perf_counter()
    sureler_ms: list[float] = []

    for r in satirlar:
        yol = gorsel_yolunu_bul(data_dir, r.get("dosya", ""))
        if yol is None:
            continue
        t0 = time.perf_counter()
        kare = cv2.imread(str(yol))
        t1 = time.perf_counter()
        if kare is not None:
            sureler_ms.append((t1 - t0) * 1000.0)

    toplam_olcum_ms = (time.perf_counter() - t_basla) * 1000.0
    if not sureler_ms:
        return None, None, toplam_olcum_ms, 0

    ort_ms = sum(sureler_ms) / len(sureler_ms)
    fps = (1000.0 / ort_ms) if ort_ms > 0 else None
    return ort_ms, fps, toplam_olcum_ms, len(sureler_ms)


def ekran_kare_sure_fps(tekrar: int = 10) -> tuple[float | None, float | None, float]:
    """Ekran kare alma süresi (ms), FPS ve toplam ölçüm süresini (ms) döndürür."""
    t_basla = time.perf_counter()
    sureler_ms: list[float] = []

    try:
        import mss

        with mss.mss() as sct:
            mon = sct.monitors[1]
            for _ in range(tekrar):
                t0 = time.perf_counter()
                _ = sct.grab(mon)
                t1 = time.perf_counter()
                sureler_ms.append((t1 - t0) * 1000.0)
    except Exception:
        try:
            from PIL import ImageGrab

            for _ in range(tekrar):
                t0 = time.perf_counter()
                _ = ImageGrab.grab()
                t1 = time.perf_counter()
                sureler_ms.append((t1 - t0) * 1000.0)
        except Exception:
            toplam_olcum_ms = (time.perf_counter() - t_basla) * 1000.0
            return None, None, toplam_olcum_ms

    toplam_olcum_ms = (time.perf_counter() - t_basla) * 1000.0
    if not sureler_ms:
        return None, None, toplam_olcum_ms

    ort_ms = sum(sureler_ms) / len(sureler_ms)
    fps = (1000.0 / ort_ms) if ort_ms > 0 else None
    return ort_ms, fps, toplam_olcum_ms


def hedef_metrik_hesapla(satirlar: list[dict[str, str]], mod: str) -> dict[str, str]:
    if not satirlar or mod not in satirlar[0]:
        return {"tp": "___", "fp": "___", "fn": "___", "tn": "___", "acc": "___"}

    tp = fp = fn = tn = 0
    for r in satirlar:
        g = r.get("gercek_sinif", "").strip().lower()
        p = r.get(mod, "").strip().lower()

        if g in HEDEFLER:
            if p == g:
                tp += 1
            else:
                fn += 1
        else:
            if p in HEDEFLER:
                fp += 1
            else:
                tn += 1

    toplam = len(satirlar)
    acc = f"%{(tp + tn) / toplam * 100.0:.1f}" if toplam > 0 else "___"
    return {"tp": str(tp), "fp": str(fp), "fn": str(fn), "tn": str(tn), "acc": acc}


def main() -> None:
    t_genel_basla = time.perf_counter()
    print("olcum.py calistirildi.", flush=True)
    csv_path = etiket_dosyasini_bul()
    if csv_path is None:
        print("HATA: etiketler dosyasi bulunamadi.", flush=True)
        return

    satirlar = satir_sozluklerini_oku(csv_path)
    if not satirlar:
        print(f"HATA: {csv_path} icinde okunabilir satir yok.", flush=True)
        return

    toplam = len(satirlar)
    data_ms, data_fps, data_olcum_ms, olculen = data_kare_sure_fps(satirlar, csv_path.parent)
    ekran_ms, ekran_fps, ekran_olcum_ms = ekran_kare_sure_fps(10)

    data_ms_str = f"{data_ms:.2f} ms" if data_ms is not None else "___ ms"
    data_fps_str = f"{data_fps:.2f} FPS" if data_fps is not None else "___ FPS"
    ekran_ms_str = f"{ekran_ms:.2f} ms" if ekran_ms is not None else "___ ms"
    ekran_fps_str = f"{ekran_fps:.2f} FPS" if ekran_fps is not None else "___ FPS"

    print(f"Dosya          : {csv_path}", flush=True)
    print(f"Toplam test    : {toplam} | Olculen data karesi: {olculen}", flush=True)
    print(f"Data kare alma : {data_ms_str}/kare ({data_fps_str}) | Olcum suresi: {data_olcum_ms:.2f} ms", flush=True)
    print(f"Ekran kare alma: {ekran_ms_str}/kare ({ekran_fps_str}) | Olcum suresi: {ekran_olcum_ms:.2f} ms\n", flush=True)

    print("=== DOGRULUK TABLOSU ===", flush=True)
    print("| Mod | TP/FP/FN/TN | Dogruluk & Sure |", flush=True)
    print("| :--- | :--- | :--- |", flush=True)
    for mod in MODES:
        m = hedef_metrik_hesapla(satirlar, mod)
        sure_ozet = f"{data_ms_str} / {data_fps_str}" if data_ms is not None else f"{data_olcum_ms:.2f} ms"
        print(f"| `{mod}` | {m['tp']}/{m['fp']}/{m['fn']}/{m['tn']} | {m['acc']} ({sure_ozet}) |", flush=True)

    genel_sure_ms = (time.perf_counter() - t_genel_basla) * 1000.0
    print(f"\nToplam olcum suresi: {genel_sure_ms:.2f} ms", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"BEKLENMEYEN HATA: {type(exc).__name__}: {exc}", flush=True)