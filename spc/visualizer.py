"""
spc.visualizer
~~~~~~~~~~~~~~
Proses yeterlilik dağılımı (Histogram, Gauss eğrisi ve tolerans sınırları) görselleştirme motoru.
"""

from typing import Iterable, Optional, Tuple, Union
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from spc.models import ProcessCapabilityResult


class ProcessVisualizer:
    """
    Ölçüm verilerini ve proses yeterlilik indekslerini Matplotlib
    üzerinde profesyonel kalite kontrol grafiğine dönüştürür.
    """

    def __init__(self, style: str = "seaborn-v0_8-whitegrid") -> None:
        """
        Parametreler:
            style (str): Matplotlib grafik stili.
        """
        try:
            plt.style.use(style)
        except OSError:
            plt.style.use("default")

    def plot_capability(
        self,
        data: Iterable[Union[int, float]],
        result: ProcessCapabilityResult,
        title: str = "Proses Yeterlilik Dağılımı (SPC Histogram & Gauss Eğrisi)",
        bins: Union[int, str] = "auto",
        save_path: Optional[str] = None,
        dpi: int = 300,
        show: bool = False,
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Histogram, normal dağılım eğrisi ve tolerans limitlerini çizer.

        Parametreler:
            data (Iterable[float]): Ölçülen ham veri dizisi.
            result (ProcessCapabilityResult): Hesaplanan SPC sonuç nesnesi.
            title (str): Grafik başlığı.
            bins (int | str): Histogram sepet sayısı ('auto' veya int).
            save_path (str, optional): Grafiğin kaydedileceği dosya yolu.
            dpi (int): Çıktı çözünürlüğü.
            show (bool): plt.show() fonksiyonunu çağırıp çağırmayacağı.

        Döndürür:
            Tuple[plt.Figure, plt.Axes]: Oluşturulan figür ve eksen nesneleri.
        """
        arr = np.asarray(data, dtype=np.float64)

        fig, ax = plt.subplots(figsize=(11, 6.5))

        # 1. Histogram (Yoğunluk normalize edilmiş)
        ax.hist(
            arr,
            bins=bins,
            density=True,
            alpha=0.55,
            color="#2b5c8f",
            edgecolor="#16385c",
            linewidth=1.1,
            label="Ölçüm Dağılımı (Frekans)",
        )

        # 2. X ekseni sınırları ve Gauss Eğrisi
        span_margin = result.tolerance_span * 0.25
        x_min = min(result.lsl - span_margin, float(np.min(arr)) - 0.005)
        x_max = max(result.usl + span_margin, float(np.max(arr)) + 0.005)
        x_axis = np.linspace(x_min, x_max, 1000)

        pdf = stats.norm.pdf(x_axis, loc=result.mean, scale=result.std_dev)
        ax.plot(
            x_axis,
            pdf,
            color="#1b1e23",
            linewidth=2.2,
            label=f"Gauss Dağılımı (μ={result.mean:.3f}, σ={result.std_dev:.3f})",
        )

        # 3. Fire Riski Alanlarının Taranması (Tolerans Dışı Kuyruklar)
        x_below_lsl = x_axis[x_axis <= result.lsl]
        if len(x_below_lsl) > 0:
            ax.fill_between(
                x_below_lsl,
                0,
                stats.norm.pdf(x_below_lsl, loc=result.mean, scale=result.std_dev),
                color="#d9534f",
                alpha=0.35,
                label="Alt Fire Riski (< LSL)",
            )

        x_above_usl = x_axis[x_axis >= result.usl]
        if len(x_above_usl) > 0:
            ax.fill_between(
                x_above_usl,
                0,
                stats.norm.pdf(x_above_usl, loc=result.mean, scale=result.std_dev),
                color="#d9534f",
                alpha=0.35,
                label="Üst Fire Riski (> USL)",
            )

        # 4. Limit Çizgileri
        ax.axvline(
            result.lsl,
            color="#c9302c",
            linestyle="--",
            linewidth=2.0,
            label=f"LSL: {result.lsl:.3f} mm",
        )
        ax.axvline(
            result.usl,
            color="#c9302c",
            linestyle="--",
            linewidth=2.0,
            label=f"USL: {result.usl:.3f} mm",
        )
        ax.axvline(
            result.nominal,
            color="#2e7d32",
            linestyle="-",
            linewidth=1.8,
            label=f"Nominal: {result.nominal:.3f} mm",
        )
        ax.axvline(
            result.mean,
            color="#e65100",
            linestyle=":",
            linewidth=2.0,
            label=f"Ortalama (Ortalama): {result.mean:.3f} mm",
        )

        # 5. İstatistiksel Bilgi Kutusu (Sol Üst Köşe)
        stats_box_text = (
            f"Örneklem (N) : {result.sample_size}\n"
            f"Ortalama (Ortalama)  : {result.mean:.4f} mm\n"
            f"Sapma (s)     : {result.std_dev:.4f} mm\n"
            f"Nom. Sapması  : {result.mean_deviation:+.4f} mm\n"
            f"──────────────────────\n"
            f"Cp            : {result.cp:.3f}\n"
            f"Cpk           : {result.cpk:.3f}\n"
            f"Cpu / Cpl     : {result.cpu:.2f} / {result.cpl:.2f}\n"
            f"Merkezleme (k): {result.centering_ratio_k:.2%}"
        )
        ax.text(
            0.02,
            0.96,
            stats_box_text,
            transform=ax.transAxes,
            fontsize=9.5,
            family="monospace",
            verticalalignment="top",
            bbox=dict(
                boxstyle="round,pad=0.6",
                facecolor="#fdfdfd",
                edgecolor="#b0bec5",
                alpha=0.92,
            ),
        )

        # 6. Eksen ve Başlık Düzenlemeleri
        ax.set_title(title, fontsize=13, fontweight="bold", pad=15)
        ax.set_xlabel("Ölçülen Değer (mm)", fontsize=10.5, labelpad=8)
        ax.set_ylabel("Olasılık Yoğunluğu", fontsize=10.5, labelpad=8)
        ax.set_xlim(x_min, x_max)
        ax.grid(True, linestyle="--", alpha=0.45)
        ax.legend(loc="upper right", framealpha=0.9, fontsize=9)

        fig.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=dpi, bbox_inches="tight")

        if show:
            plt.show()

        return fig, ax
