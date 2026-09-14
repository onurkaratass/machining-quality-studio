"""
ui.tab_gcode
~~~~~~~~~~~~
CustomTkinter tabanlı CNC G-Kod Simülatörü, Tezgâh Strok Sınır Denetleyicisi,
Takım Yolu Görselleştiricisi ve Hata Düzeltici Sekmesi.
"""

import os
from tkinter import filedialog, messagebox
import customtkinter as ctk
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from core.machining_calc import GCodeSimulator, GCodeAnalysisResult
from ui.styles import COLORS


class TabGCode(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color=COLORS["bg_app"], corner_radius=0)
        self.main_app = main_app
        self.current_result: GCodeAnalysisResult = None
        self._build_ui()

    def _build_ui(self):
        # 1. Üst Başlık ve Rehber Kutusu
        self.top_bar = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=12)
        self.top_bar.pack(fill="x", padx=16, pady=(12, 6))

        self.lbl_head = ctk.CTkLabel(
            self.top_bar,
            text="CNC G-KOD SİMÜLATÖRÜ, STROK DENETLEYİCİ VE HATA TEŞHİS MERKEZİ",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.lbl_head.pack(anchor="w", padx=18, pady=(10, 2))

        self.lbl_guide = ctk.CTkLabel(
            self.top_bar,
            text="💡 Nasıl Kullanılır?\n"
                 "1. Tezgâhınızın fiziksel çalışma sınırlarını (X/Y/Z strok limitleri) belirleyin.\n"
                 "2. CNC programınızı metin kutusuna yapıştırın veya '.nc / .tap / .gcode' dosyasını yükleyin.\n"
                 "3. 'Simülasyonu Başlat' butonuna bastığınızda takım yolu çizilir; eksen aşımı, fener mili kapalı kesme ve Z dalış çarpma riskleri anında listelenir.",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLORS["text_secondary"],
            justify="left",
            wraplength=1050
        )
        self.lbl_guide.pack(anchor="w", padx=18, pady=(0, 10))

        # 2. Ana Gövde
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        # Sol Panel (G-Kod ve Tezgâh Parametreleri)
        self.left_panel = ctk.CTkFrame(self.content, fg_color=COLORS["card_bg"], corner_radius=14, width=380)
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))
        self.left_panel.pack_propagate(False)

        # Sağ Panel (Takım Yolu Çizimi ve Teşhis Raporu)
        self.right_panel = ctk.CTkFrame(self.content, fg_color=COLORS["card_bg"], corner_radius=14)
        self.right_panel.pack(side="left", fill="both", expand=True)

        self._build_inputs(self.left_panel)
        self._build_display(self.right_panel)

        self._plot_empty_state()

    def _build_inputs(self, parent):
        self.lbl_in_t = ctk.CTkLabel(
            parent,
            text="Tezgâh Strok Limitleri & Kod Girişi",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["accent_cyan"]
        )
        self.lbl_in_t.pack(anchor="w", padx=16, pady=(12, 6))

        # Tezgâh Strok Limitleri (Geniş, Ferah ve Okunaklı Kutu)
        self.stroke_box = ctk.CTkFrame(parent, fg_color=COLORS["entry_bg"], corner_radius=12)
        self.stroke_box.pack(fill="x", padx=16, pady=(0, 10))

        lbl_s = ctk.CTkLabel(self.stroke_box, text="Tezgâh Fiziksel Strok Sınırları (Min / Max):", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["accent_cyan"])
        lbl_s.pack(anchor="w", padx=14, pady=(8, 4))

        grid_s = ctk.CTkFrame(self.stroke_box, fg_color="transparent")
        grid_s.pack(fill="x", padx=14, pady=(0, 10))

        # X Ekseni
        lbl_x = ctk.CTkLabel(grid_s, text="X Ekseni:", width=65, font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"], anchor="w")
        lbl_x.grid(row=0, column=0, pady=3)
        self.ent_xmin = ctk.CTkEntry(grid_s, width=80, height=30, font=ctk.CTkFont(family="Segoe UI", size=10))
        self.ent_xmin.insert(0, "-250")
        self.ent_xmin.grid(row=0, column=1, padx=2, pady=3)
        ctk.CTkLabel(grid_s, text="─", text_color=COLORS["text_secondary"]).grid(row=0, column=2, padx=4)
        self.ent_xmax = ctk.CTkEntry(grid_s, width=80, height=30, font=ctk.CTkFont(family="Segoe UI", size=10))
        self.ent_xmax.insert(0, "250")
        self.ent_xmax.grid(row=0, column=3, padx=2, pady=3)
        ctk.CTkLabel(grid_s, text="mm", font=ctk.CTkFont(family="Segoe UI", size=9), text_color=COLORS["text_secondary"]).grid(row=0, column=4, padx=4)

        # Y Ekseni
        lbl_y = ctk.CTkLabel(grid_s, text="Y Ekseni:", width=65, font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"], anchor="w")
        lbl_y.grid(row=1, column=0, pady=3)
        self.ent_ymin = ctk.CTkEntry(grid_s, width=80, height=30, font=ctk.CTkFont(family="Segoe UI", size=10))
        self.ent_ymin.insert(0, "-200")
        self.ent_ymin.grid(row=1, column=1, padx=2, pady=3)
        ctk.CTkLabel(grid_s, text="─", text_color=COLORS["text_secondary"]).grid(row=1, column=2, padx=4)
        self.ent_ymax = ctk.CTkEntry(grid_s, width=80, height=30, font=ctk.CTkFont(family="Segoe UI", size=10))
        self.ent_ymax.insert(0, "200")
        self.ent_ymax.grid(row=1, column=3, padx=2, pady=3)
        ctk.CTkLabel(grid_s, text="mm", font=ctk.CTkFont(family="Segoe UI", size=9), text_color=COLORS["text_secondary"]).grid(row=1, column=4, padx=4)

        # Z Ekseni
        lbl_z = ctk.CTkLabel(grid_s, text="Z Ekseni:", width=65, font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"], anchor="w")
        lbl_z.grid(row=2, column=0, pady=3)
        self.ent_zmin = ctk.CTkEntry(grid_s, width=80, height=30, font=ctk.CTkFont(family="Segoe UI", size=10))
        self.ent_zmin.insert(0, "-200")
        self.ent_zmin.grid(row=2, column=1, padx=2, pady=3)
        ctk.CTkLabel(grid_s, text="─", text_color=COLORS["text_secondary"]).grid(row=2, column=2, padx=4)
        self.ent_zmax = ctk.CTkEntry(grid_s, width=80, height=30, font=ctk.CTkFont(family="Segoe UI", size=10))
        self.ent_zmax.insert(0, "50")
        self.ent_zmax.grid(row=2, column=3, padx=2, pady=3)
        ctk.CTkLabel(grid_s, text="mm", font=ctk.CTkFont(family="Segoe UI", size=9), text_color=COLORS["text_secondary"]).grid(row=2, column=4, padx=4)

        # Dosya Yükle Butonu
        self.btn_load_nc = ctk.CTkButton(
            parent,
            text="📁 G-Kod Dosyası Yükle (.nc / .tap / .txt)",
            corner_radius=8,
            height=36,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color=COLORS["entry_bg"],
            text_color=COLORS["text_primary"],
            hover_color=COLORS["sidebar_hover"],
            command=self._on_load_gcode_file
        )
        self.btn_load_nc.pack(fill="x", padx=16, pady=(2, 6))

        # G-Kod Metin Kutusu
        self.lbl_code_t = ctk.CTkLabel(parent, text="G-Kod Editörü / Program Satırları:", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_code_t.pack(anchor="w", padx=16, pady=(2, 2))

        sample_gcode = (
            "O1001 (CNC HASSAS CEP FREZELEME)\n"
            "G21 G90 G40 G80 G49\n"
            "T01 M06 (PARMAK FREZE D12)\n"
            "G43 H01\n"
            "S2800 M03\n"
            "G00 X0 Y0 Z15.\n"
            "G00 Z2.\n"
            "G01 Z-3.0 F250\n"
            "G01 X80. Y0 F750\n"
            "G01 X80. Y60.\n"
            "G01 X0 Y60.\n"
            "G01 X0 Y0\n"
            "G00 Z25.\n"
            "M05\n"
            "M30\n"
        )
        self.txt_gcode = ctk.CTkTextbox(parent, corner_radius=10, height=170, font=ctk.CTkFont(family="Consolas", size=10))
        self.txt_gcode.insert("1.0", sample_gcode)
        self.txt_gcode.pack(fill="x", padx=16, pady=(0, 10))

        # Simülasyon Butonu
        self.btn_sim = ctk.CTkButton(
            parent,
            text="⚡ Simülasyonu Başlat & Denetle",
            corner_radius=10,
            height=42,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            text_color="#ffffff",
            command=self._on_run_simulation
        )
        self.btn_sim.pack(fill="x", padx=16, pady=(2, 12))

    def _build_display(self, parent):
        self.action_bar = ctk.CTkFrame(parent, fg_color="transparent")
        self.action_bar.pack(fill="x", padx=14, pady=(10, 6))

        self.lbl_chart_t = ctk.CTkLabel(
            self.action_bar,
            text="2D Takım Yolu Önizlemesi (XY Düzlemi & Tezgâh Limitleri)",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["accent_cyan"]
        )
        self.lbl_chart_t.pack(side="left")

        # Düzeltilmiş G-Kodu İndir
        self.btn_save_fixed = ctk.CTkButton(
            self.action_bar,
            text="💾 G-Kodu Dışa Aktar (.nc)",
            corner_radius=8,
            height=34,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="#0284c7",
            hover_color="#0369a1",
            text_color="#ffffff",
            command=self._on_export_gcode
        )
        self.btn_save_fixed.pack(side="right", padx=(6, 0))

        # PNG İndir
        self.btn_png = ctk.CTkButton(
            self.action_bar,
            text="📥 Takım Yolunu PNG İndir",
            corner_radius=8,
            height=34,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color=COLORS["btn_png"],
            hover_color=COLORS["btn_png_hover"],
            text_color="#ffffff",
            command=self._on_export_png
        )
        self.btn_png.pack(side="right")

        # Matplotlib Çizim Çerçevesi
        self.chart_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color=COLORS["entry_bg"])
        self.chart_frame.pack(fill="both", expand=True, padx=14, pady=4)

        self.fig = Figure(figsize=(7.5, 3.8), dpi=100, facecolor=COLORS["plot_card"])
        self.ax = self.fig.add_subplot(111, facecolor=COLORS["plot_bg"])
        self.fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)

        # 4'lü Metrik Kartları
        self.metrics_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.metrics_frame.pack(fill="x", padx=14, pady=6)

        self.cards = {}
        self.cards["cut"] = self._create_metric_card(self.metrics_frame, "Kesme Mesafesi", "-- m")
        self.cards["rapid"] = self._create_metric_card(self.metrics_frame, "Hızlı Hareket (G00)", "-- m")
        self.cards["time"] = self._create_metric_card(self.metrics_frame, "Tahmini Süre", "--:--")
        self.cards["tools"] = self._create_metric_card(self.metrics_frame, "Takımlar", "--")

        # Hata & Uyarı Teşhis Paneli
        self.diag_frame = ctk.CTkFrame(parent, fg_color=COLORS["entry_bg"], corner_radius=10)
        self.diag_frame.pack(fill="x", padx=14, pady=(0, 10))

        self.lbl_diag_head = ctk.CTkLabel(self.diag_frame, text="TEŞHİS VE GÜVENLİK RAPORU", font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"), text_color=COLORS["accent_cyan"])
        self.lbl_diag_head.pack(anchor="w", padx=12, pady=(6, 2))

        self.txt_errors = ctk.CTkTextbox(self.diag_frame, corner_radius=8, height=65, font=ctk.CTkFont(family="Segoe UI", size=9))
        self.txt_errors.insert("1.0", "G-kodunu girip 'Simülasyonu Başlat & Denetle' butonuna tıklayınız.")
        self.txt_errors.pack(fill="x", padx=12, pady=(0, 8))

    def _create_metric_card(self, parent, title, val):
        box = ctk.CTkFrame(parent, fg_color=COLORS["entry_bg"], corner_radius=10)
        box.pack(side="left", fill="both", expand=True, padx=3)

        lbl_t = ctk.CTkLabel(box, text=title, font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"), text_color=COLORS["text_secondary"])
        lbl_t.pack(anchor="w", padx=10, pady=(6, 0))

        lbl_v = ctk.CTkLabel(box, text=val, font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=COLORS["text_primary"])
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
            "[ Takım Yolu Bekleniyor ]\n\nG-Kodunu girip 'Simülasyonu Başlat' butonuna tıklayınız.",
            transform=self.ax.transAxes,
            ha="center", va="center",
            fontsize=10,
            color=COLORS["text_secondary"],
            family="Segoe UI"
        )
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.fig.tight_layout()
        self.canvas.draw()

    def _on_load_gcode_file(self):
        path = filedialog.askopenfilename(filetypes=[("CNC Dosyaları", "*.nc *.tap *.gcode *.txt"), ("Tüm Dosyalar", "*.*")])
        if path:
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                self.txt_gcode.delete("1.0", "end")
                self.txt_gcode.insert("1.0", content)
                self._on_run_simulation()
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya açılamadı: {e}")

    def _on_run_simulation(self):
        raw_code = self.txt_gcode.get("1.0", "end").strip()
        if not raw_code:
            messagebox.showwarning("Eksik Kod", "Lütfen bir G-Kodu giriniz.")
            return

        try:
            xmin = float(self.ent_xmin.get().strip())
            xmax = float(self.ent_xmax.get().strip())
            ymin = float(self.ent_ymin.get().strip())
            ymax = float(self.ent_ymax.get().strip())
            zmin = float(self.ent_zmin.get().strip())
            zmax = float(self.ent_zmax.get().strip())
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli tezgâh strok sınırları giriniz.")
            return

        sim = GCodeSimulator(x_limits=(xmin, xmax), y_limits=(ymin, ymax), z_limits=(zmin, zmax))
        res = sim.analyze(raw_code)
        self.current_result = res

        # Metrik Kartları
        self.cards["cut"][2].configure(text=f"{res.cut_distance_mm / 1000.0:.2f} m")
        self.cards["rapid"][2].configure(text=f"{res.rapid_distance_mm / 1000.0:.2f} m")

        # Süre: mm:ss
        mins = int(res.estimated_time_seconds // 60)
        secs = int(res.estimated_time_seconds % 60)
        self.cards["time"][2].configure(text=f"{mins:02d}:{secs:02d} dk")
        self.cards["tools"][2].configure(text=", ".join(res.tools_used) if res.tools_used else "T01")

        # Hata ve Uyarıları Listele
        self.txt_errors.delete("1.0", "end")
        diag_lines = []
        if res.errors:
            diag_lines.append(f"🔴 {len(res.errors)} ADET KRİTİK HATA TESPİT EDİLDİ:")
            for err in res.errors:
                diag_lines.append(f"  • {err}")
        else:
            diag_lines.append("✅ KUSURSUZ: Tezgâh strok aşımı, fener mili kapalı kesme veya ilerlemesiz kesme hatası bulunmadı.")

        if res.warnings:
            diag_lines.append(f"\n⚠️ {len(res.warnings)} ADET GÜVENLİK UYARISI:")
            for warn in res.warnings:
                diag_lines.append(f"  • {warn}")

        self.txt_errors.insert("1.0", "\n".join(diag_lines))

        # Takım Yolunu Çiz
        self._plot_toolpath(res, (xmin, xmax), (ymin, ymax))

    def _plot_toolpath(self, res: GCodeAnalysisResult, x_lim, y_lim):
        self.ax.clear()
        self.ax.set_facecolor(COLORS["plot_bg"])
        self.fig.patch.set_facecolor(COLORS["plot_card"])
        self.ax.tick_params(colors=COLORS["text_secondary"], labelsize=8)
        for spine in self.ax.spines.values():
            spine.set_color(COLORS["card_border"])

        # Tezgâh Strok Sınırları (Gri Kesikli Kutu)
        self.ax.plot(
            [x_lim[0], x_lim[1], x_lim[1], x_lim[0], x_lim[0]],
            [y_lim[0], y_lim[0], y_lim[1], y_lim[1], y_lim[0]],
            color="#ef4444" if res.errors else "#64748b",
            linestyle="--",
            linewidth=1.2,
            label="Tezgâh Çalışma Sınırı (Strok)"
        )

        for seg in res.segments:
            sx, sy, sz = seg.start_pos
            ex, ey, ez = seg.end_pos
            if seg.motion_type == "G00":
                self.ax.plot([sx, ex], [sy, ey], color="#f59e0b", linestyle=":", linewidth=1.1)
            else:
                self.ax.plot([sx, ex], [sy, ey], color="#38bdf8", linestyle="-", linewidth=1.5)

        # İş Sıfırı (X0, Y0)
        self.ax.plot(0, 0, marker="+", color="#10b981", markersize=12, markeredgewidth=2, label="İş Parçası Sıfırı (WCS)")

        self.ax.set_title(f"CNC Takım Yolu & Tezgâh Sınırları (Toplam: {len(res.segments)} hareket)", fontsize=10, fontweight="bold", color=COLORS["plot_text"], pad=8)
        self.ax.set_xlabel("X Ekseni (mm)", fontsize=8, color=COLORS["text_secondary"])
        self.ax.set_ylabel("Y Ekseni (mm)", fontsize=8, color=COLORS["text_secondary"])
        self.ax.legend(loc="upper right", fontsize=8, facecolor=COLORS["plot_card"], edgecolor=COLORS["card_border"], labelcolor=COLORS["plot_text"])
        self.ax.grid(True, linestyle="--", alpha=0.25, color=COLORS["plot_grid"])
        self.ax.set_aspect("equal", "datalim")
        self.fig.tight_layout()
        self.canvas.draw()

    def _on_export_png(self):
        if not self.current_result:
            messagebox.showwarning("Uyarı", "Önce simülasyonu çalıştırınız.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Görselleri", "*.png"), ("Tüm Dosyalar", "*.*")],
            initialfile="cnc_takim_yolu.png"
        )
        if save_path:
            try:
                self.fig.savefig(save_path, dpi=300, bbox_inches="tight", facecolor=COLORS["plot_card"])
                messagebox.showinfo("Başarılı", f"Takım yolu grafiği 300 DPI çözünürlükte kaydedildi:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Hata", str(e))

    def _on_export_gcode(self):
        raw_code = self.txt_gcode.get("1.0", "end").strip()
        if not raw_code:
            messagebox.showwarning("Uyarı", "Kaydedilecek kod bulunamadı.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".nc",
            filetypes=[("CNC G-Kodu", "*.nc *.tap *.txt"), ("Tüm Dosyalar", "*.*")],
            initialfile="islenmis_program.nc"
        )
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(raw_code)
                messagebox.showinfo("Başarılı", f"G-Kodu başarıyla kaydedildi:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Hata", str(e))

    def apply_theme(self):
        self.configure(fg_color=COLORS["bg_app"])
        self.top_bar.configure(fg_color=COLORS["card_bg"])
        self.lbl_head.configure(text_color=COLORS["text_primary"])
        self.lbl_guide.configure(text_color=COLORS["text_secondary"])

        self.left_panel.configure(fg_color=COLORS["card_bg"])
        self.right_panel.configure(fg_color=COLORS["card_bg"])
        self.stroke_box.configure(fg_color=COLORS["entry_bg"])
        self.chart_frame.configure(fg_color=COLORS["entry_bg"])
        self.diag_frame.configure(fg_color=COLORS["entry_bg"])

        self.lbl_in_t.configure(text_color=COLORS["accent_cyan"])
        self.lbl_code_t.configure(text_color=COLORS["text_primary"])
        self.lbl_chart_t.configure(text_color=COLORS["accent_cyan"])
        self.lbl_diag_head.configure(text_color=COLORS["accent_cyan"])

        for ent in [self.ent_xmin, self.ent_xmax, self.ent_ymin, self.ent_ymax, self.ent_zmin, self.ent_zmax]:
            ent.configure(fg_color=COLORS["entry_bg"], text_color=COLORS["text_primary"], border_color=COLORS["entry_border"])

        self.btn_load_nc.configure(fg_color=COLORS["entry_bg"], hover_color=COLORS["sidebar_hover"], text_color=COLORS["text_primary"])
        self.btn_sim.configure(fg_color=COLORS["accent_primary"], hover_color=COLORS["accent_hover"], text_color="#ffffff")
        self.btn_png.configure(fg_color=COLORS["btn_png"], hover_color=COLORS["btn_png_hover"], text_color="#ffffff")
        self.btn_save_fixed.configure(fg_color="#0284c7", hover_color="#0369a1", text_color="#ffffff")

        self.txt_gcode.configure(fg_color=COLORS["entry_bg"], text_color=COLORS["text_primary"])
        self.txt_errors.configure(fg_color=COLORS["entry_bg"], text_color=COLORS["text_primary"])

        for key, (box, lbl_t, lbl_v) in self.cards.items():
            box.configure(fg_color=COLORS["entry_bg"])
            lbl_t.configure(text_color=COLORS["text_secondary"])
            lbl_v.configure(text_color=COLORS["text_primary"])

        if self.current_result:
            try:
                xmin = float(self.ent_xmin.get())
                xmax = float(self.ent_xmax.get())
                ymin = float(self.ent_ymin.get())
                ymax = float(self.ent_ymax.get())
                self._plot_toolpath(self.current_result, (xmin, xmax), (ymin, ymax))
            except Exception:
                self._plot_empty_state()
        else:
            self._plot_empty_state()
