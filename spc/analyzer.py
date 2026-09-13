"""
spc.analyzer
~~~~~~~~~~~~
İstatistiksel proses kontrolü ve makine yeterlilik hesaplama motoru.
"""

from typing import Iterable, Union
import numpy as np

from spc.models import CapabilityStatus, ProcessCapabilityResult


class CapabilityAnalyzer:
    """
    Talaşlı imalat ve seri üretim parçalarının ölçüm verilerini
    kullanarak proses yeterlilik indekslerini (Cp, Cpk) hesaplar.
    """

    def __init__(self, nominal: float, usl: float, lsl: float) -> None:
        """
        Parametreler:
            nominal (float): Parçanın teknik resim anma ölçüsü (örn: 25.00 mm).
            usl (float): Üst spesifikasyon/tolerans limiti (Upper Spec Limit).
            lsl (float): Alt spesifikasyon/tolerans limiti (Lower Spec Limit).
        """
        if usl <= lsl:
            raise ValueError(f"USL ({usl}) değeri LSL ({lsl}) değerinden büyük olmalıdır.")
        if not (lsl <= nominal <= usl):
            raise ValueError("Nominal ölçü USL ve LSL sınırları arasında yer almalıdır.")

        self.nominal = float(nominal)
        self.usl = float(usl)
        self.lsl = float(lsl)
        self.tolerance_span = self.usl - self.lsl

    def analyze(self, data: Iterable[Union[int, float]]) -> ProcessCapabilityResult:
        """
        Ölçüm veri kümesini analiz eder ve sonuçları döndürür.

        Parametreler:
            data (Iterable[float]): CNC tezgâhından çıkan ölçüm değerleri.

        Döndürür:
            ProcessCapabilityResult: Hesaplanan tüm istatistikler ve indeksler.
        """
        arr = np.asarray(data, dtype=np.float64)

        if arr.ndim != 1 or arr.size < 2:
            raise ValueError("Analiz için en az 2 adet geçerli 1 boyutlu ölçüm verisi gereklidir.")

        sample_size = int(arr.size)
        mean = float(np.mean(arr))
        
        # Numune standart sapması (Bessel düzeltmesi ile: ddof=1)
        std_dev = float(np.std(arr, ddof=1))
        variance = float(np.var(arr, ddof=1))

        if std_dev == 0.0:
            raise ValueError("Standart sapma sıfır: Verilerde hiçbir değişkenlik bulunmuyor.")

        # Potansiyel proses yeterliliği (Cp)
        cp = self.tolerance_span / (6.0 * std_dev)

        # Üst ve alt tek taraflı yeterlilik indeksleri
        cpu = (self.usl - mean) / (3.0 * std_dev)
        cpl = (mean - self.lsl) / (3.0 * std_dev)

        # Fiili proses yeterliliği (Cpk)
        cpk = min(cpu, cpl)

        # Ortalama sapması ve proses merkezleme kaybı katsayısı (k)
        mean_deviation = mean - self.nominal
        tolerance_midpoint = (self.usl + self.lsl) / 2.0
        centering_ratio_k = abs(mean - tolerance_midpoint) / (self.tolerance_span / 2.0)

        # Yeterlilik durumu değerlendirmesi
        if cpk >= 1.67:
            status = CapabilityStatus.EXCELLENT
        elif cpk >= 1.33:
            status = CapabilityStatus.CAPABLE
        elif cpk >= 1.00:
            status = CapabilityStatus.MARGINAL
        else:
            status = CapabilityStatus.INCAPABLE

        return ProcessCapabilityResult(
            sample_size=sample_size,
            mean=mean,
            std_dev=std_dev,
            variance=variance,
            nominal=self.nominal,
            usl=self.usl,
            lsl=self.lsl,
            mean_deviation=mean_deviation,
            tolerance_span=self.tolerance_span,
            cp=cp,
            cpu=cpu,
            cpl=cpl,
            cpk=cpk,
            centering_ratio_k=centering_ratio_k,
            status=status,
        )
