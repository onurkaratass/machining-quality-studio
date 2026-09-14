"""
ui.tab_reports
~~~~~~~~~~~~~~
CustomTkinter tabanlı Kurumsal Kalite Raporlama ve Dokümantasyon Sekmesi.
"""

import customtkinter as ctk
from ui.styles import COLORS


class TabReports(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color=COLORS["bg_app"], corner_radius=0)
        self.main_app = main_app
        self._build_ui()

    def _build_ui(self):
        self.top_bar = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=12)
        self.top_bar.pack(fill="x", padx=16, pady=(12, 6))

        self.lbl_head = ctk.CTkLabel(
            self.top_bar,
            text="KURUMSAL RAPORLAMA VE KALİTE SERTİFİKASYON MERKEZİ",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.lbl_head.pack(anchor="w", padx=18, pady=(10, 2))

        self.lbl_sub = ctk.CTkLabel(
            self.top_bar,
            text="Resmi FAI (İlk Parça Onayı) ve PPAP kalite sertifikaları için kurumsal başlık, tezgâh ve onay ayarları.",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLORS["text_secondary"]
        )
        self.lbl_sub.pack(anchor="w", padx=18, pady=(0, 10))

        # Ana Kart
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        self.card = ctk.CTkFrame(self.content, fg_color=COLORS["card_bg"], corner_radius=14)
        self.card.pack(fill="both", expand=True)

        self.lbl_sec_t = ctk.CTkLabel(
            self.card,
            text="PDF Kalite Sertifikası Kurumsal Bilgileri",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["accent_cyan"]
        )
        self.lbl_sec_t.pack(anchor="w", padx=20, pady=(16, 12))

        self.form = ctk.CTkFrame(self.card, fg_color="transparent")
        self.form.pack(fill="x", padx=20, pady=(0, 16))

        fields = [
            ("company", "Firma / İmalat Atölyesi Ünvanı:", "Hassas Talaşlı İmalat Sanayi A.Ş."),
            ("operator", "Kalite Kontrol Sorumlusu (Ad Soyad):", "Kalite Güvence ve Metroloji"),
            ("machine", "CNC Tezgâh Kodu / İstasyon:", "CNC-LATHE-01"),
            ("lot", "İş Emri / Parti / Lot No:", "LOT-2026-X1"),
        ]

        self.entries = {}
        self.labels = {}
        for row, (key, label_text, default_val) in enumerate(fields):
            lbl = ctk.CTkLabel(self.form, text=label_text, font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
            lbl.grid(row=row, column=0, sticky="w", pady=6)
            self.labels[key] = lbl

            ent = ctk.CTkEntry(self.form, placeholder_text=default_val, width=420, corner_radius=8, height=38, font=ctk.CTkFont(family="Segoe UI", size=11))
            ent.insert(0, default_val)
            ent.grid(row=row, column=1, sticky="we", padx=(15, 0), pady=6)
            self.entries[key] = ent

        # Bilgilendirme Kutusu
        self.info_box = ctk.CTkFrame(self.card, fg_color=COLORS["entry_bg"], corner_radius=12)
        self.info_box.pack(fill="x", padx=20, pady=(6, 16))

        self.lbl_info_t = ctk.CTkLabel(self.info_box, text="DOKÜMANTASYON STANDARDI HAKKINDA", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["accent_cyan"])
        self.lbl_info_t.pack(anchor="w", padx=14, pady=(10, 2))

        info_text = (
            "• Üretilen PDF sertifikaları ISO 9001 ve havacılık imalat kalite güvence standartlarına uygundur.\n"
            "• SPC sekmesinde 'Resmi PDF Raporu Oluştur' butonuna tıklandığında yukarıdaki bilgiler rapora otomatik eklenir.\n"
            "• Çıktı tek sayfalık A4 formatında; tolerans değerlerini, hesaplanan Cp/Cpk indekslerini, gömülü Gauss grafiğini ve ıslak imza kutucuklarını içerir."
        )
        self.lbl_info_body = ctk.CTkLabel(self.info_box, text=info_text, font=ctk.CTkFont(family="Segoe UI", size=9), text_color=COLORS["text_secondary"], justify="left")
        self.lbl_info_body.pack(anchor="w", padx=14, pady=(0, 10))

        # Hızlı Buton
        self.btn_go_spc = ctk.CTkButton(
            self.card,
            text="📊 SPC Sekmesine Git ve Analiz Raporunu İndir",
            corner_radius=10,
            height=42,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            text_color="#ffffff",
            command=lambda: self.main_app.show_tab("SPC")
        )
        self.btn_go_spc.pack(side="left", padx=20, pady=(0, 20))

    def get_report_metadata(self) -> dict:
        return {
            "company": self.entries["company"].get().strip() or "Hassas Talaşlı İmalat Sanayi A.Ş.",
            "operator": self.entries["operator"].get().strip() or "Kalite Kontrol Sorumlusu",
            "machine": self.entries["machine"].get().strip() or "CNC-LATHE-01",
            "lot": self.entries["lot"].get().strip() or "LOT-2026-X1",
        }

    def apply_theme(self):
        self.configure(fg_color=COLORS["bg_app"])
        self.top_bar.configure(fg_color=COLORS["card_bg"])
        self.lbl_head.configure(text_color=COLORS["text_primary"])
        self.lbl_sub.configure(text_color=COLORS["text_secondary"])

        self.card.configure(fg_color=COLORS["card_bg"])
        self.lbl_sec_t.configure(text_color=COLORS["accent_cyan"])

        for lbl in self.labels.values():
            lbl.configure(text_color=COLORS["text_primary"])

        for ent in self.entries.values():
            ent.configure(
                fg_color=COLORS["entry_bg"],
                text_color=COLORS["text_primary"],
                border_color=COLORS["entry_border"]
            )

        self.info_box.configure(fg_color=COLORS["entry_bg"])
        self.lbl_info_t.configure(text_color=COLORS["accent_cyan"])
        self.lbl_info_body.configure(text_color=COLORS["text_secondary"])

        self.btn_go_spc.configure(fg_color=COLORS["accent_primary"], hover_color=COLORS["accent_hover"], text_color="#ffffff")
