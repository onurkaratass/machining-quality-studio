"""
spc.reporter
~~~~~~~~~~~~
İstatistiksel proses kontrolü sonuçları için terminal raporlama ve karar destek motoru.
"""

from scipy import stats
from spc.models import CapabilityStatus, ProcessCapabilityResult


class ProcessReporter:
    """
    Hesaplanan proses yeterlilik verilerini mühendislik yorumlarıyla
    harmanlayarak terminal raporuna dönüştürür.
    """

    @staticmethod
    def calculate_estimated_scrap_ppm(result: ProcessCapabilityResult) -> tuple[float, float, float]:
        """
        Gauss dağılımı varsayımı altında alt, üst ve toplam tahmini fire (ppm) miktarını hesaplar.
        """
        z_lower = (result.lsl - result.mean) / result.std_dev
        z_upper = (result.usl - result.mean) / result.std_dev

        p_lower = stats.norm.cdf(z_lower)
        p_upper = 1.0 - stats.norm.cdf(z_upper)

        ppm_lower = float(p_lower * 1_000_000)
        ppm_upper = float(p_upper * 1_000_000)
        ppm_total = ppm_lower + ppm_upper

        return ppm_lower, ppm_upper, ppm_total

    @classmethod
    def generate_report(cls, result: ProcessCapabilityResult, part_name: str = "CNC İş Parçası") -> str:
        """
        Terminalde görüntülenebilecek yapılandırılmış metin raporu üretir.
        """
        ppm_l, ppm_u, ppm_tot = cls.calculate_estimated_scrap_ppm(result)

        # Karar ve Tezgâh Aksiyon Önerileri
        action_notes = []
        if result.status == CapabilityStatus.EXCELLENT:
            action_notes.append("Proses mükemmel yeterliliktedir. Seri üretime mevcut parametrelerle devam edilebilir.")
        elif result.status == CapabilityStatus.CAPABLE:
            action_notes.append("Proses endüstri standardında yeterlidir (Cpk >= 1.33). Periyodik numune kontrolü sürdürülmelidir.")
        elif result.status == CapabilityStatus.MARGINAL:
            action_notes.append("DİKKAT: Proses sınırda çalışıyor (1.00 <= Cpk < 1.33). Güvenlik marjı dar, sıkı kontrol önerilir.")
        else:
            action_notes.append("KRİTİK UYARI: Proses yetersizdir (Cpk < 1.00). Yüksek fire riski mevcuttur! Operasyon durdurulmalıdır.")

        # Takım Ofseti / Merkezleme Teşhisi
        if result.cp >= 1.33 and result.cpk < 1.33:
            action_notes.append(
                "TEŞHİS: Cp potansiyeli yüksek ancak Cpk yetersiz. Bu durum tezgâh hassasiyetinin iyi olduğunu fakat "
                "takım sıfırlama (work offset) veya takım aşınması (wear offset) nedeniyle ortalamanın kaydığını gösterir. "
                f"CNC tezgâhına {-result.mean_deviation:+.4f} mm ofset düzeltmesi verilmesi önerilir."
            )
        elif result.cp < 1.33:
            action_notes.append(
                "TEŞHİS: Cp değeri düşüktür. Prosesin doğal dağılımı (varyansı) geniştir. "
                "Tezgâh rijitliği, kesici uç aşınması, bağlama (fikstür) salgısı veya talaş sıkışması incelenmelidir."
            )

        report_lines = [
            "╔══════════════════════════════════════════════════════════════════════╗",
            "║        İSTATİSTİKSEL PROSES KONTROL (SPC) KALİTE VE YETERLİLİK RAPORU  ║",
            "╚══════════════════════════════════════════════════════════════════════╝",
            f" Parça / Operasyon Adı : {part_name}",
            f" İncelenen Örneklem    : {result.sample_size} Adet",
            "─" * 70,
            " 1. SPESİFİKASYON VE TEKNİK RESİM LİMİTLERİ",
            f"   • Nominal Ölçü      : {result.nominal:.4f} mm",
            f"   • Alt Tolerans (LSL): {result.lsl:.4f} mm",
            f"   • Üst Tolerans (USL): {result.usl:.4f} mm",
            f"   • Tolerans Genişliği: {result.tolerance_span:.4f} mm",
            "─" * 70,
            " 2. NUMUNE İSTATİSTİKLERİ",
            f"   • Örneklem Ortalaması (X̄) : {result.mean:.4f} mm",
            f"   • Standart Sapma (s)      : {result.std_dev:.4f} mm",
            f"   • Varyans (s²)            : {result.variance:.6f} mm²",
            f"   • Nominalden Sapma        : {result.mean_deviation:+.4f} mm",
            "─" * 70,
            " 3. PROSES YETERLİLİK İNDEKSLERİ",
            f"   • Potansiyel Yeterlilik (Cp) : {result.cp:.3f}",
            f"   • Üst Yeterlilik (Cpu)       : {result.cpu:.3f}",
            f"   • Alt Yeterlilik (Cpl)       : {result.cpl:.3f}",
            f"   • Fiili Yeterlilik (Cpk)     : {result.cpk:.3f}",
            f"   • Merkezleme Kaybı (k)       : {result.centering_ratio_k:.2%}",
            "─" * 70,
            " 4. TAHMİNİ FİRE ANALİZİ (PPM - Milyonda Parça)",
            f"   • Alt Limit Altı (< LSL)     : {ppm_l:.1f} PPM",
            f"   • Üst Limit Üstü (> USL)     : {ppm_u:.1f} PPM",
            f"   • Toplam Beklenen Fire       : {ppm_tot:.1f} PPM (%{ppm_tot / 10000:.4f})",
            "─" * 70,
            " 5. DEĞERLENDİRME VE AKSİYON",
            f"   • Durum : {result.status.value}",
        ]

        for note in action_notes:
            report_lines.append(f"   • {note}")

        report_lines.append("═" * 70)
        return "\n".join(report_lines)

    @classmethod
    def print_report(cls, result: ProcessCapabilityResult, part_name: str = "CNC İş Parçası") -> None:
        """Raporu doğrudan standart çıktıya yazdırır."""
        print(cls.generate_report(result, part_name=part_name))
