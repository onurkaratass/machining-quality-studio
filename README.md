# SPC for Manufacturing & Machining (spc-manufacturing)

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style](https://img.shields.io/badge/code%20style-pep8-green.svg)](https://pep8.org/)

Talaşlı imalat, CNC işleme merkezleri ve seri üretim hatlarından çıkan parçaların kalite kontrol verilerini (kumpas, mikrometre, mihengir veya CMM ölçümleri) analiz etmek için geliştirilmiş açık kaynaklı bir **İstatistiksel Proses Kontrol (SPC - Statistical Process Control)** ve **Proses Yeterlilik (, C_{pk}$)** analiz kütüphanesidir.

---

## 📌 Öne Çıkan Özellikler

- **Hassas İstatistiksel Hesaplama:** Örneklem ortalaması ($\bar{X}$), Bessel düzeltmeli numune standart sapması ($, =1$), varyans ve nominal sapma.
- **Proses Yeterlilik İndeksleri:** $, {pu}$, {pl}$, {pk}$ ve merkezleme kaybı katsayısı ($).
- **Tezgâh & Takım Teşhisi:** $ ve {pk}$ ayrışmasını analiz ederek **takım aşınması (wear offset)** veya **sıfırlama (work offset)** hatalarını otomatik tespit eden karar destek sistemi.
- **Tahmini Fire Analizi (PPM):** Gauss dağılımı kuyruk integralinden parça başına beklenen milyonda hata (PPM) hesabı.
- **Yüksek Çözünürlüklü Görselleştirme:** Ölçüm histogramı, teorik Gauss eğrisi, USL/LSL/Nominal çizgileri ve kırmızıyla taranmış tolerans dışı fire alanları.
- **Terminal Raporu:** Atölye ve kalite odalarında hızlı karar almayı sağlayan yapılandırılmış özet tablosu.

---

## 📐 Matematiksel Formülasyon

### 1. Temel Tanımlayıcı İstatistikler
- **Örneklem Ortalaması ($\bar{X}$):**
  794\bar{X} = \frac{1}{n} \sum_{i=1}^{n} X_i794

- **Numune Standart Sapması ($):**
  794s = \sqrt{\frac{1}{n - 1} \sum_{i=1}^{n} (X_i - \bar{X})^2}794

### 2. Yeterlilik İndeksleri
- **Potansiyel Yeterlilik ($):** Sürecin spesifikasyon aralığına sığabilme potansiyelini ifade eder.
  794C_p = \frac{\text{USL} - \text{LSL}}{6s}794

- **Fiili Proses Yeterliliği ({pk}$):** Sürecin ortalamasının tolerans sınırlarına olan mesafesini dikkate alır.
  794C_{pu} = \frac{\text{USL} - \bar{X}}{3s}, \quad C_{pl} = \frac{\bar{X} - \text{LSL}}{3s}794
  794C_{pk} = \min(C_{pu}, C_{pl})794

- **Merkezleme Oranı ($):**
  794k = \frac{|\bar{X} - M|}{(\text{USL} - \text{LSL}) / 2}, \quad M = \frac{\text{USL} + \text{LSL}}{2}794

---

## 🏭 Endüstriyel Değerlendirme Kriterleri

| {pk}$ Değeri | Proses Durumu | İmalat Aksiyonu |
| :--- | :--- | :--- |
| **{pk} \ge 1.67* | Mükemmel / \sigma$ Seviyesi | Seri üretime devam edilebilir, fire riski < 1 PPM. |
| **.33 \le C_{pk} < 1.67* | Yeterli ve Kararlı (\sigma$) | Otomotiv ve talaşlı imalat standartlarına uygun. |
| **.00 \le C_{pk} < 1.33* | Sınırda / Riskli | Sıkı kontrol ve takım parametrelerinin incelenmesi önerilir. |
| **{pk} < 1.00* | Yetersiz / Yüksek Fire | **Operasyon durdurulmalı**, kök neden araştırması yapılmalıdır. |

> **Mühendislik Notu:**  \ge 1.33$ iken {pk} < 1.33$ ise, tezgâh tekrarlanabilirliği yeterlidir ancak parça ortalaması kaymıştır. CNC tezgâhında takım aşınma ofseti (wear offset) düzeltilerek proses tekrar merkeze çekilmelidir.

---

## 🚀 Kurulum

Depoyu yerel ortamınıza klonlayın ve gereksinimleri yükleyin:



---

## 💻 Hızlı Başlangıç



---

## 📁 Proje Ağacı



---

## 🧪 Testlerin Çalıştırılması

Tüm istatistiksel ve mantıksal fonksiyonları test etmek için:



---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında açık kaynak olarak lisanslanmıştır.
