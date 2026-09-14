# ⚙️ Machining & Quality Studio (CNC & SPC Engineering Suite)

[![Python Version](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://microsoft.com)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge)](#)

> **Talaşlı imalat atölyeleri, CNC işleme merkezleri ve kalite kontrol departmanları için geliştirilmiş; ISO 286 Tolerans & Geçme, CNC Kesme & Güç Hesabı, CNC G-Kod Simülasyonu & Strok Denetimi, Yüzey Pürüzlülüğü ($Ra$), Kılavuz & Diş Tablosu, İmalat Maliyeti & Teklif Motoru, İstatistiksel Proses Kontrol ($C_p, C_{pk}$) ve Kurumsal PDF Sertifikaları üreten hepsi-bir-arada masaüstü mühendislik istasyonu.**

---

## 📌 Entegre Modüller

### 1. 📊 İstatistiksel Proses Kontrol (SPC & Kalite)
- $C_p$, $C_{pk}$, Bessel düzeltmeli standart sapma ($s$), varyans, ortalama sapma hesabı.
- Canlı interaktif Gauss çan eğrisi, histogram, tolerans dışı fire alanları.
- Otomatik takım aşınması (*tool wear*) ve tezgâh ofset (*wear offset*) teşhisi.
- 300 DPI PNG ve ISO 9001/AS9100 uyumlu A4 PDF Kalite Sertifikası çıktısı.

### 2. 📐 ISO 286 Tolerans & Geçme Analizörü
- Standart delik ($H6$ ila $H11$) ve mil ($c11$ ila $s6$) toleransları.
- Boşluklu, Sıkı veya Ara geçme tespiti ve mikron seviyesinde sınırlar.
- Tek tıkla hesaplanan toleransları SPC modülüne aktarma entegrasyonu.

### 3. ✨ Yüzey Pürüzlülüğü ($Ra, Rz$) ve Uç Yarıçapı Asistanı
- Kinematik pürüzlülük formülü ile $R_{th}$, $Ra$ ve $Rz$ hesabı.
- ISO yüzey kalite sınıfı derecelendirmesi ($N1$ ila $N12$).
- Hedef $Ra$ için izin verilen maksimum güvenli ilerlemeyi ($f_{max}$) hesaplayıp kesme modülüne aktarma.
- Canlı teorik takım izi profil grafiği.

### 4. ⚙️ CNC Kesme Parametreleri & Güç Hesabı
- CNC Frezeleme (*Milling*) ve Tornalama (*Turning*) modları.
- Kienzle kesme kuvveti modeli ile; devir ($N$ RPM), tabla ilerlemesi ($V_f$), talaş debisi ($\text{MRR}$), net motor gücü ($P_c$ kW) ve mil torku ($M_c$ Nm).
- Tezgâh motor aşırı yüklenme erken uyarısı.

### 5. 🛠️ CNC G-Kod Simülatörü & Strok Denetleyicisi
- Tezgâh fiziksel eksen sınırları (X, Y, Z soft limits) denetimi; eksen aşımında kırmızı alarm.
- Fener mili kapalı kesme, ilerlemesiz kesme ve Z eksi koda hızlı dalış (çarpma riski) teşhisi.
- Canlı 2D takım yolu çizimi (hızlı hareket G00 vs talaşlı kesme G01).
- Net kesme yolu, hızlı hareket yolu, parça işleme süresi (*Cycle Time*) ve takım listesi.
- Düzeltilmiş G-kodu dışa aktarma (.nc).

### 6. 🔩 Standart Diş Açma, Kılavuz & Ön Delik Matkap Tablosu
- Metrik Standart Kaba (M3 - M36), Metrik İnce ve Gaz / Boru Dişi (G / BSP).
- Kesin ön delme matkap çapı ($D_{drill}$), hatve ve diş derinliği.
- CNC Rijit Kılavuz (*Rigid Tapping*) için senkronize ilerleme ($F = N \times P$).

### 7. 💰 İmalat Parça Maliyeti ve Fiyat Teklifi Motoru
- Kütük hammadde ağırlığı ve malzeme maliyeti hesabı.
- G-kod simülatöründen gelen işleme süresi ve tezgâh saatlik ücreti ile işleme bedeli.
- Takım amortismanı, hazırlık işçiliği ve kâr marjı ekleme.
- Tek tıkla kurumsal **"Müşteri Fiyat Teklif Mektubu (PDF Quotation)"** çıktısı.

### 8. 💬 Kullanıcı İstek, Öneri & Hata Bildirimi (Feedback Hub)
- Tek tıkla doğrudan geliştiriciye (`karatasonur172@gmail.com`) yönlenen şablonlu bildirim sistemi.

---

## 💻 Kurulum ve Çalıştırma

```bash
git clone https://github.com/kullanici-adiniz/machining-quality-studio.git
cd machining-quality-studio
pip install -r requirements.txt
python main.py
```

Tek tıkla bağımsız Windows `.exe` üretmek için **`build_exe.bat`** dosyasını çalıştırabilirsiniz.

---

## 📄 Lisans
Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.
