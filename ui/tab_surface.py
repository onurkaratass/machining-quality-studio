"""
ui.tab_surface
~~~~~~~~~~~~~~
CustomTkinter tabanlı Yüzey Pürüzlülüğü (Ra, Rz), Uç Yarıçapı ve İlerleme Hesaplayıcısı.
"""

from tkinter import messagebox
import customtkinter as ctk
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from core.machining_calc import SurfaceRoughnessEngine, SurfaceRoughnessResult
from ui.styles import COLORS


class TabSurface(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color=COLORS["bg_app"], corner_radius=0)
        self.main_app = main_app
        self.current_result: SurfaceRoughnessResult = None
        self._build_ui()

    def _build_ui(self):
        # 1. Üst Başlık ve Rehber
        self.top_bar = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=12)
        self.top_bar.pack(fill="x", padx=16, pady=(12, 6))

        self.lbl_head = ctk.CTkLabel(
            self.top_bar,
            text="YÜZEY PÜRÜZLÜLÜĞÜ (Ra, Rz) VE KESİCİ UÇ YARIÇAPI ASİSTANI",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.lbl_head.pack(anchor="w", padx=18, pady=(10, 2))

        self.lbl_guide = ctk.CTkLabel(
            self.top_bar,
            text="💡 Nasıl Kullanılır?\n"
                 "1. Kesici uç köşe radyüsünü (rε) ve tezgâhtaki ilerleme değerini (f mm/dev) seçin.\n"
                 "2. 'Hesapla' butonuna bastığınızda teorik pürüzlülük (Rth), Ra ve ISO kalite sınıfı (N1-N12) belirlenir.\n"
                 "3. Teknik resimdeki hedef Ra değerini girerek tezgâha verilebilecek 'Maksimum Güvenli İlerleme' sınırını bulun ve tek tıkla kesme sekmesine aktarın.",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLORS["text_secondary"],
            justify="left"
        )
        self.lbl_guide.pack(anchor="w", padx=18, pady=(0, 10))

        # 2. Ana Gövde
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        self.left_card = ctk.CTkFrame(self.content, fg_color=COLORS["card_bg"], corner_radius=14, width=340)
        self.left_card.pack(side="left", fill="y", padx=(0, 10))
        self.left_card.pack_propagate(False)

        self.right_card = ctk.CTkFrame(self.content, fg_color=COLORS["card_bg"], corner_radius=14)
        self.right_card.pack(side="left", fill="both", expand=True)

        self._build_inputs(self.left_card)
        self._build_results(self.right_card)

        self._on_calculate()

    def _build_inputs(self, parent):
        self.lbl_in_t = ctk.CTkLabel(
            parent,
            text="Takım Ucu ve İlerleme",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["accent_cyan"]
        )
        self.lbl_in_t.pack(anchor="w", padx=16, pady=(12, 8))

        # Uç Yarıçapı (r_eps)
        self.lbl_re = ctk.CTkLabel(parent, text="Uç Köşe Radyüsü (rε - mm):", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_re.pack(anchor="w", padx=16)
        self.cb_reps = ctk.CTkOptionMenu(
            parent,
            values=["0.2 mm", "0.4 mm", "0.8 mm", "1.2 mm", "1.6 mm"],
            corner_radius=8,
            height=36,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=COLORS["dropdown_bg"],
            text_color=COLORS["dropdown_text"],
            button_color=COLORS["accent_primary"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["dropdown_menu"],
            dropdown_text_color=COLORS["dropdown_text"],
            dropdown_hover_color=COLORS["dropdown_hover"]
        )
        self.cb_reps.set("0.8 mm")
        self.cb_reps.pack(fill="x", padx=16, pady=(2, 10))

        # İlerleme (f)
        self.lbl_f = ctk.CTkLabel(parent, text="Mevcut İlerleme (f - mm/dev):", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_f.pack(anchor="w", padx=16)
        self.entry_feed = ctk.CTkEntry(parent, placeholder_text="Örn: 0.15", corner_radius=8, height=36, font=ctk.CTkFont(family="Segoe UI", size=11))
        self.entry_feed.insert(0, "0.15")
        self.entry_feed.pack(fill="x", padx=16, pady=(2, 10))

        # Hedef Ra
        self.lbl_tra = ctk.CTkLabel(parent, text="Hedeflenen Ra Sınırı (µm):", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_tra.pack(anchor="w", padx=16)
        self.entry_target_ra = ctk.CTkEntry(parent, placeholder_text="Örn: 1.6", corner_radius=8, height=36, font=ctk.CTkFont(family="Segoe UI", size=11))
        self.entry_target_ra.insert(0, "1.6")
        self.entry_target_ra.pack(fill="x", padx=16, pady=(2, 12))

        # Hesapla Butonu
        self.btn_calc = ctk.CTkButton(
            parent,
            text="⚡ Pürüzlülüğü Hesapla",
            corner_radius=10,
            height=40,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            text_color="#ffffff",
            command=self._on_calculate
        )
        self.btn_calc.pack(fill="x", padx=16, pady=(0, 14))

        # Kesme Modülüne Aktar Kutusu
        self.trans_box = ctk.CTkFrame(parent, fg_color=COLORS["entry_bg"], corner_radius=12)
        self.trans_box.pack(fill="x", padx=16, pady=(4, 12))

        self.lbl_trans_t = ctk.CTkLabel(self.trans_box, text="Kesme Modülü Entegrasyonu", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["accent_cyan"])
        self.lbl_trans_t.pack(anchor="w", padx=12, pady=(10, 2))

        self.lbl_max_f_info = ctk.CTkLabel(self.trans_box, text="Hedef Ra için Maks İlerleme: --", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_max_f_info.pack(anchor="w", padx=12, pady=(2, 6))

        self.btn_send_feed = ctk.CTkButton(
            self.trans_box,
            text="📤 Bu İlerlemeyi Kesme Modülüne Aktar",
            corner_radius=8,
            height=34,
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            fg_color="#0284c7",
            hover_color="#0369a1",
            text_color="#ffffff",
            command=self._on_send_feed
        )
        self.btn_send_feed.pack(fill="x", padx=12, pady=(0, 10))

    def _build_results(self, parent):
        # Üst Başlık
        self.lbl_res_t = ctk.CTkLabel(
            parent,
            text="Hesaplanan Yüzey Kalitesi ve Pürüzlülük Profili",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["accent_cyan"]
        )
        self.lbl_res_t.pack(anchor="w", padx=18, pady=(12, 6))

        # 3'lü Metrik Kartları
        self.grid_cards = ctk.CTkFrame(parent, fg_color="transparent")
        self.grid_cards.pack(fill="x", padx=18, pady=(0, 8))

        self.cards = {}
        self.cards["ra"] = self._make_card(self.grid_cards, "Aritmetik Pürüzlülük (Ra)", "-- µm", 0, 0, highlight=True)
        self.cards["rz"] = self._make_card(self.grid_cards, "Tepe-Çukur (Rz / Rth)", "-- µm", 0, 1)
        self.cards["grade"] = self._make_card(self.grid_cards, "ISO Yüzey Kalite Sınıfı", "--", 0, 2)

        # Matplotlib Profil Çizim Alanı
        self.chart_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color=COLORS["entry_bg"])
        self.chart_frame.pack(fill="both", expand=True, padx=18, pady=4)

        self.fig = Figure(figsize=(7.5, 3.5), dpi=100, facecolor=COLORS["plot_card"])
        self.ax = self.fig.add_subplot(111, facecolor=COLORS["plot_bg"])
        self.fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)

    def _make_card(self, parent, title, val, row, col, highlight=False):
        box = ctk.CTkFrame(parent, fg_color=COLORS["entry_bg"], corner_radius=12)
        box.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
        parent.grid_columnconfigure(col, weight=1)

        lbl_t = ctk.CTkLabel(box, text=title, font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"), text_color=COLORS["text_secondary"])
        lbl_t.pack(anchor="w", padx=12, pady=(8, 0))

        v_col = COLORS["accent_cyan"] if highlight else COLORS["text_primary"]
        lbl_v = ctk.CTkLabel(box, text=val, font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color=v_col)
        lbl_v.pack(anchor="w", padx=12, pady=(0, 8))

        return (box, lbl_t, lbl_v)

    def _on_calculate(self):
        try:
            r_str = self.cb_reps.get().replace("mm", "").strip()
            r_eps = float(r_str)
            feed = float(self.entry_feed.get().strip())
            target_ra = float(self.entry_target_ra.get().strip())

            res = SurfaceRoughnessEngine.calculate(feed, r_eps, target_ra)
            self.current_result = res

            self.cards["ra"][2].configure(text=f"{res.ra_um:.2f} µm")
            self.cards["rz"][2].configure(text=f"{res.rz_um:.2f} µm")
            self.cards["grade"][2].configure(text=res.iso_grade.split("(")[0].strip())

            self.lbl_max_f_info.configure(text=f"Hedef {target_ra:.1f} µm İçin Maks İlerleme: {res.max_feed_for_target_ra:.3f} mm/dev")

            # Mikro Yüzey Profil Grafiğini Çiz
            self._plot_profile(res)

        except Exception:
            pass

    def _plot_profile(self, res: SurfaceRoughnessResult):
        self.ax.clear()
        self.ax.set_facecolor(COLORS["plot_bg"])
        self.fig.patch.set_facecolor(COLORS["plot_card"])
        self.ax.tick_params(colors=COLORS["text_secondary"], labelsize=8)
        for spine in self.ax.spines.values():
            spine.set_color(COLORS["card_border"])

        # Teorik takım izi dalgaları (Kinematik Cusps)
        f = res.feed_mm_rev
        r = res.r_eps_mm
        x_points = np.linspace(-f, f * 3, 500)
        y_points = []
        for x in x_points:
            # Modulo x within feed tooth mark
            x_rel = (x % f) - (f / 2.0)
            # Dairesel kesici uç profili: y = r - sqrt(r^2 - x_rel^2) in um
            if abs(x_rel) < r:
                y = (r - np.sqrt(r**2 - x_rel**2)) * 1000.0
            else:
                y = res.rth_um
            y_points.append(y)

        y_arr = np.array(y_points)
        self.ax.plot(x_points, y_arr, color="#38bdf8", linewidth=2.0, label="Teorik Takım İzi Profili")
        self.ax.fill_between(x_points, 0, y_arr, color="#0284c7", alpha=0.3)

        # Ra Ortalama Çizgisi
        self.ax.axhline(res.ra_um, color="#10b981", linestyle="--", linewidth=1.6, label=f"Ra = {res.ra_um:.2f} µm")
        self.ax.axhline(res.rth_um, color="#ef4444", linestyle=":", linewidth=1.6, label=f"Rz/Rth = {res.rth_um:.2f} µm")

        self.ax.set_title(f"Kesici Uç İzi & Yüzey Pürüzlülüğü Modeli (rε={r} mm, f={f} mm/dev)", fontsize=10, fontweight="bold", color=COLORS["plot_text"], pad=8)
        self.ax.set_xlabel("İlerleme Ekseni (mm)", fontsize=8, color=COLORS["text_secondary"])
        self.ax.set_ylabel("Pürüzlülük Derinliği (µm)", fontsize=8, color=COLORS["text_secondary"])
        self.ax.legend(loc="upper right", fontsize=8, facecolor=COLORS["plot_card"], edgecolor=COLORS["card_border"], labelcolor=COLORS["plot_text"])
        self.ax.grid(True, linestyle="--", alpha=0.25, color=COLORS["plot_grid"])
        self.fig.tight_layout()
        self.canvas.draw()

    def _on_send_feed(self):
        if self.current_result:
            f_max = self.current_result.max_feed_for_target_ra
            mach_tab = self.main_app.tabs.get("MACHINING")
            if mach_tab:
                mach_tab.entry_f.delete(0, "end")
                mach_tab.entry_f.insert(0, f"{f_max:.3f}")
                mach_tab._on_calculate()
                messagebox.showinfo("Başarılı", f"Hesaplanan maksimum güvenli ilerleme ({f_max:.3f} mm/dev) Kesme Parametreleri sekmesine aktarıldı!")
                self.main_app.show_tab("MACHINING")

    def apply_theme(self):
        self.configure(fg_color=COLORS["bg_app"])
        self.top_bar.configure(fg_color=COLORS["card_bg"])
        self.lbl_head.configure(text_color=COLORS["text_primary"])
        self.lbl_guide.configure(text_color=COLORS["text_secondary"])

        self.left_card.configure(fg_color=COLORS["card_bg"])
        self.right_card.configure(fg_color=COLORS["card_bg"])
        self.chart_frame.configure(fg_color=COLORS["entry_bg"])
        self.trans_box.configure(fg_color=COLORS["entry_bg"])

        self.lbl_in_t.configure(text_color=COLORS["accent_cyan"])
        self.lbl_re.configure(text_color=COLORS["text_primary"])
        self.lbl_f.configure(text_color=COLORS["text_primary"])
        self.lbl_tra.configure(text_color=COLORS["text_primary"])
        self.lbl_res_t.configure(text_color=COLORS["accent_cyan"])
        self.lbl_trans_t.configure(text_color=COLORS["accent_cyan"])
        self.lbl_max_f_info.configure(text_color=COLORS["text_primary"])

        self.cb_reps.configure(
            fg_color=COLORS["dropdown_bg"],
            text_color=COLORS["dropdown_text"],
            button_color=COLORS["accent_primary"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["dropdown_menu"],
            dropdown_text_color=COLORS["dropdown_text"],
            dropdown_hover_color=COLORS["dropdown_hover"]
        )

        self.entry_feed.configure(fg_color=COLORS["entry_bg"], text_color=COLORS["text_primary"], border_color=COLORS["entry_border"])
        self.entry_target_ra.configure(fg_color=COLORS["entry_bg"], text_color=COLORS["text_primary"], border_color=COLORS["entry_border"])

        self.btn_calc.configure(fg_color=COLORS["accent_primary"], hover_color=COLORS["accent_hover"], text_color="#ffffff")
        self.btn_send_feed.configure(fg_color="#0284c7", hover_color="#0369a1", text_color="#ffffff")

        for key, (box, lbl_t, lbl_v) in self.cards.items():
            box.configure(fg_color=COLORS["entry_bg"])
            lbl_t.configure(text_color=COLORS["text_secondary"])
            val_c = COLORS["accent_cyan"] if (key == "ra") else COLORS["text_primary"]
            lbl_v.configure(text_color=val_c)

        if self.current_result:
            self._plot_profile(self.current_result)
