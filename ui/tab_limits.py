"""
ui.tab_limits
~~~~~~~~~~~~~
CustomTkinter tabanlı ISO 286 Tolerans ve Geçme Analizörü Arayüz Sekmesi.
"""

from tkinter import messagebox
import customtkinter as ctk

from core.limits_fits import calculate_iso_fit, FitResult, FitType
from ui.styles import COLORS


class TabLimitsFits(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color=COLORS["bg_app"], corner_radius=0)
        self.main_app = main_app
        self.current_result: FitResult = None
        self._build_ui()

    def _build_ui(self):
        # 1. Üst Başlık ve Rehber Kutusu
        self.top_bar = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=12)
        self.top_bar.pack(fill="x", padx=16, pady=(12, 6))

        self.lbl_head = ctk.CTkLabel(
            self.top_bar,
            text="ISO 286 STANDART DELİK - MİL TOLERANS VE GEÇME HESAPLAYICISI",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.lbl_head.pack(anchor="w", padx=18, pady=(10, 2))

        self.lbl_guide = ctk.CTkLabel(
            self.top_bar,
            text="💡 Nasıl Kullanılır?\n"
                 "1. Parçanın anma çapını (D) girin; ardından delik (örn: H7) ve mil (örn: g6, p6) tolerans sınıflarını seçin.\n"
                 "2. 'Geçmeyi Hesapla' butonuna basarak mikrometre (µm) ve mm cinsinden boşluk veya sıkılık sınırlarını görün.\n"
                 "3. 'SPC'ye Aktar' butonuyla bu sınırları doğrudan kalite modülüne gönderip üretim toleranslarını analiz edin.",
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
            text="Geçme Parametreleri",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["accent_cyan"]
        )
        self.lbl_in_t.pack(anchor="w", padx=16, pady=(12, 8))

        # Nominal Çap
        self.lbl_d_t = ctk.CTkLabel(parent, text="Nominal Anma Çapı (D - mm):", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_d_t.pack(anchor="w", padx=16)
        self.entry_d = ctk.CTkEntry(parent, placeholder_text="Örn: 30.000", corner_radius=8, height=38, font=ctk.CTkFont(family="Segoe UI", size=11))
        self.entry_d.insert(0, "30.000")
        self.entry_d.pack(fill="x", padx=16, pady=(2, 10))

        # Delik Toleransı
        self.lbl_h_t = ctk.CTkLabel(parent, text="Delik Tolerans Sınıfı:", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_h_t.pack(anchor="w", padx=16)
        self.cb_hole = ctk.CTkOptionMenu(
            parent,
            values=["H6", "H7", "H8", "H9", "H11"],
            corner_radius=8,
            height=38,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=COLORS["dropdown_bg"],
            text_color=COLORS["dropdown_text"],
            button_color=COLORS["accent_primary"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["dropdown_menu"],
            dropdown_text_color=COLORS["dropdown_text"],
            dropdown_hover_color=COLORS["dropdown_hover"]
        )
        self.cb_hole.set("H7")
        self.cb_hole.pack(fill="x", padx=16, pady=(2, 10))

        # Mil Toleransı
        self.lbl_s_t = ctk.CTkLabel(parent, text="Mil Tolerans Sınıfı:", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_s_t.pack(anchor="w", padx=16)
        self.cb_shaft = ctk.CTkOptionMenu(
            parent,
            values=["c11", "d9", "e8", "f7", "g6", "h6", "h7", "js6", "k6", "m6", "n6", "p6", "r6", "s6"],
            corner_radius=8,
            height=38,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=COLORS["dropdown_bg"],
            text_color=COLORS["dropdown_text"],
            button_color=COLORS["accent_primary"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["dropdown_menu"],
            dropdown_text_color=COLORS["dropdown_text"],
            dropdown_hover_color=COLORS["dropdown_hover"]
        )
        self.cb_shaft.set("g6")
        self.cb_shaft.pack(fill="x", padx=16, pady=(2, 14))

        # Hesapla Butonu
        self.btn_calc = ctk.CTkButton(
            parent,
            text="⚡ Geçmeyi Hesapla",
            corner_radius=10,
            height=42,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            text_color="#ffffff",
            command=self._on_calculate
        )
        self.btn_calc.pack(fill="x", padx=16, pady=(0, 14))

        # SPC Aktarımı Bölümü
        self.spc_box = ctk.CTkFrame(parent, fg_color=COLORS["entry_bg"], corner_radius=12)
        self.spc_box.pack(fill="x", padx=16, pady=(4, 12))

        self.lbl_spc_t = ctk.CTkLabel(
            self.spc_box,
            text="SPC Kalite Entegrasyonu",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLORS["accent_cyan"]
        )
        self.lbl_spc_t.pack(anchor="w", padx=12, pady=(10, 2))

        self.lbl_spc_desc = ctk.CTkLabel(
            self.spc_box,
            text="Hesaplanan tolerans sınırlarını doğrudan kalite modülüne aktarın:",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color=COLORS["text_secondary"],
            wraplength=270,
            justify="left"
        )
        self.lbl_spc_desc.pack(anchor="w", padx=12, pady=(0, 8))

        self.btn_send_shaft = ctk.CTkButton(
            self.spc_box,
            text="📤 Mil Ölçülerini SPC'ye Aktar",
            corner_radius=8,
            height=36,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="#0284c7",
            hover_color="#0369a1",
            text_color="#ffffff",
            command=lambda: self._send_to_spc("shaft")
        )
        self.btn_send_shaft.pack(fill="x", padx=12, pady=3)

        self.btn_send_hole = ctk.CTkButton(
            self.spc_box,
            text="📤 Delik Ölçülerini SPC'ye Aktar",
            corner_radius=8,
            height=36,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="#0369a1",
            hover_color="#075985",
            text_color="#ffffff",
            command=lambda: self._send_to_spc("hole")
        )
        self.btn_send_hole.pack(fill="x", padx=12, pady=(3, 10))

    def _build_results(self, parent):
        self.lbl_res_t = ctk.CTkLabel(
            parent,
            text="Hesaplanan Tolerans ve Geçme Çıktıları",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["accent_cyan"]
        )
        self.lbl_res_t.pack(anchor="w", padx=18, pady=(12, 4))

        self.lbl_fit_title = ctk.CTkLabel(
            parent,
            text="--",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.lbl_fit_title.pack(anchor="w", padx=18)

        self.badge_frame = ctk.CTkFrame(parent, fg_color=COLORS["accent_success"], corner_radius=8)
        self.badge_frame.pack(anchor="w", padx=18, pady=(4, 12))

        self.lbl_fit_badge = ctk.CTkLabel(
            self.badge_frame,
            text="BOŞLUKLU GEÇME",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#ffffff"
        )
        self.lbl_fit_badge.pack(padx=14, pady=5)

        cards_row = ctk.CTkFrame(parent, fg_color="transparent")
        cards_row.pack(fill="x", padx=18, pady=(0, 10))

        # Delik Kartı
        self.hole_box = ctk.CTkFrame(cards_row, fg_color=COLORS["entry_bg"], corner_radius=12)
        self.hole_box.pack(side="left", fill="both", expand=True, padx=(0, 6))

        self.lbl_h_box_t = ctk.CTkLabel(self.hole_box, text="DELİK SPESİFİKASYONU", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["accent_cyan"])
        self.lbl_h_box_t.pack(anchor="w", padx=12, pady=(10, 2))
        self.lbl_hole_limits = ctk.CTkLabel(self.hole_box, text="--", font=ctk.CTkFont(family="Segoe UI", size=10), text_color=COLORS["text_primary"], justify="left")
        self.lbl_hole_limits.pack(anchor="w", padx=12, pady=(0, 10))

        # Mil Kartı
        self.shaft_box = ctk.CTkFrame(cards_row, fg_color=COLORS["entry_bg"], corner_radius=12)
        self.shaft_box.pack(side="left", fill="both", expand=True)

        self.lbl_s_box_t = ctk.CTkLabel(self.shaft_box, text="MİL SPESİFİKASYONU", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["accent_cyan"])
        self.lbl_s_box_t.pack(anchor="w", padx=12, pady=(10, 2))
        self.lbl_shaft_limits = ctk.CTkLabel(self.shaft_box, text="--", font=ctk.CTkFont(family="Segoe UI", size=10), text_color=COLORS["text_primary"], justify="left")
        self.lbl_shaft_limits.pack(anchor="w", padx=12, pady=(0, 10))

        # Boşluk / Sıkılık Kartı
        self.clearance_box = ctk.CTkFrame(parent, fg_color=COLORS["entry_bg"], corner_radius=12)
        self.clearance_box.pack(fill="x", padx=18, pady=(0, 10))

        self.lbl_clr_t = ctk.CTkLabel(self.clearance_box, text="BOŞLUK / SIKILIK MİKTARLARI", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["accent_warning"])
        self.lbl_clr_t.pack(anchor="w", padx=12, pady=(10, 2))
        self.lbl_clearance_text = ctk.CTkLabel(self.clearance_box, text="--", font=ctk.CTkFont(family="Segoe UI", size=10), text_color=COLORS["text_primary"], justify="left")
        self.lbl_clearance_text.pack(anchor="w", padx=12, pady=(0, 10))

        # Tavsiye Kartı
        self.advice_card = ctk.CTkFrame(parent, fg_color=COLORS["entry_bg"], corner_radius=10)
        self.advice_card.pack(fill="x", padx=18, pady=(0, 14))

        self.lbl_fit_advice = ctk.CTkLabel(self.advice_card, text="", font=ctk.CTkFont(family="Segoe UI", size=10), text_color=COLORS["text_secondary"], justify="left", wraplength=560)
        self.lbl_fit_advice.pack(anchor="w", padx=12, pady=8)

    def _on_calculate(self):
        val_d = self.entry_d.get().strip()
        if not val_d:
            return

        try:
            d = float(val_d)
            res = calculate_iso_fit(d, self.cb_hole.get(), self.cb_shaft.get())
            self.current_result = res
        except Exception as e:
            messagebox.showerror("Hesaplama Hatası", str(e))
            return

        self.lbl_fit_title.configure(text=f"{res.fit_designation}  (Nominal: {res.nominal_diameter:.3f} mm)")

        if res.fit_type == FitType.CLEARANCE:
            self.badge_frame.configure(fg_color=COLORS["accent_success"])
            self.lbl_fit_badge.configure(text="BOŞLUKLU GEÇME")
            self.lbl_clearance_text.configure(
                text=f"• Maksimum Boşluk : +{res.max_clearance*1000:.1f} µm (+{res.max_clearance:.4f} mm)\n"
                     f"• Minimum Boşluk  : +{res.min_clearance*1000:.1f} µm (+{res.min_clearance:.4f} mm)"
            )
            self.lbl_fit_advice.configure(text="İmalat Notu: Parçalar birbirinin içinde dönebilir veya eksenel kayabilir (Örn: yataklama, kayar burç).")
        elif res.fit_type == FitType.INTERFERENCE:
            self.badge_frame.configure(fg_color=COLORS["accent_danger"])
            self.lbl_fit_badge.configure(text="SIKI GEÇME (ÇAKMA / PRENSES)")
            self.lbl_clearance_text.configure(
                text=f"• Maksimum Sıkılık: {res.max_interference*1000:.1f} µm ({res.max_interference:.4f} mm)\n"
                     f"• Minimum Sıkılık : {res.min_interference*1000:.1f} µm ({res.min_interference:.4f} mm)"
            )
            self.lbl_fit_advice.configure(text="İmalat Notu: Montaj presle veya gövde ısıtılarak / mil soğutularak yapılmalıdır (Örn: rulman çakma).")
        else:
            self.badge_frame.configure(fg_color=COLORS["accent_warning"])
            self.lbl_fit_badge.configure(text="ARA GEÇME (BELİRSİZ)")
            self.lbl_clearance_text.configure(
                text=f"• Maksimum Boşluk : +{res.max_clearance*1000:.1f} µm (+{res.max_clearance:.4f} mm)\n"
                     f"• Maksimum Sıkılık: {res.max_interference*1000:.1f} µm ({res.max_interference:.4f} mm)"
            )
            self.lbl_fit_advice.configure(text="İmalat Notu: İmalat sapmalarına göre hafif boşluk veya hafif sıkılık oluşabilir (Örn: merkezleme pimleri).")

        self.lbl_hole_limits.configure(
            text=f"• Sınırlar: {res.hole_min:.4f} mm - {res.hole_max:.4f} mm\n"
                 f"• Sapmalar: EI={res.hole_ei:+.4f}, ES={res.hole_es:+.4f}\n"
                 f"• Tolerans Bandı: {res.hole_tol*1000:.1f} µm"
        )

        self.lbl_shaft_limits.configure(
            text=f"• Sınırlar: {res.shaft_min:.4f} mm - {res.shaft_max:.4f} mm\n"
                 f"• Sapmalar: ei={res.shaft_ei:+.4f}, es={res.shaft_es:+.4f}\n"
                 f"• Tolerans Bandı: {res.shaft_tol*1000:.1f} µm"
        )

    def _send_to_spc(self, target: str):
        if not self.current_result:
            return
        res = self.current_result
        if target == "shaft":
            part_name = f"Mil İmalatı ({res.fit_designation})"
            nominal = (res.shaft_max + res.shaft_min) / 2.0
            usl = res.shaft_max
            lsl = res.shaft_min
        else:
            part_name = f"Delik İmalatı ({res.fit_designation})"
            nominal = (res.hole_max + res.hole_min) / 2.0
            usl = res.hole_max
            lsl = res.hole_min

        self.main_app.switch_to_spc_with_limits(part_name, nominal, usl, lsl)

    def apply_theme(self):
        self.configure(fg_color=COLORS["bg_app"])
        self.top_bar.configure(fg_color=COLORS["card_bg"])
        self.lbl_head.configure(text_color=COLORS["text_primary"])
        self.lbl_guide.configure(text_color=COLORS["text_secondary"])

        self.left_card.configure(fg_color=COLORS["card_bg"])
        self.right_card.configure(fg_color=COLORS["card_bg"])

        self.lbl_in_t.configure(text_color=COLORS["accent_cyan"])
        self.lbl_d_t.configure(text_color=COLORS["text_primary"])
        self.lbl_h_t.configure(text_color=COLORS["text_primary"])
        self.lbl_s_t.configure(text_color=COLORS["text_primary"])

        self.entry_d.configure(
            fg_color=COLORS["entry_bg"],
            text_color=COLORS["text_primary"],
            border_color=COLORS["entry_border"]
        )

        # Dropdown renklerinin temaya tam uyarlanması (Açık modda bembeyaz ve net)
        self.cb_hole.configure(
            fg_color=COLORS["dropdown_bg"],
            text_color=COLORS["dropdown_text"],
            button_color=COLORS["accent_primary"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["dropdown_menu"],
            dropdown_text_color=COLORS["dropdown_text"],
            dropdown_hover_color=COLORS["dropdown_hover"]
        )

        self.cb_shaft.configure(
            fg_color=COLORS["dropdown_bg"],
            text_color=COLORS["dropdown_text"],
            button_color=COLORS["accent_primary"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["dropdown_menu"],
            dropdown_text_color=COLORS["dropdown_text"],
            dropdown_hover_color=COLORS["dropdown_hover"]
        )

        self.spc_box.configure(fg_color=COLORS["entry_bg"])
        self.lbl_spc_t.configure(text_color=COLORS["accent_cyan"])
        self.lbl_spc_desc.configure(text_color=COLORS["text_secondary"])

        self.lbl_res_t.configure(text_color=COLORS["accent_cyan"])
        self.lbl_fit_title.configure(text_color=COLORS["text_primary"])

        self.hole_box.configure(fg_color=COLORS["entry_bg"])
        self.lbl_h_box_t.configure(text_color=COLORS["accent_cyan"])
        self.lbl_hole_limits.configure(text_color=COLORS["text_primary"])

        self.shaft_box.configure(fg_color=COLORS["entry_bg"])
        self.lbl_s_box_t.configure(text_color=COLORS["accent_cyan"])
        self.lbl_shaft_limits.configure(text_color=COLORS["text_primary"])

        self.clearance_box.configure(fg_color=COLORS["entry_bg"])
        self.lbl_clr_t.configure(text_color=COLORS["accent_warning"])
        self.lbl_clearance_text.configure(text_color=COLORS["text_primary"])

        self.advice_card.configure(fg_color=COLORS["entry_bg"])
        self.lbl_fit_advice.configure(text_color=COLORS["text_secondary"])

        self.btn_calc.configure(fg_color=COLORS["accent_primary"], hover_color=COLORS["accent_hover"], text_color="#ffffff")
        self.btn_send_shaft.configure(fg_color="#0284c7", hover_color="#0369a1", text_color="#ffffff")
        self.btn_send_hole.configure(fg_color="#0369a1", hover_color="#075985", text_color="#ffffff")
