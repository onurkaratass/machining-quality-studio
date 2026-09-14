"""
core.spc_engine
~~~~~~~~~~~~~~~
SPC proses yeterlilik hesaplayıcısı, normal dağılım eğrisi ve karar destek motoru.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Tuple, Union
import numpy as np
from scipy import stats


class CapabilityStatus(Enum):
    EXCELLENT = "Mükemmel / Yüksek Kararlılık (Cpk >= 1.67)"
    CAPABLE = "Yeterli ve Kontrol Altında (1.33 <= Cpk < 1.67)"
    MARGINAL = "Sınırda / Dikkat Gerektirir (1.00 <= Cpk < 1.33)"
    INCAPABLE = "Yetersiz / Yüksek Fire Riski (Cpk < 1.00)"


@dataclass(frozen=True)
class SPCResult:
    sample_size: int
    mean: float
    std_dev: float
    variance: float
    nominal: float
    usl: float
    lsl: float
    mean_deviation: float       # X_bar - Nominal
    tolerance_span: float       # USL - LSL
    cp: float
    cpu: float
    cpl: float
    cpk: float
    centering_ratio_k: float   # Ortalama kayıklığı katsayısı
    status: CapabilityStatus
    ppm_lower: float
    ppm_upper: float
    ppm_total: float
    diagnosis_note: str


class SPCEngine:
    @staticmethod
    def analyze(data: Iterable[Union[int, float]], nominal: float, usl: float, lsl: float) -> SPCResult:
        if usl <= lsl:
            raise ValueError(f"Üst limit ({usl}), alt limitten ({lsl}) büyük olmalıdır.")

        arr = np.asarray(data, dtype=np.float64)
        if arr.ndim != 1 or arr.size < 2:
            raise ValueError("Analiz için en az 2 adet sayısal ölçüm verisi girilmelidir.")

        sample_size = int(arr.size)
        mean = float(np.mean(arr))
        std_dev = float(np.std(arr, ddof=1))
        variance = float(np.var(arr, ddof=1))

        if std_dev == 0.0:
            raise ValueError("Standart sapma sıfır: Verilerde hiçbir değişkenlik bulunmuyor.")

        tolerance_span = usl - lsl
        cp = tolerance_span / (6.0 * std_dev)
        cpu = (usl - mean) / (3.0 * std_dev)
        cpl = (mean - lsl) / (3.0 * std_dev)
        cpk = min(cpu, cpl)

        # Ortalama sapması ve merkezleme kaybı
        mean_deviation = mean - nominal
        midpoint = (usl + lsl) / 2.0
        k = abs(mean - midpoint) / (tolerance_span / 2.0)

        # PPM Hesabı (Milyonda parça fire tahmini)
        z_lower = (lsl - mean) / std_dev
        z_upper = (usl - mean) / std_dev
        ppm_lower = float(stats.norm.cdf(z_lower) * 1_000_000)
        ppm_upper = float((1.0 - stats.norm.cdf(z_upper)) * 1_000_000)
        ppm_total = ppm_lower + ppm_upper

        if cpk >= 1.67:
            status = CapabilityStatus.EXCELLENT
        elif cpk >= 1.33:
            status = CapabilityStatus.CAPABLE
        elif cpk >= 1.00:
            status = CapabilityStatus.MARGINAL
        else:
            status = CapabilityStatus.INCAPABLE

        # Tezgâh Teşhis ve Aksiyon Notu
        if cp >= 1.33 and cpk < 1.33:
            shift = mean - midpoint
            diagnosis_note = (
                f"Tezgâh tekrarlanabilirliği yeterli (Cp={cp:.2f}), ancak ortalama hedef merkezden kaymış. "
                f"CNC aşınma ofsetine (wear offset) {-shift:+.4f} mm düzeltme vererek süreci merkeze çekiniz."
            )
        elif cp < 1.33:
            diagnosis_note = (
                f"Doğal yayılım yüksek (Cp={cp:.2f}). Tezgâh rijitliği, kesici uç titreşimi, "
                "iş parçası bağlama salgısı veya talaş sıkışması kontrol edilmelidir."
            )
        else:
            diagnosis_note = "Proses kararlı ve spesifikasyon sınırları içinde kontrol altındadır."

        return SPCResult(
            sample_size=sample_size,
            mean=mean,
            std_dev=std_dev,
            variance=variance,
            nominal=nominal,
            usl=usl,
            lsl=lsl,
            mean_deviation=mean_deviation,
            tolerance_span=tolerance_span,
            cp=cp,
            cpu=cpu,
            cpl=cpl,
            cpk=cpk,
            centering_ratio_k=k,
            status=status,
            ppm_lower=ppm_lower,
            ppm_upper=ppm_upper,
            ppm_total=ppm_total,
            diagnosis_note=diagnosis_note
        )
