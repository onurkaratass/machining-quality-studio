"""
SPC - Statistical Process Control for Manufacturing & Machining
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Açık kaynaklı, talaşlı imalat ve seri üretim odaklı istatistiksel
proses kontrolü ve proses yeterliliği (Cp, Cpk) analiz kütüphanesi.
"""

from spc.models import CapabilityStatus, ProcessCapabilityResult
from spc.analyzer import CapabilityAnalyzer
from spc.visualizer import ProcessVisualizer
from spc.reporter import ProcessReporter

__version__ = "0.1.0"
__all__ = [
    "CapabilityStatus",
    "ProcessCapabilityResult",
    "CapabilityAnalyzer",
    "ProcessVisualizer",
    "ProcessReporter",
]
