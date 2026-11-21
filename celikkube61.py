import cv2
import numpy as np
import time

KAMERA_ID = 0
cap = cv2.VideoCapture(KAMERA_ID, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print(f"Hata: {KAMERA_ID} numaralı kamera açılamadı!")
    exit()

fgbg = cv2.createBackgroundSubtractorMOG2(history=400, varThreshold=50, detectShadows=False)

# Başlangıç modu: 4 = HSV + Filtreli (Asıl Sistemimiz)
current_mode = 4

print("=== ÇELİK KUBBE TEST & ÖLÇÜM MODÜLÜ AKTİF ===")
print("Modlar arası geçiş için klavyedeki tuşları kullan:")
print(" [1] -> RGB + Filtresiz")
print(" [2] -> RGB + Filtreli")
print(" [3] -> HSV + Filtresiz")
print(" [4] -> HSV + Filtreli (Asıl Sistem)")
print(" [q] -> Çıkış")

while True:
    baslangic_zamani = time.time()
    
    ret, frame = cap.read()
    if not ret:
        print("Kamera akışı alınamadı.")
        break

    frame = cv2.flip(frame, 1)
    h_frame, w_frame, _ = frame.shape

    # --- 1. RENK UZAYI SEÇİMİ (RGB vs HSV) ---
    if current_mode in [1, 2]:  # RGB UZAYI
        b, g, r = cv2.split(frame)
        # Basit RGB eşikleme
        red_mask = ((r > 120) & (g < 80) & (b < 80)).astype(np.uint8) * 255
        blue_mask = ((b > 120) & (r < 80) & (g < 80)).astype(np.uint8) * 255
    else:  # HSV UZAYI (Mod 3 ve 4)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_red1, upper_red1 = np.array([0, 120, 70]), np.array([10, 255, 255])
        lower_red2, upper_red2 = np.array([170, 120, 70]), np.array([180, 255, 255])
        red_mask = cv2.bitwise_or(cv2.inRange(hsv, lower_red1, upper_red1), cv2.inRange(hsv, lower_red2, upper_red2))
        
        lower_blue, upper_blue = np.array([90, 100, 70]), np.array([130, 255, 255])
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

    color_target_mask = cv2.bitwise_or(red_mask, blue_mask)

    # --- 2. FİLTRELEME SEÇİMİ (Filtresiz vs Filtreli) ---
    if current_mode in [2, 4]:  # FİLTRELİ (MOG2 Arka Plan + Morfolojik Gürültü Temizliği)
        fgmask = fgbg.apply(frame)
        fusion_mask = cv2.bitwise_and(fgmask, color_target_mask)
        kernel = np.ones((5, 5), np.uint8)
        fusion_mask = cv2.morphologyEx(fusion_mask, cv2.MORPH_OPEN, kernel)
        fusion_mask = cv2.morphologyEx(fusion_mask, cv2.MORPH_DILATE, kernel)
    else:  # FİLTRESİZ (Ham maske, parazit temizliği yok)
        fusion_mask = color_target_mask

    # --- 3. KONTUR VE HEDEF ANALİZİ ---
    contours, _ = cv2.findContours(fusion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 1500 < area < 40000:
            x, y, w, h = cv2.boundingRect(cnt)
            
            roi_red = red_mask[y:y+h, x:x+w]
            roi_blue = blue_mask[y:y+h, x:x+w]
            
            if np.sum(roi_red > 0) > np.sum(roi_blue > 0):
                label = "DUSMAN (HOSTILE)"
                color = (0, 0, 255)  # Kırmızı
            else:
                label = "DOST (FRIENDLY)"
                color = (0, 255, 0)  # Yeşil

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, label, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 2)

    # İşlem Süresi (ms) Hesaplama
    bitis_zamani = time.time()
    gecen_sure_ms = (bitis_zamani - baslangic_zamani) * 1000

    # --- 4. HUD ARAYÜZÜ VE BİLGİ PANELİ ---
    mode_names = {
        1: "1: RGB + Filtresiz",
        2: "2: RGB + Filtreli",
        3: "3: HSV + Filtresiz",
        4: "4: HSV + Filtreli (Asil Sistem)"
    }
    
    cv2.rectangle(frame, (15, 15), (420, 75), (0, 0, 0), -1)
    cv2.rectangle(frame, (15, 15), (420, 75), (0, 255, 0), 1)
    cv2.putText(frame, f"TEST MODU: {mode_names[current_mode]}", (22, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 2)
    cv2.putText(frame, f"Kare Islem Suresi: {gecen_sure_ms:.1f} ms", (22, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1)

    cv2.imshow("Celik Kubbe - Test ve Olcum Modulu", frame)

    # Klavye Kontrolleri (1, 2, 3, 4 ve q)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('1'):
        current_mode = 1
        print("Mod Değişti: RGB + Filtresiz")
    elif key == ord('2'):
        current_mode = 2
        print("Mod Değişti: RGB + Filtreli")
    elif key == ord('3'):
        current_mode = 3
        print("Mod Değişti: HSV + Filtresiz")
    elif key == ord('4'):
        current_mode = 4
        print("Mod Değişti: HSV + Filtreli (Asıl Sistem)")

cap.release()
cv2.destroyAllWindows()
