"""
ui.tab_thread
~~~~~~~~~~~~~
CustomTkinter tabanlı Standart Diş Açma, Kılavuz ve Ön Delik Matkabı Hesaplayıcısı.
"""

from tkinter import messagebox
import customtkinter as ctk

from core.machining_calc import ThreadEngine, ThreadInfo
from ui.styles import COLORS


class TabThread(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color=COLORS["bg_app"], corner_radius=0)
        self.main_app = main_app
        self.current_thread: ThreadInfo = None
        self._build_ui()

    def _build_ui(self):
        # 1. Üst Başlık ve Rehber
        self.top_bar = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=12)
        self.top_bar.pack(fill="x", padx=16, pady=(12, 6))

        self.lbl_head = ctk.CTkLabel(
            self.top_bar,
            text="STANDART DİŞ AÇMA, KILAVUZ VE ÖN DELİK MATKABI ASİSTANI",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.lbl_head.pack(anchor="w", padx=18, pady=(10, 2))

        self.lbl_guide = ctk.CTkLabel(
            self.top_bar,
            text="💡 Nasıl Kullanılır?\n"
                 "1. Diş türünü (Metrik Kaba, İnce veya Gaz Dişi) ve anma diş ölçüsünü (örn: M8, M12) seçin.\n"
                 "2. Kılavuz çekmeden önce delinmesi gereken kesin 'Ön Delik Matkap Çapı'nı (D_drill) ve hatveyi (P) anında görün.\n"
                 "3. Fener mili devrini (RPM) girerek CNC tezgâhında rijit kılavuz (Rigid Tapping) için gereken senkronize ilerleme hızını (F = N x P) hesaplayın ve aktarın.",
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
            text="Diş ve Kılavuz Parametreleri",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["accent_cyan"]
        )
        self.lbl_in_t.pack(anchor="w", padx=16, pady=(12, 8))

        # Diş Standardı
        self.lbl_std = ctk.CTkLabel(parent, text="Diş Serisi Standardı:", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_std.pack(anchor="w", padx=16)

        self.cb_series = ctk.CTkOptionMenu(
            parent,
            values=["Metrik Standart (Kaba)", "Metrik İnce Diş", "Gaz / Boru Dişi (G / BSP)"],
            corner_radius=8,
            height=36,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=COLORS["dropdown_bg"],
            text_color=COLORS["dropdown_text"],
            button_color=COLORS["accent_primary"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["dropdown_menu"],
            dropdown_text_color=COLORS["dropdown_text"],
            dropdown_hover_color=COLORS["dropdown_hover"],
            command=self._on_series_change
        )
        self.cb_series.set("Metrik Standart (Kaba)")
        self.cb_series.pack(fill="x", padx=16, pady=(2, 10))

        # Diş Ölçüsü
        self.lbl_size = ctk.CTkLabel(parent, text="Diş Anma Ölçüsü:", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_size.pack(anchor="w", padx=16)

        coarse_list = list(ThreadEngine.METRIC_COARSE.keys())
        self.cb_thread = ctk.CTkOptionMenu(
            parent,
            values=coarse_list,
            corner_radius=8,
            height=36,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=COLORS["dropdown_bg"],
            text_color=COLORS["dropdown_text"],
            button_color=COLORS["accent_primary"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["dropdown_menu"],
            dropdown_text_color=COLORS["dropdown_text"],
            dropdown_hover_color=COLORS["dropdown_hover"],
            command=lambda v: self._on_calculate()
        )
        self.cb_thread.set("M8")
        self.cb_thread.pack(fill="x", padx=16, pady=(2, 10))

        # Fener Mili Devri (RPM)
        self.lbl_rpm = ctk.CTkLabel(parent, text="CNC Kılavuz Devri (N - RPM):", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_rpm.pack(anchor="w", padx=16)
        self.entry_rpm = ctk.CTkEntry(parent, placeholder_text="Örn: 400", corner_radius=8, height=36, font=ctk.CTkFont(family="Segoe UI", size=11))
        self.entry_rpm.insert(0, "400")
        self.entry_rpm.pack(fill="x", padx=16, pady=(2, 12))

        # Hesapla Butonu
        self.btn_calc = ctk.CTkButton(
            parent,
            text="⚡ Diş Bilgilerini Getir",
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

        self.lbl_trans_t = ctk.CTkLabel(self.trans_box, text="Rijit Kılavuz Senkronizasyonu", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["accent_cyan"])
        self.lbl_trans_t.pack(anchor="w", padx=12, pady=(10, 2))

        self.lbl_sync_f = ctk.CTkLabel(self.trans_box, text="İlerleme F = N x P : -- mm/dak", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_sync_f.pack(anchor="w", padx=12, pady=(2, 6))

        self.btn_send_feed = ctk.CTkButton(
            self.trans_box,
            text="📤 Kılavuz İlerlemesini Aktar",
            corner_radius=8,
            height=34,
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            fg_color="#0284c7",
            hover_color="#0369a1",
            text_color="#ffffff",
            command=self._on_send_sync_feed
        )
        self.btn_send_feed.pack(fill="x", padx=12, pady=(0, 10))

    def _build_results(self, parent):
        self.lbl_res_t = ctk.CTkLabel(
            parent,
            text="Standart Diş Geometrisi ve İmalat Tablosu",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["accent_cyan"]
        )
        self.lbl_res_t.pack(anchor="w", padx=18, pady=(12, 6))

        # 4 Büyük Metrik Kartı
        self.grid_cards = ctk.CTkFrame(parent, fg_color="transparent")
        self.grid_cards.pack(fill="x", padx=18, pady=(0, 10))

        self.cards = {}
        self.cards["drill"] = self._make_card(self.grid_cards, "Ön Delik Matkabı (D_drill)", "-- mm", 0, 0, highlight=True)
        self.cards["pitch"] = self._make_card(self.grid_cards, "Hatve / Diş Adımı (P)", "-- mm", 0, 1)
        self.cards["depth"] = self._make_card(self.grid_cards, "Diş Derinliği (h3)", "-- mm", 1, 0)
        self.cards["feed"] = self._make_card(self.grid_cards, "Rijit Kılavuz İlerlemesi (F)", "-- mm/dak", 1, 1, highlight=True)

        # Bilgi ve Standart Tablosu Kartı
        self.info_card = ctk.CTkFrame(parent, fg_color=COLORS["entry_bg"], corner_radius=12)
        self.info_card.pack(fill="both", expand=True, padx=18, pady=(4, 14))

        self.lbl_info_head = ctk.CTkLabel(self.info_card, text="İMALAT TAVSİYELERİ VE DİŞ BİLGİLERİ", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["accent_cyan"])
        self.lbl_info_head.pack(anchor="w", padx=16, pady=(12, 4))

        self.txt_thread_info = ctk.CTkTextbox(self.info_card, corner_radius=8, font=ctk.CTkFont(family="Consolas", size=11))
        self.txt_thread_info.pack(fill="both", expand=True, padx=14, pady=(0, 12))

    def _make_card(self, parent, title, val, row, col, highlight=False):
        box = ctk.CTkFrame(parent, fg_color=COLORS["entry_bg"], corner_radius=12)
        box.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
        parent.grid_columnconfigure(col, weight=1)

        lbl_t = ctk.CTkLabel(box, text=title, font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"), text_color=COLORS["text_secondary"])
        lbl_t.pack(anchor="w", padx=14, pady=(10, 0))

        v_col = COLORS["accent_cyan"] if highlight else COLORS["text_primary"]
        lbl_v = ctk.CTkLabel(box, text=val, font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"), text_color=v_col)
        lbl_v.pack(anchor="w", padx=14, pady=(0, 10))

        return (box, lbl_t, lbl_v)

    def _on_series_change(self, choice: str):
        if "Kaba" in choice:
            vals = list(ThreadEngine.METRIC_COARSE.keys())
        elif "İnce" in choice:
            vals = list(ThreadEngine.METRIC_FINE.keys())
        else:
            vals = list(ThreadEngine.PIPE_BSP.keys())

        self.cb_thread.configure(values=vals)
        self.cb_thread.set(vals[0])
        self._on_calculate()

    def _on_calculate(self):
        try:
            th_name = self.cb_thread.get().strip()
            th = ThreadEngine.get_thread(th_name)
            self.current_thread = th

            rpm = float(self.entry_rpm.get().strip() or "400")
            sync_feed = rpm * th.pitch_mm

            self.cards["drill"][2].configure(text=f"Ø{th.drill_dia_mm:.2f} mm")
            self.cards["pitch"][2].configure(text=f"{th.pitch_mm:.3f} mm")
            self.cards["depth"][2].configure(text=f"{th.depth_mm:.3f} mm")
            self.cards["feed"][2].configure(text=f"{sync_feed:.1f} mm/dak")

            self.lbl_sync_f.configure(text=f"İlerleme F = {rpm:.0f} x {th.pitch_mm:.3f} = {sync_feed:.1f} mm/dak")

            lines = [
                f"═" * 58,
                f"  DİŞ SPESİFİKASYONU: {th.designation} ({th.thread_type})",
                f"═" * 58,
                f" • Anma Dış Çapı (Nominal)     : {th.nominal_dia_mm:.3f} mm",
                f" • Hatve / Diş Adımı (P)       : {th.pitch_mm:.3f} mm",
                f" • Ön Delik Matkap Çapı        : Ø{th.drill_dia_mm:.2f} mm  (H7 delik toleransı önerilir)",
                f" • Teorik Diş Profil Derinliği : {th.depth_mm:.3f} mm",
                f"─" * 58,
                f" CNC RİJİT KILAVUZ (G84 / M29) PARAMETRELERİ:",
                f" • Fener Mili Devri (S)        : {rpm:.0f} RPM",
                f" • Senkronize İlerleme Hızı (F): {sync_feed:.1f} mm/dak (F = S x Hatve)",
                f"═" * 58,
                f" İMALAT VE TEZGAH GÜVENLİK TAVSİYELERİ:",
                f" 1. Ön deliği delerken pah kırmayı (min 0.5 x Hatve) unutmayınız.",
                f" 2. Kılavuz çekerken uygun kılavuz çekme yağı / kesme sıvısı (M08) kullanınız.",
                f" 3. Kör deliklerde talaşı dışarı atan helis kanallı kılavuz tercih ediniz.",
            ]
            self.txt_thread_info.delete("1.0", "end")
            self.txt_thread_info.insert("1.0", "\n".join(lines))

        except Exception:
            pass

    def _on_send_sync_feed(self):
        if self.current_thread:
            try:
                rpm = float(self.entry_rpm.get().strip() or "400")
                sync_feed = rpm * self.current_thread.pitch_mm
                mach_tab = self.main_app.tabs.get("MACHINING")
                if mach_tab:
                    mach_tab.entry_d.delete(0, "end")
                    mach_tab.entry_d.insert(0, f"{self.current_thread.nominal_dia_mm:.2f}")
                    mach_tab.entry_f.delete(0, "end")
                    mach_tab.entry_f.insert(0, f"{self.current_thread.pitch_mm:.3f}")
                    mach_tab.entry_vc.delete(0, "end")
                    # Vc = (pi * D * N) / 1000
                    vc = (3.14159 * self.current_thread.nominal_dia_mm * rpm) / 1000.0
                    mach_tab.entry_vc.insert(0, f"{vc:.1f}")
                    mach_tab._on_calculate()
                    messagebox.showinfo("Başarılı", f"Kılavuz parametreleri ({rpm:.0f} RPM, Hatve {self.current_thread.pitch_mm} mm) Kesme sekmesine aktarıldı!")
                    self.main_app.show_tab("MACHINING")
            except Exception as e:
                messagebox.showerror("Hata", str(e))

    def apply_theme(self):
        self.configure(fg_color=COLORS["bg_app"])
        self.top_bar.configure(fg_color=COLORS["card_bg"])
        self.lbl_head.configure(text_color=COLORS["text_primary"])
        self.lbl_guide.configure(text_color=COLORS["text_secondary"])

        self.left_card.configure(fg_color=COLORS["card_bg"])
        self.right_card.configure(fg_color=COLORS["card_bg"])
        self.info_card.configure(fg_color=COLORS["entry_bg"])
        self.trans_box.configure(fg_color=COLORS["entry_bg"])

        self.lbl_in_t.configure(text_color=COLORS["accent_cyan"])
        self.lbl_std.configure(text_color=COLORS["text_primary"])
        self.lbl_size.configure(text_color=COLORS["text_primary"])
        self.lbl_rpm.configure(text_color=COLORS["text_primary"])
        self.lbl_res_t.configure(text_color=COLORS["accent_cyan"])
        self.lbl_trans_t.configure(text_color=COLORS["accent_cyan"])
        self.lbl_sync_f.configure(text_color=COLORS["text_primary"])
        self.lbl_info_head.configure(text_color=COLORS["accent_cyan"])

        for cb in [self.cb_series, self.cb_thread]:
            cb.configure(
                fg_color=COLORS["dropdown_bg"],
                text_color=COLORS["dropdown_text"],
                button_color=COLORS["accent_primary"],
                button_hover_color=COLORS["accent_hover"],
                dropdown_fg_color=COLORS["dropdown_menu"],
                dropdown_text_color=COLORS["dropdown_text"],
                dropdown_hover_color=COLORS["dropdown_hover"]
            )

        self.entry_rpm.configure(fg_color=COLORS["entry_bg"], text_color=COLORS["text_primary"], border_color=COLORS["entry_border"])
        self.btn_calc.configure(fg_color=COLORS["accent_primary"], hover_color=COLORS["accent_hover"], text_color="#ffffff")
        self.btn_send_feed.configure(fg_color="#0284c7", hover_color="#0369a1", text_color="#ffffff")
        self.txt_thread_info.configure(fg_color=COLORS["entry_bg"], text_color=COLORS["text_primary"])

        for key, (box, lbl_t, lbl_v) in self.cards.items():
            box.configure(fg_color=COLORS["entry_bg"])
            lbl_t.configure(text_color=COLORS["text_secondary"])
            v_col = COLORS["accent_cyan"] if (key in ["drill", "feed"]) else COLORS["text_primary"]
            lbl_v.configure(text_color=v_col)
