"""
core.machining_calc
~~~~~~~~~~~~~~~~~~~
CNC Frezeleme ve Tornalama için Kesme Parametreleri, Güç, Tork ve Talaş Debisi Motoru.
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple


class OperationType(Enum):
    MILLING = "Frezeleme"
    TURNING = "Tornalama"


@dataclass(frozen=True)
class WorkpieceMaterial:
    code: str
    name: str
    kc1_1: float   # 1 mm2 talaş kesiti için özgül kesme kuvveti (N/mm2)
    mc: float      # Kienzle talaş kalınlığı üssü
    recommended_vc_min: float # m/min (Karbür takım için)
    recommended_vc_max: float


MATERIALS: Dict[str, WorkpieceMaterial] = {
    "C45": WorkpieceMaterial("1.0503 (C45 / İmalat Çeliği)", "İmalat Çeliği C45", 1800.0, 0.25, 140.0, 220.0),
    "4140": WorkpieceMaterial("1.7225 (42CrMo4 / Islah Çeliği)", "Islah Çeliği 4140", 2100.0, 0.26, 120.0, 190.0),
    "304": WorkpieceMaterial("1.4301 (AISI 304 / Paslanmaz)", "Paslanmaz Çelik 304", 2200.0, 0.23, 100.0, 160.0),
    "AL7075": WorkpieceMaterial("3.4365 (Alüminyum 7075 / T6)", "Alüminyum 7075", 700.0, 0.25, 300.0, 600.0),
    "GG25": WorkpieceMaterial("0.6025 (Pik Döküm / GG25)", "Pik Dökme Demir", 1100.0, 0.28, 150.0, 250.0),
}


@dataclass(frozen=True)
class MachiningResult:
    operation: OperationType
    material_name: str
    diameter: float           # Takım çapı (freze) veya iş parçası çapı (torna) mm
    cutting_speed: float      # Vc (m/min)
    rpm: float                # N (dev/dak)
    feed_rate: float          # Vf (mm/dak)
    feed_per_tooth_or_rev: float # fz (mm/diş) veya f (mm/dev)
    depth_of_cut_ap: float    # ap (mm)
    width_of_cut_ae: float    # ae (mm)
    mrr: float                # Talaş kaldırma debisi (cm3/dak)
    kc: float                 # Özgül kesme kuvveti (N/mm2)
    cutting_force_fc: float   # Teğetsel kesme kuvveti (N)
    power_kw: float           # Tezgâh net kesme gücü (kW)
    torque_nm: float          # Fener mili torku (Nm)


def calculate_milling(
    diameter: float,
    teeth_z: int,
    cutting_speed_vc: float,
    feed_per_tooth_fz: float,
    depth_ap: float,
    width_ae: float,
    material_key: str = "C45",
    efficiency_eta: float = 0.85
) -> MachiningResult:
    """CNC Frezeleme kesme kuvveti, güç, tork ve talaş debisi hesabı."""
    if diameter <= 0 or teeth_z <= 0 or cutting_speed_vc <= 0 or feed_per_tooth_fz <= 0:
        raise ValueError("Parametreler pozitif sayı olmalıdır.")
    if width_ae > diameter:
        width_ae = diameter

    mat = MATERIALS.get(material_key, MATERIALS["C45"])

    # Devir: N = (1000 * Vc) / (pi * D)
    rpm = (1000.0 * cutting_speed_vc) / (math.pi * diameter)
    
    # İlerleme hızı: Vf = fz * z * N
    feed_rate = feed_per_tooth_fz * teeth_z * rpm

    # Talaş kaldırma debisi (cm3/dak): (ap * ae * Vf) / 1000
    mrr = (depth_ap * width_ae * feed_rate) / 1000.0

    # Ortalama talaş kalınlığı (Kienzle hm): hm = fz * sqrt(ae / D)
    hm = feed_per_tooth_fz * math.sqrt(width_ae / diameter)
    hm = max(hm, 0.001)

    # Özgül kesme kuvveti: kc = kc1.1 * hm^(-mc)
    kc = mat.kc1_1 * (hm ** (-mat.mc))

    # Kesme gücü (kW): (ap * ae * Vf * kc) / (60 * 10^6 * eta)
    power_kw = (depth_ap * width_ae * feed_rate * kc) / (60.0 * 1e6 * efficiency_eta)

    # Tork (Nm): (9550 * Pc) / N
    torque_nm = (9550.0 * power_kw) / rpm if rpm > 0 else 0.0

    # Ortalama teğetsel kesme kuvveti: Fc = (Pc * 60000) / Vc
    cutting_force_fc = (power_kw * 1000.0 * 60.0) / cutting_speed_vc if cutting_speed_vc > 0 else 0.0

    return MachiningResult(
        operation=OperationType.MILLING,
        material_name=mat.name,
        diameter=diameter,
        cutting_speed=cutting_speed_vc,
        rpm=rpm,
        feed_rate=feed_rate,
        feed_per_tooth_or_rev=feed_per_tooth_fz,
        depth_of_cut_ap=depth_ap,
        width_of_cut_ae=width_ae,
        mrr=mrr,
        kc=kc,
        cutting_force_fc=cutting_force_fc,
        power_kw=power_kw,
        torque_nm=torque_nm
    )


def calculate_turning(
    diameter: float,
    cutting_speed_vc: float,
    feed_rev_f: float,
    depth_ap: float,
    material_key: str = "C45",
    efficiency_eta: float = 0.85
) -> MachiningResult:
    """CNC Tornalama kesme kuvveti, güç, tork ve talaş debisi hesabı."""
    if diameter <= 0 or cutting_speed_vc <= 0 or feed_rev_f <= 0 or depth_ap <= 0:
        raise ValueError("Parametreler pozitif sayı olmalıdır.")

    mat = MATERIALS.get(material_key, MATERIALS["C45"])

    # Devir: N = (1000 * Vc) / (pi * D)
    rpm = (1000.0 * cutting_speed_vc) / (math.pi * diameter)
    
    # İlerleme hızı: Vf = f * N (mm/dak)
    feed_rate = feed_rev_f * rpm

    # Talaş kaldırma debisi (cm3/dak): Vc * ap * f (cm3/dak)
    mrr = cutting_speed_vc * depth_ap * feed_rev_f

    # Tornalamada ortalama talaş kalınlığı hm yaklaşık f (besleme) alınır
    hm = max(feed_rev_f, 0.001)

    # Özgül kesme kuvveti: kc = kc1.1 * hm^(-mc)
    kc = mat.kc1_1 * (hm ** (-mat.mc))

    # Teğetsel kesme kuvveti (N): Fc = ap * f * kc
    cutting_force_fc = depth_ap * feed_rev_f * kc

    # Kesme gücü (kW): (Fc * Vc) / (60000 * eta)
    power_kw = (cutting_force_fc * cutting_speed_vc) / (60000.0 * efficiency_eta)

    # Tork (Nm): (9550 * Pc) / N
    torque_nm = (9550.0 * power_kw) / rpm if rpm > 0 else 0.0

    return MachiningResult(
        operation=OperationType.TURNING,
        material_name=mat.name,
        diameter=diameter,
        cutting_speed=cutting_speed_vc,
        rpm=rpm,
        feed_rate=feed_rate,
        feed_per_tooth_or_rev=feed_rev_f,
        depth_of_cut_ap=depth_ap,
        width_of_cut_ae=0.0,
        mrr=mrr,
        kc=kc,
        cutting_force_fc=cutting_force_fc,
        power_kw=power_kw,
        torque_nm=torque_nm
    )


@dataclass
class GCodeSegment:
    start_pos: Tuple[float, float, float]
    end_pos: Tuple[float, float, float]
    motion_type: str  # "G00", "G01", "G02", "G03"
    feed_rate: float
    line_number: int


@dataclass
class GCodeAnalysisResult:
    total_lines: int
    rapid_distance_mm: float
    cut_distance_mm: float
    estimated_time_seconds: float
    tools_used: List[str]
    min_bounds: Tuple[float, float, float]
    max_bounds: Tuple[float, float, float]
    errors: List[str]
    warnings: List[str]
    segments: List[GCodeSegment]


class GCodeSimulator:
    def __init__(
        self,
        x_limits: Tuple[float, float] = (-300.0, 300.0),
        y_limits: Tuple[float, float] = (-200.0, 200.0),
        z_limits: Tuple[float, float] = (-250.0, 50.0),
        rapid_speed_mm_min: float = 15000.0
    ):
        self.x_lim = x_limits
        self.y_lim = y_limits
        self.z_lim = z_limits
        self.rapid_speed = rapid_speed_mm_min

    def analyze(self, gcode_text: str) -> GCodeAnalysisResult:
        import re
        lines = gcode_text.strip().splitlines()
        errors = []
        warnings = []
        segments = []

        cur_x, cur_y, cur_z = 0.0, 0.0, 0.0
        active_motion = "G00"
        active_feed = 0.0
        active_spindle = 0
        spindle_running = False
        distance_mode = "G90"
        unit_mode = "G21"

        min_x, max_x = 0.0, 0.0
        min_y, max_y = 0.0, 0.0
        min_z, max_z = 0.0, 0.0

        rapid_dist = 0.0
        cut_dist = 0.0
        est_time_sec = 0.0

        tools_used = set()
        has_program_end = False
        has_tool_height_comp = False
        active_tool = None

        for line_num, raw_line in enumerate(lines, start=1):
            clean_line = re.sub(r'\(.*?\)', '', raw_line)
            clean_line = clean_line.split(';')[0].strip().upper()
            if not clean_line:
                continue

            tokens = re.findall(r'([A-Z])\s*([+-]?\d*\.?\d+)', clean_line)
            word_dict = {t[0]: float(t[1]) if '.' in t[1] else int(t[1]) for t in tokens}
            g_codes = [int(float(t[1])) for t in tokens if t[0] == 'G']
            m_codes = [int(float(t[1])) for t in tokens if t[0] == 'M']

            if 90 in g_codes: distance_mode = "G90"
            if 91 in g_codes: distance_mode = "G91"
            if 20 in g_codes: unit_mode = "G20"
            if 21 in g_codes: unit_mode = "G21"
            if 43 in g_codes: has_tool_height_comp = True
            if 49 in g_codes: has_tool_height_comp = False

            if 3 in m_codes or 4 in m_codes: spindle_running = True
            if 5 in m_codes: spindle_running = False
            if 30 in m_codes or 2 in m_codes: has_program_end = True

            if 'S' in word_dict: active_spindle = int(word_dict['S'])
            if 'F' in word_dict: active_feed = float(word_dict['F'])
            if 'T' in word_dict:
                active_tool = f"T{int(word_dict['T']):02d}"
                tools_used.add(active_tool)
                est_time_sec += 5.0

            for g in g_codes:
                if g in [0, 1, 2, 3]:
                    active_motion = f"G{g:02d}"

            target_x = cur_x
            target_y = cur_y
            target_z = cur_z

            has_coord = False
            if 'X' in word_dict:
                has_coord = True
                val = float(word_dict['X'])
                target_x = (cur_x + val) if distance_mode == "G91" else val
            if 'Y' in word_dict:
                has_coord = True
                val = float(word_dict['Y'])
                target_y = (cur_y + val) if distance_mode == "G91" else val
            if 'Z' in word_dict:
                has_coord = True
                val = float(word_dict['Z'])
                target_z = (cur_z + val) if distance_mode == "G91" else val

            if has_coord:
                if not (self.x_lim[0] <= target_x <= self.x_lim[1]):
                    errors.append(f"Satır {line_num}: X={target_x:.3f} mm tezgâh sınırını ({self.x_lim[0]:.0f} ila {self.x_lim[1]:.0f} mm) AŞTI!")
                if not (self.y_lim[0] <= target_y <= self.y_lim[1]):
                    errors.append(f"Satır {line_num}: Y={target_y:.3f} mm tezgâh sınırını ({self.y_lim[0]:.0f} ila {self.y_lim[1]:.0f} mm) AŞTI!")
                if not (self.z_lim[0] <= target_z <= self.z_lim[1]):
                    errors.append(f"Satır {line_num}: Z={target_z:.3f} mm tezgâh sınırını ({self.z_lim[0]:.0f} ila {self.z_lim[1]:.0f} mm) AŞTI!")

            if active_motion in ["G01", "G02", "G03"] and has_coord:
                if not spindle_running or active_spindle <= 0:
                    errors.append(f"Satır {line_num}: Fener mili çalıştırılmadan (M03 / S eksik) talaşlı kesme hareketi ({active_motion}) yapıldı!")
                if active_feed <= 0.0:
                    errors.append(f"Satır {line_num}: İlerleme hızı (F) tanımlanmadan kesme hareketi ({active_motion}) yapıldı!")

            if active_motion == "G00" and target_z < cur_z and target_z < 0.0:
                warnings.append(f"Satır {line_num}: G00 hızlı ilerleme ile Z={target_z:.3f} eksi koda dalış yapılıyor! Çarpma (Crash) riski!")

            if 4 in g_codes:
                p_val = float(word_dict.get('P', word_dict.get('X', 0.0)))
                est_time_sec += p_val

            dx = target_x - cur_x
            dy = target_y - cur_y
            dz = target_z - cur_z
            step_dist = math.sqrt(dx*dx + dy*dy + dz*dz)

            if step_dist > 0.0001:
                if active_motion == "G00":
                    rapid_dist += step_dist
                    est_time_sec += (step_dist / (self.rapid_speed / 60.0))
                else:
                    cut_dist += step_dist
                    feed_actual = active_feed if active_feed > 0 else 500.0
                    est_time_sec += (step_dist / (feed_actual / 60.0))

                segments.append(GCodeSegment(
                    start_pos=(cur_x, cur_y, cur_z),
                    end_pos=(target_x, target_y, target_z),
                    motion_type=active_motion,
                    feed_rate=active_feed,
                    line_number=line_num
                ))

            cur_x, cur_y, cur_z = target_x, target_y, target_z
            min_x, max_x = min(min_x, cur_x), max(max_x, cur_x)
            min_y, max_y = min(min_y, cur_y), max(max_y, cur_y)
            min_z, max_z = min(min_z, cur_z), max(max_z, cur_z)

        if not has_program_end:
            warnings.append("Program sonu komutu (M30 veya M02) bulunamadı.")
        if active_tool and not has_tool_height_comp:
            warnings.append("Takım değiştirilmiş ancak G43 H (takım boy telafisi) kodu çağrılmamış.")

        return GCodeAnalysisResult(
            total_lines=len(lines),
            rapid_distance_mm=rapid_dist,
            cut_distance_mm=cut_dist,
            estimated_time_seconds=est_time_sec,
            tools_used=sorted(list(tools_used)),
            min_bounds=(min_x, min_y, min_z),
            max_bounds=(max_x, max_y, max_z),
            errors=errors,
            warnings=warnings,
            segments=segments
        )


@dataclass(frozen=True)
class CostResult:
    part_name: str
    weight_kg: float
    material_cost: float
    machine_cost: float
    setup_cost: float
    tool_cost: float
    base_unit_cost: float
    profit_margin_tl: float
    final_unit_price: float
    total_batch_price: float
    batch_size: int


class CostEngine:
    @staticmethod
    def calculate(
        part_name: str,
        diameter_mm: float,
        length_mm: float,
        density_g_cm3: float,
        price_per_kg_tl: float,
        cycle_time_min: float,
        machine_hour_rate_tl: float,
        tool_wear_cost_tl: float,
        setup_time_min: float,
        labor_hour_rate_tl: float,
        batch_size: int,
        markup_percent: float
    ) -> CostResult:
        import math
        vol_cm3 = (math.pi * (diameter_mm / 2.0)**2 * length_mm) / 1000.0
        weight_kg = (vol_cm3 * density_g_cm3) / 1000.0
        material_cost = weight_kg * price_per_kg_tl
        machine_cost = (cycle_time_min / 60.0) * machine_hour_rate_tl
        b_size = max(1, batch_size)
        setup_per_part = ((setup_time_min / 60.0) * labor_hour_rate_tl) / b_size

        base_unit_cost = material_cost + machine_cost + tool_wear_cost_tl + setup_per_part
        profit_tl = base_unit_cost * (markup_percent / 100.0)
        final_unit_price = base_unit_cost + profit_tl
        total_batch_price = final_unit_price * b_size

        return CostResult(
            part_name=part_name,
            weight_kg=weight_kg,
            material_cost=material_cost,
            machine_cost=machine_cost,
            setup_cost=setup_per_part,
            tool_cost=tool_wear_cost_tl,
            base_unit_cost=base_unit_cost,
            profit_margin_tl=profit_tl,
            final_unit_price=final_unit_price,
            total_batch_price=total_batch_price,
            batch_size=b_size
        )


@dataclass(frozen=True)
class SurfaceRoughnessResult:
    r_eps_mm: float
    feed_mm_rev: float
    rth_um: float
    ra_um: float
    rz_um: float
    iso_grade: str
    max_feed_for_target_ra: float


class SurfaceRoughnessEngine:
    @staticmethod
    def calculate(feed_mm_rev: float, r_eps_mm: float, target_ra_um: float = 1.6) -> SurfaceRoughnessResult:
        import math
        r_eps = max(0.01, r_eps_mm)
        f = max(0.001, feed_mm_rev)

        rth = (f ** 2) / (8.0 * r_eps) * 1000.0
        ra = rth / 4.0
        rz = rth

        if ra <= 0.05: iso_grade = "N2 (Süper Ayna / Polisaj)"
        elif ra <= 0.1: iso_grade = "N3 (Ayna Parlaklığı)"
        elif ra <= 0.2: iso_grade = "N4 (Çok İnce Taşlama)"
        elif ra <= 0.4: iso_grade = "N5 (İnce Taşlama / Parlatma)"
        elif ra <= 0.8: iso_grade = "N6 (Hassas İnce Torna / Taşlama)"
        elif ra <= 1.6: iso_grade = "N7 (Standart Hassas Talaşlı İmalat)"
        elif ra <= 3.2: iso_grade = "N8 (Normal Torna / Freze Bitirme)"
        elif ra <= 6.3: iso_grade = "N9 (Kaba Torna / Freze)"
        elif ra <= 12.5: iso_grade = "N10 (Ağır Kaba Talaş Kaldırma)"
        else: iso_grade = "N11+ (Çok Kaba Yüzey)"

        # Hedef Ra için maksimum güvenli ilerleme
        target_rth = max(0.01, target_ra_um) * 4.0
        max_feed = math.sqrt((target_rth * 8.0 * r_eps) / 1000.0)

        return SurfaceRoughnessResult(
            r_eps_mm=r_eps,
            feed_mm_rev=f,
            rth_um=rth,
            ra_um=ra,
            rz_um=rz,
            iso_grade=iso_grade,
            max_feed_for_target_ra=max_feed
        )


@dataclass(frozen=True)
class ThreadInfo:
    designation: str
    nominal_dia_mm: float
    pitch_mm: float
    drill_dia_mm: float
    thread_type: str
    depth_mm: float


class ThreadEngine:
    METRIC_COARSE: Dict[str, Tuple[float, float]] = {
        "M3": (0.5, 2.5),
        "M4": (0.7, 3.3),
        "M5": (0.8, 4.2),
        "M6": (1.0, 5.0),
        "M8": (1.25, 6.8),
        "M10": (1.5, 8.5),
        "M12": (1.75, 10.2),
        "M14": (2.0, 12.0),
        "M16": (2.0, 14.0),
        "M18": (2.5, 15.5),
        "M20": (2.5, 17.5),
        "M24": (3.0, 21.0),
        "M30": (3.5, 26.5),
        "M36": (4.0, 32.0),
    }

    METRIC_FINE: Dict[str, Tuple[float, float]] = {
        "M8x1.0": (1.0, 7.0),
        "M10x1.0": (1.0, 9.0),
        "M10x1.25": (1.25, 8.8),
        "M12x1.25": (1.25, 10.8),
        "M12x1.5": (1.5, 10.5),
        "M14x1.5": (1.5, 12.5),
        "M16x1.5": (1.5, 14.5),
        "M20x1.5": (1.5, 18.5),
    }

    PIPE_BSP: Dict[str, Tuple[float, float, float]] = {
        "G 1/8": (9.728, 0.907, 8.8),
        "G 1/4": (13.157, 1.337, 11.8),
        "G 3/8": (16.662, 1.337, 15.25),
        "G 1/2": (20.955, 1.814, 19.0),
        "G 3/4": (26.441, 1.814, 24.5),
        "G 1": (33.249, 2.309, 30.75),
    }

    @classmethod
    def get_thread(cls, name: str) -> ThreadInfo:
        if name in cls.METRIC_COARSE:
            p, d = cls.METRIC_COARSE[name]
            nom = float(name.replace('M', ''))
            depth = 0.6134 * p
            return ThreadInfo(name, nom, p, d, "Metrik Standart (Kaba)", depth)
        elif name in cls.METRIC_FINE:
            p, d = cls.METRIC_FINE[name]
            nom = float(name.split('x')[0].replace('M', ''))
            depth = 0.6134 * p
            return ThreadInfo(name, nom, p, d, "Metrik İnce Diş", depth)
        elif name in cls.PIPE_BSP:
            nom, p, d = cls.PIPE_BSP[name]
            depth = 0.6403 * p
            return ThreadInfo(name, nom, p, d, "Gaz / Boru Dişi (BSP/G)", depth)
        raise ValueError(f"Bilinmeyen diş: {name}")
