"""
ui.tab_spc
~~~~~~~~~~
Gelişmiş SPC Proses Yeterlilik, Büyük Okunabilir Fontlar ve Açıklayıcı Kullanım Rehberi.
"""

import os
from tkinter import filedialog, messagebox
import customtkinter as ctk
import numpy as np
import pandas as pd
from scipy import stats

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from core.spc_engine import SPCEngine, SPCResult, CapabilityStatus
from core.pdf_exporter import QualityReportGenerator
from ui.styles import COLORS


class TabSPC(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color=COLORS["bg_app"], corner_radius=0)
        self.main_app = main_app
        self.current_result: SPCResult = None
        self.current_data = []
        self._build_ui()

    def _build_ui(self):
        # 1. Üst Başlık ve Eğitici Rehber Kutusu
        self.top_bar = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=12)
        self.top_bar.pack(fill="x", padx=16, pady=(12, 6))

        self.lbl_head = ctk.CTkLabel(
            self.top_bar,
            text="İSTATİSTİKSEL PROSES KONTROL (SPC) & MAKİNE YETERLİLİK ANALİZİ",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.lbl_head.pack(anchor="w", padx=18, pady=(10, 2))

        # Açıklayıcı Kullanım Rehberi (Herkesin kolayca anlayacağı adım adım açıklama)
        self.lbl_guide = ctk.CTkLabel(
            self.top_bar,
            text="💡 Nasıl Kullanılır?\n"
                 "1. Teknik resimdeki hedef anma ölçüsünü (Nominal) ve tolerans limitlerini (LSL/USL) girin.\n"
                 "2. Tezgâhtan çıkan parçaların kumpas/mikrometre ölçüm değerlerini alt alta yapıştırın veya CSV dosyasını seçin.\n"
                 "3. 'Analizi Başlat' butonuna bastığınızda Gauss çan eğrisi çizilir; prosesin firesiz çalışıp çalışmadığı (Cp/Cpk) ve takım aşınması anında teşhis edilir.",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLORS["text_secondary"],
            justify="left"
        )
        self.lbl_guide.pack(anchor="w", padx=18, pady=(0, 10))

        # 2. Ana Gövde
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        # Sol Panel (Veri Girişi)
        self.left_panel = ctk.CTkFrame(self.content, fg_color=COLORS["card_bg"], corner_radius=14, width=340)
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))
        self.left_panel.pack_propagate(False)

        # Sağ Panel (Grafik ve Metrikler)
        self.right_panel = ctk.CTkFrame(self.content, fg_color=COLORS["card_bg"], corner_radius=14)
        self.right_panel.pack(side="left", fill="both", expand=True)

        self._build_inputs(self.left_panel)
        self._build_display(self.right_panel)

        self._plot_empty_state()

    def _build_inputs(self, parent):
        self.lbl_in_t = ctk.CTkLabel(
            parent,
            text="Spesifikasyon ve Ölçüm Verisi",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["accent_cyan"]
        )
        self.lbl_in_t.pack(anchor="w", padx=16, pady=(12, 6))

        # Parça Adı
        self.lbl_p_name = ctk.CTkLabel(parent, text="İş Parçası Adı / Kodu:", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_p_name.pack(anchor="w", padx=16)
        self.entry_part = ctk.CTkEntry(parent, placeholder_text="Örn: CNC Torna Şaft Çapı (Ø25)", corner_radius=8, height=36, font=ctk.CTkFont(family="Segoe UI", size=10))
        self.entry_part.pack(fill="x", padx=16, pady=(2, 6))

        # Nominal Ölçü
        self.lbl_p_nom = ctk.CTkLabel(parent, text="Nominal Hedef Ölçü (mm):", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_p_nom.pack(anchor="w", padx=16)
        self.entry_nominal = ctk.CTkEntry(parent, placeholder_text="Örn: 25.000", corner_radius=8, height=36, font=ctk.CTkFont(family="Segoe UI", size=10))
        self.entry_nominal.pack(fill="x", padx=16, pady=(2, 6))

        # Tolerans Limitleri
        self.grid_tol = ctk.CTkFrame(parent, fg_color="transparent")
        self.grid_tol.pack(fill="x", padx=16, pady=(0, 6))

        self.lbl_lsl_t = ctk.CTkLabel(self.grid_tol, text="Alt Limit (LSL - mm):", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_lsl_t.grid(row=0, column=0, sticky="w")
        self.lbl_usl_t = ctk.CTkLabel(self.grid_tol, text="Üst Limit (USL - mm):", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_usl_t.grid(row=0, column=1, sticky="w", padx=(10, 0))

        self.entry_lsl = ctk.CTkEntry(self.grid_tol, placeholder_text="Örn: 24.950", corner_radius=8, height=36, width=140, font=ctk.CTkFont(family="Segoe UI", size=10))
        self.entry_lsl.grid(row=1, column=0, sticky="we", pady=(2, 0))

        self.entry_usl = ctk.CTkEntry(self.grid_tol, placeholder_text="Örn: 25.050", corner_radius=8, height=36, width=140, font=ctk.CTkFont(family="Segoe UI", size=10))
        self.entry_usl.grid(row=1, column=1, sticky="we", padx=(10, 0), pady=(2, 0))

        # CSV Butonu
        self.btn_csv = ctk.CTkButton(
            parent,
            text="📁 Ölçüm CSV Dosyası Yükle",
            corner_radius=8,
            height=34,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color=COLORS["entry_bg"],
            text_color=COLORS["text_primary"],
            hover_color=COLORS["sidebar_hover"],
            command=self._on_load_csv
        )
        self.btn_csv.pack(fill="x", padx=16, pady=(6, 2))

        self.lbl_csv_status = ctk.CTkLabel(
            parent,
            text="CSV seçilmedi (Manuel giriş yapılabilir)",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color=COLORS["text_secondary"]
        )
        self.lbl_csv_status.pack(anchor="w", padx=16)

        # Manuel Veri Kutusu
        self.lbl_txt_t = ctk.CTkLabel(parent, text="Ölçülen Parça Değerleri (satır satır):", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_txt_t.pack(anchor="w", padx=16, pady=(4, 2))

        self.txt_data = ctk.CTkTextbox(parent, corner_radius=10, height=110, font=ctk.CTkFont(family="Consolas", size=11))
        self.txt_data.pack(fill="x", padx=16, pady=(0, 8))

        # Analiz Butonu
        self.btn_run = ctk.CTkButton(
            parent,
            text="⚡ Analizi Başlat & Raporla",
            corner_radius=10,
            height=42,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            text_color="#ffffff",
            command=self._on_run_analysis
        )
        self.btn_run.pack(fill="x", padx=16, pady=(2, 12))

    def _build_display(self, parent):
        # Üst Araç Çubuğu
        self.action_bar = ctk.CTkFrame(parent, fg_color="transparent")
        self.action_bar.pack(fill="x", padx=14, pady=(10, 6))

        self.lbl_chart_t = ctk.CTkLabel(
            self.action_bar,
            text="Ölçüm Dağılımı ve Proses Yeterliliği",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["accent_cyan"]
        )
        self.lbl_chart_t.pack(side="left")

        # PNG İndir Butonu (Yüksek Kontrastlı ve Net)
        self.btn_png = ctk.CTkButton(
            self.action_bar,
            text="📥 Grafiği PNG İndir",
            corner_radius=8,
            height=34,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color=COLORS["btn_png"],
            hover_color=COLORS["btn_png_hover"],
            text_color="#ffffff",
            command=self._on_export_png
        )
        self.btn_png.pack(side="right", padx=(6, 0))

        # PDF Raporu Oluştur Butonu (Yüksek Kontrastlı Zümrüt Yeşili)
        self.btn_pdf = ctk.CTkButton(
            self.action_bar,
            text="📄 Resmi PDF Raporu Oluştur",
            corner_radius=8,
            height=34,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color=COLORS["btn_pdf"],
            hover_color=COLORS["btn_pdf_hover"],
            text_color="#ffffff",
            command=self._on_export_pdf
        )
        self.btn_pdf.pack(side="right")

        # Matplotlib Tuvali
        self.chart_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color=COLORS["entry_bg"])
        self.chart_frame.pack(fill="both", expand=True, padx=14, pady=4)

        self.fig = Figure(figsize=(7.5, 3.8), dpi=100, facecolor=COLORS["plot_card"])
        self.ax = self.fig.add_subplot(111, facecolor=COLORS["plot_bg"])
        self.fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)

        # Alt Metrik Kartları
        self.metrics_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.metrics_frame.pack(fill="x", padx=14, pady=8)

        self.cards = {}
        self.cards["cp"] = self._create_metric_card(self.metrics_frame, "Cp (Potansiyel)", "--")
        self.cards["cpk"] = self._create_metric_card(self.metrics_frame, "Cpk (Fiili)", "--")
        self.cards["mean"] = self._create_metric_card(self.metrics_frame, "Ortalama (X̄)", "--")
        self.cards["std"] = self._create_metric_card(self.metrics_frame, "Std. Sapma (s)", "--")
        self.cards["ppm"] = self._create_metric_card(self.metrics_frame, "Fire Tahmini", "-- PPM")

        # Teşhis Kutusu
        self.diag_card = ctk.CTkFrame(parent, fg_color=COLORS["entry_bg"], corner_radius=10)
        self.diag_card.pack(fill="x", padx=14, pady=(0, 10))

        self.lbl_diag = ctk.CTkLabel(
            self.diag_card,
            text="Analiz bekleniyor. Soldaki panelden değerleri girip 'Analizi Başlat' butonuna basınız.",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLORS["text_secondary"],
            anchor="w",
            justify="left"
        )
        self.lbl_diag.pack(fill="x", padx=12, pady=8)

    def _create_metric_card(self, parent, title, val):
        box = ctk.CTkFrame(parent, fg_color=COLORS["entry_bg"], corner_radius=10)
        box.pack(side="left", fill="both", expand=True, padx=3)

        lbl_t = ctk.CTkLabel(box, text=title, font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"), text_color=COLORS["text_secondary"])
        lbl_t.pack(anchor="w", padx=10, pady=(6, 0))

        lbl_v = ctk.CTkLabel(box, text=val, font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color=COLORS["text_primary"])
        lbl_v.pack(anchor="w", padx=10, pady=(0, 6))

        return (box, lbl_t, lbl_v)

    def _plot_empty_state(self):
        self.ax.clear()
        self.ax.set_facecolor(COLORS["plot_bg"])
        self.fig.patch.set_facecolor(COLORS["plot_card"])
        self.ax.tick_params(colors=COLORS["text_secondary"], labelsize=8)
        for spine in self.ax.spines.values():
            spine.set_color(COLORS["card_border"])

        self.ax.text(
            0.5, 0.5,
            "[ Analiz Bekleniyor ]\n\nSoldaki panelden nominal ölçü, tolerans ve ölçüm verilerini giriniz\nveya CSV yükleyip 'Analizi Başlat' butonuna basınız.",
            transform=self.ax.transAxes,
            ha="center", va="center",
            fontsize=11,
            color=COLORS["text_secondary"],
            family="Segoe UI"
        )
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.fig.tight_layout()
        self.canvas.draw()

    def _on_load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Dosyaları", "*.csv"), ("Tüm Dosyalar", "*.*")])
        if path:
            try:
                df = pd.read_csv(path)
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) == 0:
                    messagebox.showerror("Hata", "CSV dosyasında sayısal ölçüm sütunu bulunamadı.")
                    return
                vals = df[numeric_cols[0]].dropna().tolist()
                self.txt_data.delete("1.0", "end")
                self.txt_data.insert("1.0", "\n".join([f"{v:.4f}" for v in vals]))
                self.lbl_csv_status.configure(text=f"Yüklendi: {len(vals)} numune ({numeric_cols[0]})", text_color=COLORS["accent_success"])
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya okunamadı: {str(e)}")

    def _on_run_analysis(self):
        val_nom = self.entry_nominal.get().strip()
        val_usl = self.entry_usl.get().strip()
        val_lsl = self.entry_lsl.get().strip()
        raw_text = self.txt_data.get("1.0", "end").strip()

        if not val_nom or not val_usl or not val_lsl:
            messagebox.showwarning("Eksik Bilgi", "Lütfen Nominal ölçü, USL ve LSL tolerans sınırlarını giriniz.")
            return

        if not raw_text:
            messagebox.showwarning("Eksik Veri", "Lütfen ölçüm kutusuna en az 2 adet değer girin veya bir CSV dosyası yükleyin.")
            return

        try:
            nominal = float(val_nom)
            usl = float(val_usl)
            lsl = float(val_lsl)
        except ValueError:
            messagebox.showerror("Hata", "Tolerans ve nominal değerler geçerli sayı olmalıdır.")
            return

        lines = [line.strip().replace(",", ".") for line in raw_text.splitlines() if line.strip()]
        try:
            data = [float(v) for v in lines]
        except ValueError:
            messagebox.showerror("Hata", "Ölçüm kutusundaki satırlar sayısal olmalıdır.")
            return

        if len(data) < 2:
            messagebox.showerror("Hata", "Analiz için en az 2 adet ölçüm verisi gereklidir.")
            return

        try:
            res = SPCEngine.analyze(data, nominal=nominal, usl=usl, lsl=lsl)
            self.current_result = res
            self.current_data = data
        except Exception as e:
            messagebox.showerror("Analiz Hatası", str(e))
            return

        self.cards["cp"][2].configure(text=f"{res.cp:.3f}")
        cpk_col = COLORS["accent_success"] if res.cpk >= 1.33 else COLORS["accent_danger"]
        self.cards["cpk"][2].configure(text=f"{res.cpk:.3f}", text_color=cpk_col)
        self.cards["mean"][2].configure(text=f"{res.mean:.4f} mm")
        self.cards["std"][2].configure(text=f"{res.std_dev:.4f} mm")
        self.cards["ppm"][2].configure(text=f"{res.ppm_total:.1f} PPM")
        self.lbl_diag.configure(text=f"TEŞHİS: {res.diagnosis_note}  |  DURUM: {res.status.value}", text_color=COLORS["accent_cyan"])

        self._plot_graph(data, res)

    def _plot_graph(self, data, res: SPCResult):
        self.ax.clear()
        arr = np.array(data)

        self.ax.set_facecolor(COLORS["plot_bg"])
        self.fig.patch.set_facecolor(COLORS["plot_card"])
        self.ax.tick_params(colors=COLORS["text_secondary"], labelsize=9)
        for spine in self.ax.spines.values():
            spine.set_color(COLORS["card_border"])

        # Histogram
        self.ax.hist(
            arr, bins="auto", density=True, alpha=0.52,
            color=COLORS["accent_primary"], edgecolor=COLORS["accent_hover"], linewidth=1.2,
            label="Ölçüm Dağılımı"
        )

        # Gauss Eğrisi
        margin = res.tolerance_span * 0.3
        x_min = min(res.lsl - margin, float(np.min(arr)))
        x_max = max(res.usl + margin, float(np.max(arr)))
        x_axis = np.linspace(x_min, x_max, 600)
        pdf = stats.norm.pdf(x_axis, loc=res.mean, scale=res.std_dev)
        self.ax.plot(x_axis, pdf, color=COLORS["plot_text"], linewidth=2.2, label="Gauss Eğrisi")

        # Tolerans Dışı Fire Alanları
        x_below = x_axis[x_axis <= res.lsl]
        if len(x_below) > 0:
            self.ax.fill_between(x_below, 0, stats.norm.pdf(x_below, loc=res.mean, scale=res.std_dev), color=COLORS["accent_danger"], alpha=0.4, label="Alt Fire (< LSL)")

        x_above = x_axis[x_axis >= res.usl]
        if len(x_above) > 0:
            self.ax.fill_between(x_above, 0, stats.norm.pdf(x_above, loc=res.mean, scale=res.std_dev), color=COLORS["accent_danger"], alpha=0.4, label="Üst Fire (> USL)")

        # Limit Çizgileri
        self.ax.axvline(res.lsl, color=COLORS["accent_danger"], linestyle="--", linewidth=1.8, label=f"LSL ({res.lsl:.3f})")
        self.ax.axvline(res.usl, color=COLORS["accent_danger"], linestyle="--", linewidth=1.8, label=f"USL ({res.usl:.3f})")
        self.ax.axvline(res.nominal, color=COLORS["accent_success"], linestyle="-", linewidth=1.8, label=f"Nominal ({res.nominal:.3f})")
        self.ax.axvline(res.mean, color=COLORS["accent_warning"], linestyle=":", linewidth=2.0, label=f"Ortalama ({res.mean:.3f})")

        part_title = self.entry_part.get().strip() or "İş Parçası"
        self.ax.set_title(f"{part_title} - Proses Yeterlilik Dağılımı", fontsize=11, fontweight="bold", color=COLORS["plot_text"], pad=10)
        self.ax.legend(loc="upper right", fontsize=8, facecolor=COLORS["plot_card"], edgecolor=COLORS["card_border"], labelcolor=COLORS["plot_text"])
        self.ax.grid(True, linestyle="--", alpha=0.25, color=COLORS["plot_grid"])
        self.fig.tight_layout()
        self.canvas.draw()

    def _on_export_png(self):
        if not self.current_result:
            messagebox.showwarning("Uyarı", "Önce bir analiz çalıştırınız.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Görselleri", "*.png"), ("Tüm Dosyalar", "*.*")],
            initialfile="spc_yeterlilik_grafigi.png"
        )
        if save_path:
            try:
                self.fig.savefig(save_path, dpi=300, bbox_inches="tight", facecolor=COLORS["plot_card"])
                messagebox.showinfo("Başarılı", f"Grafik 300 DPI çözünürlükte kaydedildi:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Kayıt Hatası", str(e))

    def _on_export_pdf(self):
        if not self.current_result:
            messagebox.showwarning("Uyarı", "Önce bir analiz çalıştırınız.")
            return

        pdf_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Belgeleri", "*.pdf"), ("Tüm Dosyalar", "*.*")],
            initialfile="kalite_onay_sertifikasi.pdf"
        )
        if pdf_path:
            temp_img = os.path.join(os.path.dirname(pdf_path), "_temp_spc_plot.png")
            try:
                fig_pdf = Figure(figsize=(7.5, 3.5), dpi=150)
                ax_pdf = fig_pdf.add_subplot(111)
                arr = np.array(self.current_data)
                res = self.current_result

                ax_pdf.hist(arr, bins="auto", density=True, alpha=0.55, color="#0071e3", edgecolor="#0077ed")
                x_axis = np.linspace(min(res.lsl - 0.01, min(arr)), max(res.usl + 0.01, max(arr)), 500)
                ax_pdf.plot(x_axis, stats.norm.pdf(x_axis, loc=res.mean, scale=res.std_dev), color="#1d1d1f", linewidth=2)
                ax_pdf.axvline(res.lsl, color="#ff3b30", linestyle="--", linewidth=1.8, label="LSL")
                ax_pdf.axvline(res.usl, color="#ff3b30", linestyle="--", linewidth=1.8, label="USL")
                ax_pdf.axvline(res.nominal, color="#34c759", linestyle="-", linewidth=1.8, label="Nominal")
                ax_pdf.axvline(res.mean, color="#ff9f0a", linestyle=":", linewidth=2.0, label="Ortalama")
                ax_pdf.legend(loc="upper right", fontsize=8)
                ax_pdf.grid(True, linestyle="--", alpha=0.3)
                fig_pdf.tight_layout()
                fig_pdf.savefig(temp_img, dpi=150, bbox_inches="tight")

                rep_data = self.main_app.tabs["REPORTS"].get_report_metadata()

                QualityReportGenerator.generate_pdf(
                    result=res,
                    plot_image_path=temp_img,
                    output_pdf_path=pdf_path,
                    part_name=self.entry_part.get().strip() or "Hassas CNC Parçası",
                    company_name=rep_data.get("company", "Hassas Talaşlı İmalat Sanayi ve Ticaret A.Ş."),
                    operator_name=rep_data.get("operator", "Kalite Kontrol Sorumlusu"),
                    machine_code=rep_data.get("machine", "CNC-01")
                )

                if os.path.exists(temp_img):
                    os.remove(temp_img)

                messagebox.showinfo("Başarılı", f"Kurumsal Kalite Sertifikası Türkçe karakter desteğiyle PDF olarak kaydedildi:\n{pdf_path}")
            except Exception as e:
                messagebox.showerror("PDF Hatası", str(e))

    def load_limits_from_fit(self, part_name: str, nominal: float, usl: float, lsl: float):
        self.entry_part.delete(0, "end")
        self.entry_part.insert(0, part_name)

        self.entry_nominal.delete(0, "end")
        self.entry_nominal.insert(0, f"{nominal:.4f}")

        self.entry_usl.delete(0, "end")
        self.entry_usl.insert(0, f"{usl:.4f}")

        self.entry_lsl.delete(0, "end")
        self.entry_lsl.insert(0, f"{lsl:.4f}")

        spread = (usl - lsl) * 0.25
        mid = (usl + lsl) / 2.0
        sample_vals = np.random.normal(loc=mid, scale=spread * 0.4, size=40)
        self.txt_data.delete("1.0", "end")
        self.txt_data.insert("1.0", "\n".join([f"{v:.4f}" for v in sample_vals]))
        self.lbl_csv_status.configure(text="Tolerans sekmesinden aktarılan ölçüler yüklendi", text_color=COLORS["accent_cyan"])
        self._on_run_analysis()

    def apply_theme(self):
        self.configure(fg_color=COLORS["bg_app"])
        self.top_bar.configure(fg_color=COLORS["card_bg"])
        self.lbl_head.configure(text_color=COLORS["text_primary"])
        self.lbl_guide.configure(text_color=COLORS["text_secondary"])
        self.left_panel.configure(fg_color=COLORS["card_bg"])
        self.right_panel.configure(fg_color=COLORS["card_bg"])
        self.chart_frame.configure(fg_color=COLORS["entry_bg"])
        self.diag_card.configure(fg_color=COLORS["entry_bg"])

        self.lbl_in_t.configure(text_color=COLORS["accent_cyan"])
        self.lbl_p_name.configure(text_color=COLORS["text_primary"])
        self.lbl_p_nom.configure(text_color=COLORS["text_primary"])
        self.lbl_lsl_t.configure(text_color=COLORS["text_primary"])
        self.lbl_usl_t.configure(text_color=COLORS["text_primary"])
        self.lbl_csv_status.configure(text_color=COLORS["text_secondary"])
        self.lbl_txt_t.configure(text_color=COLORS["text_primary"])
        self.lbl_chart_t.configure(text_color=COLORS["accent_cyan"])
        self.lbl_diag.configure(text_color=COLORS["text_secondary"])

        self.entry_part.configure(fg_color=COLORS["entry_bg"], text_color=COLORS["text_primary"], border_color=COLORS["entry_border"])
        self.entry_nominal.configure(fg_color=COLORS["entry_bg"], text_color=COLORS["text_primary"], border_color=COLORS["entry_border"])
        self.entry_lsl.configure(fg_color=COLORS["entry_bg"], text_color=COLORS["text_primary"], border_color=COLORS["entry_border"])
        self.entry_usl.configure(fg_color=COLORS["entry_bg"], text_color=COLORS["text_primary"], border_color=COLORS["entry_border"])
        self.txt_data.configure(fg_color=COLORS["entry_bg"], text_color=COLORS["text_primary"], border_color=COLORS["entry_border"])
        self.btn_csv.configure(fg_color=COLORS["entry_bg"], hover_color=COLORS["sidebar_hover"], text_color=COLORS["text_primary"])
        self.btn_run.configure(fg_color=COLORS["accent_primary"], hover_color=COLORS["accent_hover"])
        self.btn_png.configure(fg_color=COLORS["btn_png"], hover_color=COLORS["btn_png_hover"], text_color="#ffffff")
        self.btn_pdf.configure(fg_color=COLORS["btn_pdf"], hover_color=COLORS["btn_pdf_hover"], text_color="#ffffff")

        for key, (box, lbl_t, lbl_v) in self.cards.items():
            box.configure(fg_color=COLORS["entry_bg"])
            lbl_t.configure(text_color=COLORS["text_secondary"])
            lbl_v.configure(text_color=COLORS["text_primary"])

        if self.current_result and len(self.current_data) > 0:
            self._plot_graph(self.current_data, self.current_result)
        else:
            self._plot_empty_state()
