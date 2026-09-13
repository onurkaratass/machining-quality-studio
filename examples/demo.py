"""
examples.demo
~~~~~~~~~~~~~
CNC şaft tornalama verisi üzerinde uçtan uca SPC analizi ve raporlama demosu.
"""

import os
import pandas as pd
from spc import CapabilityAnalyzer, ProcessReporter, ProcessVisualizer


def run_spc_demo():
    # 1. Örnek ölçüm verisini yükle
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, "sample_measurements.csv")
    df = pd.read_csv(csv_path)

    # 2. Teknik resim spesifikasyonları (Ø25 ±0.05 mm)
    nominal = 25.00
    usl = 25.05
    lsl = 24.95

    # 3. İstatistiksel Proses Kontrol Analizini Çalıştır
    analyzer = CapabilityAnalyzer(nominal=nominal, usl=usl, lsl=lsl)
    result = analyzer.analyze(df["Diameter_mm"])

    # 4. Terminal Raporunu Yazdır
    ProcessReporter.print_report(result, part_name="CNC Torna Hassas Şaft Çapı (T0101)")

    # 5. Görselleştirme Grafiğini Oluştur ve Kaydet
    output_image = os.path.join(base_dir, "spc_capability_distribution.png")
    visualizer = ProcessVisualizer()
    visualizer.plot_capability(
        data=df["Diameter_mm"],
        result=result,
        title="CNC Torna Şaft Çapı Proses Yeterlilik Analizi (Ø25 ±0.05 mm)",
        save_path=output_image,
        show=False,
    )
    print(f"\n[+] Dağılım ve tolerans grafiği kaydedildi: {output_image}\n")


if __name__ == "__main__":
    run_spc_demo()
