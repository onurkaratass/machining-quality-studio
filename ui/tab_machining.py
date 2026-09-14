"""
ui.tab_machining
~~~~~~~~~~~~~~
CustomTkinter tabanlı CNC Kesme Parametreleri, Güç ve Tork Hesaplama Arayüz Sekmesi.
"""

from tkinter import messagebox
import customtkinter as ctk

from core.machining_calc import (
    calculate_milling,
    calculate_turning,
    MATERIALS,
    MachiningResult,
    OperationType
)
from ui.styles import COLORS
from ui.components import ModernPillSwitch


class TabMachining(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color=COLORS["bg_app"], corner_radius=0)
        self.main_app = main_app
        self._build_ui()

    def _build_ui(self):
        # 1. Üst Başlık ve Rehber Kutusu
        self.top_bar = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=12)
        self.top_bar.pack(fill="x", padx=16, pady=(12, 6))

        self.lbl_head = ctk.CTkLabel(
            self.top_bar,
            text="CNC KESME PARAMETRELERİ, GÜÇ VE TORK HESAPLAYICISI",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.lbl_head.pack(anchor="w", padx=18, pady=(10, 2))

        self.lbl_guide = ctk.CTkLabel(
            self.top_bar,
            text="💡 Nasıl Kullanılır?\n"
                 "1. İşlem türünü (Frezeleme veya Tornalama) seçin ve işlenecek malzemeyi belirleyin.\n"
                 "2. Takım çapı, kesme hızı (Vc), diş başına ilerleme ve kesme derinliğini (ap/ae) girin.\n"
                 "3. 'Hesapla' butonuna bastığınızda Kienzle modeliyle fener mili devri (N), talaş debisi (MRR), net motor gücü (Pc) ve tork anında hesaplanır.",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLORS["text_secondary"],
            justify="left",
            wraplength=1050
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
            text="İşlem ve Malzeme Seçimi",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["accent_cyan"]
        )
        self.lbl_in_t.pack(anchor="w", padx=16, pady=(12, 8))

        # Çizgisiz, Kusursuz Apple Tarzı Kapsül Seçici
        self.seg_op = ModernPillSwitch(
            parent,
            values=["Frezeleme (Milling)", "Tornalama (Turning)"],
            command=self._on_op_change,
            default="Frezeleme (Milling)",
            height=38
        )
        self.seg_op.pack(fill="x", padx=16, pady=(0, 10))

        # Malzeme Dropdown
        self.lbl_mat_t = ctk.CTkLabel(parent, text="İş Parçası Malzemesi:", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_mat_t.pack(anchor="w", padx=16)
        self.mat_keys = list(MATERIALS.keys())
        self.mat_names = [MATERIALS[k].code for k in self.mat_keys]
        self.cb_material = ctk.CTkOptionMenu(
            parent,
            values=self.mat_names,
            corner_radius=8,
            height=38,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=COLORS["dropdown_bg"],
            text_color=COLORS["dropdown_text"],
            button_color=COLORS["accent_primary"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["dropdown_menu"],
            dropdown_text_color=COLORS["dropdown_text"],
            dropdown_hover_color=COLORS["dropdown_hover"],
            command=self._on_mat_change
        )
        self.cb_material.set(self.mat_names[0])
        self.cb_material.pack(fill="x", padx=16, pady=(2, 4))

        self.lbl_vc_rec = ctk.CTkLabel(parent, text="Önerilen Vc: 140 - 220 m/dak", font=ctk.CTkFont(family="Segoe UI", size=9), text_color=COLORS["accent_cyan"])
        self.lbl_vc_rec.pack(anchor="w", padx=16, pady=(0, 6))

        # Çap (D)
        self.lbl_d = ctk.CTkLabel(parent, text="Takım / İş Parçası Çapı (D - mm):", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_d.pack(anchor="w", padx=16)
        self.entry_d = ctk.CTkEntry(parent, placeholder_text="Örn: 50.0", corner_radius=8, height=38, font=ctk.CTkFont(family="Segoe UI", size=11))
        self.entry_d.insert(0, "50.0")
        self.entry_d.pack(fill="x", padx=16, pady=(2, 6))

        # Kesme Hızı (Vc)
        self.lbl_vc = ctk.CTkLabel(parent, text="Kesme Hızı (Vc - m/dak):", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_vc.pack(anchor="w", padx=16)
        self.entry_vc = ctk.CTkEntry(parent, placeholder_text="Örn: 180.0", corner_radius=8, height=38, font=ctk.CTkFont(family="Segoe UI", size=11))
        self.entry_vc.insert(0, "180.0")
        self.entry_vc.pack(fill="x", padx=16, pady=(2, 6))

        # Diş Sayısı (z)
        self.lbl_z = ctk.CTkLabel(parent, text="Kesici Ağız Sayısı (z):", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_z.pack(anchor="w", padx=16)
        self.entry_z = ctk.CTkEntry(parent, placeholder_text="Örn: 4", corner_radius=8, height=38, font=ctk.CTkFont(family="Segoe UI", size=11))
        self.entry_z.insert(0, "4")
        self.entry_z.pack(fill="x", padx=16, pady=(2, 6))

        # İlerleme
        self.lbl_f = ctk.CTkLabel(parent, text="Diş Başına İlerleme (fz - mm/diş):", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_f.pack(anchor="w", padx=16)
        self.entry_f = ctk.CTkEntry(parent, placeholder_text="Örn: 0.15", corner_radius=8, height=38, font=ctk.CTkFont(family="Segoe UI", size=11))
        self.entry_f.insert(0, "0.15")
        self.entry_f.pack(fill="x", padx=16, pady=(2, 6))

        # Kesme Derinliği ve Genişliği
        self.grid_cuts = ctk.CTkFrame(parent, fg_color="transparent")
        self.grid_cuts.pack(fill="x", padx=16, pady=(0, 10))

        self.lbl_ap = ctk.CTkLabel(self.grid_cuts, text="Derinlik (ap - mm):", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_ap.grid(row=0, column=0, sticky="w")
        self.lbl_ae = ctk.CTkLabel(self.grid_cuts, text="Genişlik (ae - mm):", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_ae.grid(row=0, column=1, sticky="w", padx=(10, 0))

        self.entry_ap = ctk.CTkEntry(self.grid_cuts, placeholder_text="Örn: 2.0", corner_radius=8, height=38, width=140, font=ctk.CTkFont(family="Segoe UI", size=11))
        self.entry_ap.insert(0, "2.0")
        self.entry_ap.grid(row=1, column=0, sticky="we", pady=(2, 0))

        self.entry_ae = ctk.CTkEntry(self.grid_cuts, placeholder_text="Örn: 35.0", corner_radius=8, height=38, width=140, font=ctk.CTkFont(family="Segoe UI", size=11))
        self.entry_ae.insert(0, "35.0")
        self.entry_ae.grid(row=1, column=1, sticky="we", padx=(10, 0), pady=(2, 0))

        # Hesapla Butonu
        self.btn_calc = ctk.CTkButton(
            parent,
            text="⚡ Parametre ve Güç Hesapla",
            corner_radius=10,
            height=42,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            text_color="#ffffff",
            command=self._on_calculate
        )
        self.btn_calc.pack(fill="x", padx=16, pady=(8, 14))

    def _build_results(self, parent):
        self.lbl_res_t = ctk.CTkLabel(
            parent,
            text="Hesaplanan Tezgâh Çıktıları",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["accent_cyan"]
        )
        self.lbl_res_t.pack(anchor="w", padx=18, pady=(12, 6))

        # 6'lı Metrik Kartları
        self.grid_cards = ctk.CTkFrame(parent, fg_color="transparent")
        self.grid_cards.pack(fill="x", padx=18, pady=(0, 10))

        self.cards = {}
        self.cards["rpm"] = self._make_card(self.grid_cards, "Devir (N)", "-- RPM", 0, 0)
        self.cards["feed"] = self._make_card(self.grid_cards, "İlerleme Hızı (Vf)", "-- mm/dak", 0, 1)
        self.cards["mrr"] = self._make_card(self.grid_cards, "Talaş Debisi (MRR)", "-- cm³/dak", 0, 2)

        self.cards["power"] = self._make_card(self.grid_cards, "Net Güç (Pc)", "-- kW", 1, 0)
        self.cards["torque"] = self._make_card(self.grid_cards, "Mil Torku (Mc)", "-- Nm", 1, 1)
        self.cards["force"] = self._make_card(self.grid_cards, "Kesme Kuvveti (Fc)", "-- N", 1, 2)

        # Tavsiye Paneli
        self.advice_box = ctk.CTkFrame(parent, fg_color=COLORS["entry_bg"], corner_radius=12)
        self.advice_box.pack(fill="x", padx=18, pady=(6, 14))

        self.lbl_adv_t = ctk.CTkLabel(self.advice_box, text="TEZGÂH VE GÜÇ TAVSİYESİ", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["accent_cyan"])
        self.lbl_adv_t.pack(anchor="w", padx=14, pady=(10, 2))

        self.lbl_power_advice = ctk.CTkLabel(self.advice_box, text="--", font=ctk.CTkFont(family="Segoe UI", size=10), text_color=COLORS["text_primary"], justify="left", wraplength=560)
        self.lbl_power_advice.pack(anchor="w", padx=14, pady=(0, 10))

    def _make_card(self, parent, title, val, row, col):
        box = ctk.CTkFrame(parent, fg_color=COLORS["entry_bg"], corner_radius=12)
        box.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
        parent.grid_columnconfigure(col, weight=1)

        lbl_t = ctk.CTkLabel(box, text=title, font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"), text_color=COLORS["text_secondary"])
        lbl_t.pack(anchor="w", padx=12, pady=(8, 0))

        lbl_v = ctk.CTkLabel(box, text=val, font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), text_color=COLORS["text_primary"])
        lbl_v.pack(anchor="w", padx=12, pady=(0, 8))

        return (box, lbl_t, lbl_v)

    def _on_op_change(self, choice: str):
        if "Tornalama" in choice:
            self.lbl_z.pack_forget()
            self.entry_z.pack_forget()
            self.lbl_f.configure(text="Devir Başına İlerleme (f - mm/dev):")
            self.entry_f.delete(0, "end")
            self.entry_f.insert(0, "0.25")
            self.lbl_ae.grid_remove()
            self.entry_ae.grid_remove()
        else:
            self.lbl_z.pack(anchor="w", padx=16, before=self.lbl_f)
            self.entry_z.pack(fill="x", padx=16, pady=(2, 6), before=self.lbl_f)
            self.lbl_f.configure(text="Diş Başına İlerleme (fz - mm/diş):")
            self.entry_f.delete(0, "end")
            self.entry_f.insert(0, "0.15")
            self.lbl_ae.grid(row=0, column=1, sticky="w", padx=(10, 0))
            self.entry_ae.grid(row=1, column=1, sticky="we", padx=(10, 0), pady=(2, 0))
        self._on_calculate()

    def _on_mat_change(self, choice: str):
        idx = self.mat_names.index(choice) if choice in self.mat_names else 0
        key = self.mat_keys[idx]
        mat = MATERIALS[key]
        self.lbl_vc_rec.configure(text=f"Önerilen Vc: {mat.recommended_vc_min:.0f} - {mat.recommended_vc_max:.0f} m/dak")

    def _on_calculate(self):
        try:
            d = float(self.entry_d.get().strip())
            vc = float(self.entry_vc.get().strip())
            f = float(self.entry_f.get().strip())
            ap = float(self.entry_ap.get().strip())
            choice = self.cb_material.get()
            idx = self.mat_names.index(choice) if choice in self.mat_names else 0
            mat_key = self.mat_keys[idx]

            if "Frezeleme" in self.seg_op.get():
                z = int(self.entry_z.get().strip())
                ae = float(self.entry_ae.get().strip())
                res = calculate_milling(d, z, vc, f, ap, ae, mat_key)
            else:
                res = calculate_turning(d, vc, f, ap, mat_key)

            self.cards["rpm"][2].configure(text=f"{res.rpm:.0f} RPM")
            self.cards["feed"][2].configure(text=f"{res.feed_rate:.0f} mm/dak")
            self.cards["mrr"][2].configure(text=f"{res.mrr:.1f} cm³/dak")

            p_col = COLORS["accent_success"] if res.power_kw < 5.5 else (COLORS["accent_warning"] if res.power_kw < 11.0 else COLORS["accent_danger"])
            self.cards["power"][2].configure(text=f"{res.power_kw:.2f} kW", text_color=p_col)
            self.cards["torque"][2].configure(text=f"{res.torque_nm:.1f} Nm")
            self.cards["force"][2].configure(text=f"{res.cutting_force_fc:.0f} N")

            if res.power_kw < 5.5:
                adv = f"• Güç İhtiyacı: Düşük / Normal ({res.power_kw:.1f} kW). Standart dik işleme merkezleri ve torna tezgâhları için çok uygundur."
            elif res.power_kw < 11.0:
                adv = f"• Güç İhtiyacı: Orta ({res.power_kw:.1f} kW). En az 7.5 - 11 kW güce sahip sanayi tipi tezgâhlar önerilir."
            else:
                adv = f"• DİKKAT: Yüksek Güç ({res.power_kw:.1f} kW)! Fener milini aşırı yükleme riski mevcuttur. Kesme derinliği veya ilerlemeyi azaltınız."

            self.lbl_power_advice.configure(text=f"{adv}\n• Malzeme Özgül Kesme Direnci (kc): {res.kc:.0f} N/mm²")

        except Exception:
            pass

    def apply_theme(self):
        self.configure(fg_color=COLORS["bg_app"])
        self.top_bar.configure(fg_color=COLORS["card_bg"])
        self.lbl_head.configure(text_color=COLORS["text_primary"])
        self.lbl_guide.configure(text_color=COLORS["text_secondary"])

        self.left_card.configure(fg_color=COLORS["card_bg"])
        self.right_card.configure(fg_color=COLORS["card_bg"])

        self.seg_op.update_theme()

        self.lbl_in_t.configure(text_color=COLORS["accent_cyan"])
        self.lbl_mat_t.configure(text_color=COLORS["text_primary"])
        self.lbl_vc_rec.configure(text_color=COLORS["accent_cyan"])
        self.lbl_d.configure(text_color=COLORS["text_primary"])
        self.lbl_vc.configure(text_color=COLORS["text_primary"])
        self.lbl_z.configure(text_color=COLORS["text_primary"])
        self.lbl_f.configure(text_color=COLORS["text_primary"])
        self.lbl_ap.configure(text_color=COLORS["text_primary"])
        self.lbl_ae.configure(text_color=COLORS["text_primary"])

        self.cb_material.configure(
            fg_color=COLORS["dropdown_bg"],
            text_color=COLORS["dropdown_text"],
            button_color=COLORS["accent_primary"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["dropdown_menu"],
            dropdown_text_color=COLORS["dropdown_text"],
            dropdown_hover_color=COLORS["dropdown_hover"]
        )

        for ent in [self.entry_d, self.entry_vc, self.entry_z, self.entry_f, self.entry_ap, self.entry_ae]:
            ent.configure(
                fg_color=COLORS["entry_bg"],
                text_color=COLORS["text_primary"],
                border_color=COLORS["entry_border"]
            )

        self.lbl_res_t.configure(text_color=COLORS["accent_cyan"])
        self.advice_box.configure(fg_color=COLORS["entry_bg"])
        self.lbl_adv_t.configure(text_color=COLORS["accent_cyan"])
        self.lbl_power_advice.configure(text_color=COLORS["text_primary"])

        self.btn_calc.configure(fg_color=COLORS["accent_primary"], hover_color=COLORS["accent_hover"], text_color="#ffffff")

        for key, (box, lbl_t, lbl_v) in self.cards.items():
            box.configure(fg_color=COLORS["entry_bg"])
            lbl_t.configure(text_color=COLORS["text_secondary"])
            lbl_v.configure(text_color=COLORS["text_primary"])
