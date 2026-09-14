"""
core.limits_fits
~~~~~~~~~~~~~~~~
ISO 286-1 ve ISO 286-2 standardına uygun Delik-Mil Tolerans ve Geçme Hesaplayıcısı.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class FitType(Enum):
    CLEARANCE = "Boşluklu Geçme"
    TRANSITION = "Ara Geçme"
    INTERFERENCE = "Sıkı Geçme"


@dataclass(frozen=True)
class FitResult:
    nominal_diameter: float
    fit_designation: str          # örn: "30 H7/g6"
    hole_class: str               # örn: "H7"
    shaft_class: str              # örn: "g6"
    
    # Delik Limitleri (mm)
    hole_es: float                # Üst sapma (mm)
    hole_ei: float                # Alt sapma (mm)
    hole_max: float               # Maksimum delik çapı (mm)
    hole_min: float               # Minimum delik çapı (mm)
    hole_tol: float               # Delik toleransı (mm)

    # Mil Limitleri (mm)
    shaft_es: float               # Üst sapma (mm)
    shaft_ei: float               # Alt sapma (mm)
    shaft_max: float              # Maksimum mil çapı (mm)
    shaft_min: float              # Minimum mil çapı (mm)
    shaft_tol: float              # Mil toleransı (mm)

    # Geçme Özellikleri
    fit_type: FitType
    max_clearance: float          # Maksimum boşluk (mm) - negatifse sıkılık
    min_clearance: float          # Minimum boşluk (mm) - negatifse sıkılık
    max_interference: float       # Maksimum sıkılık (mm)
    min_interference: float       # Minimum sıkılık (mm)


# ISO 286 standart nominal çap kademeleri (mm): (min, max]
_SIZE_STEPS = [
    (0, 3), (3, 6), (6, 10), (10, 18), (18, 30),
    (30, 50), (50, 80), (80, 120), (120, 180), (180, 250),
    (250, 315), (315, 400), (400, 500)
]

# Standart Tolerans Değerleri (IT) - mikrometre (um)
_IT_TABLE = {
    6:  [6,  8,  9,  11, 13, 16, 19, 22, 25, 29, 32, 36, 40],
    7:  [10, 12, 15, 18, 21, 25, 30, 35, 40, 46, 52, 57, 63],
    8:  [14, 18, 22, 27, 33, 39, 46, 54, 63, 72, 81, 89, 97],
    9:  [25, 30, 36, 43, 52, 62, 74, 87, 100, 115, 130, 140, 155],
    10: [40, 48, 58, 70, 84, 100, 120, 140, 160, 185, 210, 230, 250],
    11: [60, 75, 90, 110, 130, 160, 190, 220, 250, 290, 320, 360, 400]
}

# Mil Esas Sapmaları (um)
_SHAFT_DEVIATIONS = {
    'c': [-60, -70, -80, -95, -110, -130, -150, -180, -230, -280, -330, -380, -440],
    'd': [-20, -30, -40, -50, -65,  -80,  -100, -120, -145, -170, -190, -210, -230],
    'e': [-14, -20, -25, -32, -40,  -50,  -60,  -72,  -85,  -100, -110, -125, -135],
    'f': [-6,  -10, -13, -16, -20,  -25,  -30,  -36,  -43,  -50,  -56,  -62,  -68],
    'g': [-2,  -4,  -5,  -6,  -7,   -9,   -10,  -12,  -14,  -15,  -17,  -18,  -20],
    'h': [0,   0,   0,   0,   0,    0,    0,    0,    0,    0,    0,    0,    0],
    'js': [0,  0,   0,   0,   0,    0,    0,    0,    0,    0,    0,    0,    0],  # simetrik
    'k': [0,   +1,  +1,  +1,  +2,   +2,   +2,   +3,   +3,   +4,   +4,   +4,   +5],
    'm': [+2,  +4,  +6,  +7,  +8,   +9,   +11,  +13,  +15,  +17,  +20,  +21,  +23],
    'n': [+4,  +8,  +10, +12, +15,  +17,  +20,  +23,  +27,  +31,  +35,  +37,  +40],
    'p': [+6,  +12, +15, +18, +22,  +26,  +32,  +37,  +43,  +48,  +54,  +59,  +65],
    'r': [+10, +15, +19, +23, +28,  +34,  +41,  +48,  +56,  +64,  +72,  +79,  +87],
    's': [+14, +19, +23, +28, +35,  +43,  +53,  +63,  +73,  +84,  +94,  +104, +115],
}


def _get_step_index(diameter: float) -> int:
    if diameter <= 0 or diameter > 500:
        raise ValueError(f"Nominal çap 0 ile 500 mm arasında olmalıdır. Girilen: {diameter}")
    for idx, (low, high) in enumerate(_SIZE_STEPS):
        if idx == 0 and diameter <= high:
            return idx
        if low < diameter <= high:
            return idx
    return len(_SIZE_STEPS) - 1


def calculate_iso_fit(diameter: float, hole_class: str = "H7", shaft_class: str = "g6") -> FitResult:
    """
    ISO 286 sistemine göre delik ve mil tolerans limitlerini ve geçme türünü hesaplar.
    """
    idx = _get_step_index(diameter)
    
    # Delik Hesabı (H serisi: EI = 0, ES = +IT)
    hole_letter = hole_class[0].upper()
    hole_grade = int(hole_class[1:])
    if hole_letter != "H" or hole_grade not in _IT_TABLE:
        raise ValueError(f"Desteklenmeyen delik sınıfı: {hole_class}. Örn: H6, H7, H8, H9, H11")

    hole_it_um = _IT_TABLE[hole_grade][idx]
    hole_ei_mm = 0.0
    hole_es_mm = hole_it_um / 1000.0

    # Mil Hesabı
    shaft_letter = ""
    for ch in shaft_class:
        if ch.isalpha():
            shaft_letter += ch.lower()
        else:
            break
    shaft_grade = int(shaft_class[len(shaft_letter):])

    if shaft_letter not in _SHAFT_DEVIATIONS or shaft_grade not in _IT_TABLE:
        raise ValueError(f"Desteklenmeyen mil sınıfı: {shaft_class}. Örn: h6, g6, f7, p6, k6")

    shaft_it_um = _IT_TABLE[shaft_grade][idx]

    if shaft_letter == "js":
        # Simetrik tolerans: ± IT/2
        shaft_es_mm = +(shaft_it_um / 2.0) / 1000.0
        shaft_ei_mm = -(shaft_it_um / 2.0) / 1000.0
    elif shaft_letter in ['c', 'd', 'e', 'f', 'g', 'h']:
        # Üst sapma es verilir, ei = es - it
        es_um = _SHAFT_DEVIATIONS[shaft_letter][idx]
        ei_um = es_um - shaft_it_um
        shaft_es_mm = es_um / 1000.0
        shaft_ei_mm = ei_um / 1000.0
    else:
        # Alt sapma ei verilir (k, m, n, p, r, s), es = ei + it
        ei_um = _SHAFT_DEVIATIONS[shaft_letter][idx]
        es_um = ei_um + shaft_it_um
        shaft_es_mm = es_um / 1000.0
        shaft_ei_mm = ei_um / 1000.0

    # Limit Ölçüler
    hole_min = diameter + hole_ei_mm
    hole_max = diameter + hole_es_mm
    shaft_min = diameter + shaft_ei_mm
    shaft_max = diameter + shaft_es_mm

    # Boşluk ve Sıkılık Hesabı
    # Boşluk = Delik - Mil
    max_clearance = hole_max - shaft_min
    min_clearance = hole_min - shaft_max

    # Geçme Türü Tespiti
    if min_clearance > 0:
        fit_type = FitType.CLEARANCE
        max_interf = 0.0
        min_interf = 0.0
    elif max_clearance < 0:
        fit_type = FitType.INTERFERENCE
        max_interf = abs(min_clearance)
        min_interf = abs(max_clearance)
    else:
        fit_type = FitType.TRANSITION
        max_interf = abs(min_clearance) if min_clearance < 0 else 0.0
        min_interf = 0.0

    return FitResult(
        nominal_diameter=diameter,
        fit_designation=f"Ø{diameter:.3f} {hole_class}/{shaft_class}",
        hole_class=hole_class,
        shaft_class=shaft_class,
        hole_es=hole_es_mm,
        hole_ei=hole_ei_mm,
        hole_max=hole_max,
        hole_min=hole_min,
        hole_tol=hole_es_mm - hole_ei_mm,
        shaft_es=shaft_es_mm,
        shaft_ei=shaft_ei_mm,
        shaft_max=shaft_max,
        shaft_min=shaft_min,
        shaft_tol=shaft_es_mm - shaft_ei_mm,
        fit_type=fit_type,
        max_clearance=max_clearance,
        min_clearance=min_clearance,
        max_interference=max_interf,
        min_interference=min_interf
    )
