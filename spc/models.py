"""
spc.models
~~~~~~~~~~
SPC analiz modelleri ve veri tipleri.
"""

from dataclasses import dataclass
from enum import Enum


class CapabilityStatus(Enum):
    """Proses yeterlilik durumu sınıflandırması."""
    EXCELLENT = "Mükemmel / Yüksek Kararlılık (Cpk >= 1.67)"
    CAPABLE = "Yeterli ve Kontrol Altında (1.33 <= Cpk < 1.67)"
    MARGINAL = "Sınırda / Dikkat Gerektirir (1.00 <= Cpk < 1.33)"
    INCAPABLE = "Yetersiz / Yüksek Fire Riski (Cpk < 1.00)"


@dataclass(frozen=True)
class ProcessCapabilityResult:
    """Proses yeterlilik analizi sonuç veri sınıfı."""
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
