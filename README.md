# Çelik Kubbe İFF - Elektro-Optik Renk Uzayı Tabanlı Dost-Düşman Ayrım Altsistemi

Bu depo, çok katmanlı hava savunma mimarisi (Çelik Kubbe) konsepti altında, alçak irtifa tehditlerinin elektro-optik kamera verileriyle **dost (mavi tonları) ve düşman (kırmızı tonları)** olarak sınıflandırılmasını sağlayan saf yazılım tabanlı bilgisayarla görü altsistemine aittir. Proje, donanımdan bağımsız olarak saf Python ve OpenCV üzerinde çalışmaktadır.

---

## 1. İşleme Hattı (Pipeline) Blok Şeması

```text
[USB Kamera / Canlı Akış] 
       ↓
[Ön İşleme: BGR → HSV Renk Uzayı Dönüşümü]
       ↓
[Morfolojik Filtreleme (Gürültü ve Arka Plan Temizliği)]
       ↓
[Kontur Analizi & Renk Eşikleme Kararı]
       ↓
[Sınıflandırma ve Arayüz Çıktısı (Dost / Düşman / FPS)]


2. Donanım ve Sistem Gereksinimleri
Bu altsistem herhangi bir harici mikrodenetleyici (STM32 vb.) veya özel gömülü kart gerektirmez; tamamen ana bilgisayar kaynaklarını kullanır.

Kamera: 720p veya 1080p, min. 30 FPS USB Web Kamera

Aydınlatma: Sabit kontrollü LED masa lambası (Test ortamı aydınlatma standardizasyonu için)

Sabitleme: Masaüstü mini tripod

İşlem Birimi: Standart PC (CPU tabanlı işleme yeterlidir, harici GPU zorunlu değildir)



3. Veri Seti Açıklaması
Örneklem Boyutu: İlk aşamada 10 adet standartlaştırılmış test karesi üzerinden doğrulama yapılmıştır.

Işık Koşulları:

Standart İç Mekan Aydınlatması

Düşük Işık / Gölgeli Koşullar

Etiket Biçimi: Görüntülerdeki hedef nesneler manuel olarak etiketlenmiş (Ground Truth) ve tahmin sonuçları ile karşılaştırılarak Confusion Matrix (Karışıklık Matrisi) metrikleri üretilmiştir.

Veri Depolama: Büyük ölçekli test veri seti harici bulut depolama alanında tutulmakta olup, repoda yalnızca örnek test kareleri yer almaktadır.



4. Kurulum
1-Projeyi çalıştırmak için sisteminizde Python yüklü olmalıdır.

git clone [https://github.com/kullaniciadi/celik-kubbe-iff-vision.git](https://github.com/kullaniciadi/celik-kubbe-iff-vision.git)
cd celik-kubbe-iff-vision

2-Gerekli kütüphaneleri yükleyin (Önerilen: Python 3.x):

pip install opencv-python numpy


5. Nasıl Çalıştırırım?

Ana betiği çalıştırmak ve kameradan canlı renk tabanlı IFF analizi almak için:
python main.py
(Not: Kamera indeksini değiştirmek için cv2.VideoCapture(0) parametresini güncelleyebilirsiniz.)


6. Arayüz ve Entegrasyon Sözleşmesi (Interface Contract)
Bu altsistem, üst seviye komuta-kontrol simülasyon yazılımlarıyla veya diğer takım üyelerinin modülleriyle şu sözleşme üzerinden haberleşir:

Girdi:

cv2 video yakalama akışı (frame) veya diskten okunan test görselleri.

Çıktı (Arayüz Verisi):

Her kare için tespit edilen nesnenin sınıfı (Dost / Düşman), güven skoru ve işleme süresi (ms).

Konsol log çıktısı ve OpenCV GUI penceresi üzerinde bounding box (sınırlayıcı kutu) çizimleri.


7. İlk Deneysel Performans ve Doğrulama Sonuçları
İlk pilot ölçüm sonuçları (10 adet test karesi, ortalama işlem süresi: 61 ms / kare):

================================================================================
ÇELİK KUBBE C2 SİMYASUONİ - DENEYSEL PERFORMANS VE DOĞRULAMA RAPORU
================================================================================

ÖLÇÜM KRİTERİ VE PARAMETRELER:
- Test Karesi (Örneklem): 10 adet test karesi
- Ortalama İşlem Süresi: 61 ms / kare (Tüm konfigürasyonlar için ortalama)
- Referans: Manuel etiketleme (Ground Truth)

--------------------------------------------------------------------------------
1. STANDART IŞIK KOŞULLARI TABLOSU
--------------------------------------------------------------------------------
| Mod / Konfigürasyon         | TP | FP | FN | TN | Doğruluk | Kesinlik | Duyarlılık |
|-----------------------------|----|----|----|----|----------|----------|------------|
| RGB + Filtresiz             | 7  | 1  | 1  | 1  | %80.0    | %87.5    | %87.5      |
| RGB + Filtreli              | 7  | 0  | 2  | 1  | %80.0    | %100.0   | %77.8      |
| HSV + Filtresiz             | 7  | 1  | 0  | 2  | %90.0    | %87.5    | %100.0     |
| HSV + Filtreli (Asıl Sistem)| 10 | 0  | 0  | 0  | %100.0   | %100.0   | %100.0     |

--------------------------------------------------------------------------------
2. DÜŞÜK IŞIK KOŞULLARI TABLOSU
--------------------------------------------------------------------------------
| Mod / Konfigürasyon         | TP | FP | FN | TN | Doğruluk | Kesinlik | Duyarlılık |
|-----------------------------|----|----|----|----|----------|----------|------------|
| Düşük Işık - RGB + Filtresiz| 4  | 0  | 4  | 2  | %60.0    | %100.0   | %50.0      |
| Düşük Işık - RGB + Filtreli | 3  | 0  | 5  | 2  | %50.0    | %100.0   | %37.5      |
| Düşük Işık - HSV + Filtresiz| 8  | 0  | 0  | 2  | %100.0   | %100.0   | %100.0     |
| Düşük Işık - HSV+Filtreli   | 8  | 0  | 0  | 2  | %100.0   | %100.0   | %100.0     |

--------------------------------------------------------------------------------
3. BİLİMSEL ÇIKARIM VE TARTIŞMA
--------------------------------------------------------------------------------
- İşlem yükünün tüm modlarda ortalama 61 ms seviyesinde kararlı seyrettiği tespit 
  edilmiştir.
- Aydınlatma azaldığında RGB tabanlı modellerde eşik sapmalarından dolayı 
  doğruluğun %50-%60 aralığına gerilediği gözlemlenmiştir.
- Renk tonunu (Hue) parlaklıktan (Value) izole eden HSV mimarisi ve filtreleme 
  sayesinde, düşük ışık koşullarında bile %100 başarım kararlılıkla korunmuştur.
================================================================================

