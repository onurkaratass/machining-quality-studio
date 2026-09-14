"""
ui.tab_cost
~~~~~~~~~~~
CustomTkinter tabanlı İmalat Parça Maliyeti ve Müşteri Fiyat Teklifi (Quotation) Sekmesi.
"""

from tkinter import filedialog, messagebox
import customtkinter as ctk

from core.machining_calc import CostEngine, CostResult
from core.pdf_exporter import QuotationReportGenerator
from ui.styles import COLORS


class TabCost(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color=COLORS["bg_app"], corner_radius=0)
        self.main_app = main_app
        self.current_result: CostResult = None
        self._build_ui()

    def _build_ui(self):
        # 1. Üst Başlık ve Rehber
        self.top_bar = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=12)
        self.top_bar.pack(fill="x", padx=16, pady=(12, 6))

        self.lbl_head = ctk.CTkLabel(
            self.top_bar,
            text="TALAŞLI İMALAT PARÇA MALİYETİ VE FİYAT TEKLİFİ HESAPLAYICISI",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.lbl_head.pack(anchor="w", padx=18, pady=(10, 2))

        self.lbl_guide = ctk.CTkLabel(
            self.top_bar,
            text="💡 Nasıl Kullanılır?\n"
                 "1. Kütük hammadde ölçülerini (çap/boy), malzeme kg fiyatını ve sipariş parti adedini girin.\n"
                 "2. Tezgâh saat ücretini ve işleme süresini (G-Kod sekmesinden otomatik aktarılabilir) belirleyin.\n"
                 "3. 'Hesapla' butonuna bastığınızda net birim maliyet, kâr payı ve tek tıkla kurumsal Müşteri Teklif Formu (PDF) oluşturulur.",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLORS["text_secondary"],
            justify="left"
        )
        self.lbl_guide.pack(anchor="w", padx=18, pady=(0, 10))

        # 2. Ana Gövde
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        self.left_card = ctk.CTkFrame(self.content, fg_color=COLORS["card_bg"], corner_radius=14, width=380)
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
            text="Maliyet ve Teklif Parametreleri",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["accent_cyan"]
        )
        self.lbl_in_t.pack(anchor="w", padx=16, pady=(10, 6))

        # Parça Adı
        self.lbl_p = ctk.CTkLabel(parent, text="İş Parçası Adı:", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_p.pack(anchor="w", padx=16)
        self.entry_part = ctk.CTkEntry(parent, placeholder_text="Örn: Hassas Rulman Şaftı", corner_radius=8, height=34, font=ctk.CTkFont(family="Segoe UI", size=10))
        self.entry_part.insert(0, "Hassas CNC Şaftı")
        self.entry_part.pack(fill="x", padx=16, pady=(2, 6))

        # Kütük Çap ve Boy
        grid_dim = ctk.CTkFrame(parent, fg_color="transparent")
        grid_dim.pack(fill="x", padx=16, pady=(0, 4))
        ctk.CTkLabel(grid_dim, text="Kütük Çapı (mm):", font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(grid_dim, text="Kütük Boyu (mm):", font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold")).grid(row=0, column=1, sticky="w", padx=(8, 0))

        self.entry_dia = ctk.CTkEntry(grid_dim, width=150, height=32, font=ctk.CTkFont(family="Segoe UI", size=10))
        self.entry_dia.insert(0, "60.0")
        self.entry_dia.grid(row=1, column=0, sticky="we", pady=(2, 0))

        self.entry_len = ctk.CTkEntry(grid_dim, width=150, height=32, font=ctk.CTkFont(family="Segoe UI", size=10))
        self.entry_len.insert(0, "150.0")
        self.entry_len.grid(row=1, column=1, sticky="we", padx=(8, 0), pady=(2, 0))

        # Yoğunluk ve Kg Fiyatı
        grid_mat = ctk.CTkFrame(parent, fg_color="transparent")
        grid_mat.pack(fill="x", padx=16, pady=(4, 4))
        ctk.CTkLabel(grid_mat, text="Yoğunluk (g/cm³):", font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(grid_mat, text="Hammadde (TL/kg):", font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold")).grid(row=0, column=1, sticky="w", padx=(8, 0))

        self.entry_dens = ctk.CTkEntry(grid_mat, width=150, height=32, font=ctk.CTkFont(family="Segoe UI", size=10))
        self.entry_dens.insert(0, "7.85")
        self.entry_dens.grid(row=1, column=0, sticky="we", pady=(2, 0))

        self.entry_mat_price = ctk.CTkEntry(grid_mat, width=150, height=32, font=ctk.CTkFont(family="Segoe UI", size=10))
        self.entry_mat_price.insert(0, "55.0")
        self.entry_mat_price.grid(row=1, column=1, sticky="we", padx=(8, 0), pady=(2, 0))

        # İşleme Süresi ve Tezgâh Ücreti
        grid_time = ctk.CTkFrame(parent, fg_color="transparent")
        grid_time.pack(fill="x", padx=16, pady=(4, 4))
        ctk.CTkLabel(grid_time, text="İşleme Süresi (Dakika):", font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(grid_time, text="Tezgâh Saat (TL/saat):", font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold")).grid(row=0, column=1, sticky="w", padx=(8, 0))

        self.entry_time = ctk.CTkEntry(grid_time, width=150, height=32, font=ctk.CTkFont(family="Segoe UI", size=10))
        self.entry_time.insert(0, "8.5")
        self.entry_time.grid(row=1, column=0, sticky="we", pady=(2, 0))

        self.entry_rate = ctk.CTkEntry(grid_time, width=150, height=32, font=ctk.CTkFont(family="Segoe UI", size=10))
        self.entry_rate.insert(0, "900.0")
        self.entry_rate.grid(row=1, column=1, sticky="we", padx=(8, 0), pady=(2, 0))

        # G-Kodu Modülünden Çek Butonu
        self.btn_pull_gcode = ctk.CTkButton(
            parent,
            text="⏱️ Süreyi G-Kod Modülünden Aktar",
            corner_radius=8,
            height=30,
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            fg_color=COLORS["entry_bg"],
            hover_color=COLORS["sidebar_hover"],
            text_color=COLORS["accent_cyan"],
            command=self._on_pull_gcode_time
        )
        self.btn_pull_gcode.pack(fill="x", padx=16, pady=(2, 6))

        # Parti Adedi ve Kâr Marjı
        grid_batch = ctk.CTkFrame(parent, fg_color="transparent")
        grid_batch.pack(fill="x", padx=16, pady=(2, 6))
        ctk.CTkLabel(grid_batch, text="Sipariş Adedi:", font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(grid_batch, text="Kâr Marjı (%):", font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold")).grid(row=0, column=1, sticky="w", padx=(8, 0))

        self.entry_batch = ctk.CTkEntry(grid_batch, width=150, height=32, font=ctk.CTkFont(family="Segoe UI", size=10))
        self.entry_batch.insert(0, "50")
        self.entry_batch.grid(row=1, column=0, sticky="we", pady=(2, 0))

        self.entry_markup = ctk.CTkEntry(grid_batch, width=150, height=32, font=ctk.CTkFont(family="Segoe UI", size=10))
        self.entry_markup.insert(0, "30")
        self.entry_markup.grid(row=1, column=1, sticky="we", padx=(8, 0), pady=(2, 0))

        # Hesapla Butonu
        self.btn_calc = ctk.CTkButton(
            parent,
            text="⚡ Fiyat Teklifini Hesapla",
            corner_radius=10,
            height=40,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            text_color="#ffffff",
            command=self._on_calculate
        )
        self.btn_calc.pack(fill="x", padx=16, pady=(8, 12))

    def _build_results(self, parent):
        # Üst Araç Çubuğu
        self.action_bar = ctk.CTkFrame(parent, fg_color="transparent")
        self.action_bar.pack(fill="x", padx=18, pady=(12, 6))

        self.lbl_res_t = ctk.CTkLabel(
            self.action_bar,
            text="Maliyet Analizi ve Fiyat Teklifi Özeti",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["accent_cyan"]
        )
        self.lbl_res_t.pack(side="left")

        self.btn_pdf = ctk.CTkButton(
            self.action_bar,
            text="📄 Müşteri Teklif Mektubu (PDF)",
            corner_radius=8,
            height=34,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color=COLORS["btn_pdf"],
            hover_color=COLORS["btn_pdf_hover"],
            text_color="#ffffff",
            command=self._on_export_pdf
        )
        self.btn_pdf.pack(side="right")

        # 4 Büyük Metrik Kartı
        self.grid_cards = ctk.CTkFrame(parent, fg_color="transparent")
        self.grid_cards.pack(fill="x", padx=18, pady=(0, 10))

        self.cards = {}
        self.cards["weight"] = self._make_card(self.grid_cards, "Kütük Ağırlığı", "-- kg", 0, 0)
        self.cards["base"] = self._make_card(self.grid_cards, "Birim Net Maliyet", "-- TL", 0, 1)
        self.cards["price"] = self._make_card(self.grid_cards, "Birim Satış Fiyatı", "-- TL", 1, 0, highlight=True)
        self.cards["total"] = self._make_card(self.grid_cards, "Parti Toplam Teklif", "-- TL", 1, 1, highlight=True)

        # Detaylı Maliyet Döküm Kartı
        self.breakdown_card = ctk.CTkFrame(parent, fg_color=COLORS["entry_bg"], corner_radius=12)
        self.breakdown_card.pack(fill="both", expand=True, padx=18, pady=(4, 14))

        self.lbl_bk_t = ctk.CTkLabel(self.breakdown_card, text="AYRINTILI MALİYET KALEMLERİ DÖKÜMÜ", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["accent_cyan"])
        self.lbl_bk_t.pack(anchor="w", padx=16, pady=(12, 4))

        self.txt_breakdown = ctk.CTkTextbox(self.breakdown_card, corner_radius=8, font=ctk.CTkFont(family="Consolas", size=11))
        self.txt_breakdown.pack(fill="both", expand=True, padx=14, pady=(0, 12))

    def _make_card(self, parent, title, val, row, col, highlight=False):
        box = ctk.CTkFrame(parent, fg_color=COLORS["entry_bg"], corner_radius=12)
        box.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
        parent.grid_columnconfigure(col, weight=1)

        lbl_t = ctk.CTkLabel(box, text=title, font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"), text_color=COLORS["text_secondary"])
        lbl_t.pack(anchor="w", padx=14, pady=(10, 0))

        val_color = COLORS["accent_cyan"] if highlight else COLORS["text_primary"]
        lbl_v = ctk.CTkLabel(box, text=val, font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"), text_color=val_color)
        lbl_v.pack(anchor="w", padx=14, pady=(0, 10))

        return (box, lbl_t, lbl_v)

    def _on_pull_gcode_time(self):
        gcode_tab = self.main_app.tabs.get("GCODE")
        if gcode_tab and gcode_tab.current_result:
            sec = gcode_tab.current_result.estimated_time_seconds
            mins = round(sec / 60.0, 2)
            self.entry_time.delete(0, "end")
            self.entry_time.insert(0, str(mins))
            messagebox.showinfo("Başarılı", f"G-Kod simülatöründen işleme süresi aktarıldı: {mins:.2f} dakika")
            self._on_calculate()
        else:
            messagebox.showwarning("Bilgi Yok", "G-Kod simülatörü sekmesinde henüz analiz çalıştırılmamış.")

    def _on_calculate(self):
        try:
            part = self.entry_part.get().strip() or "Hassas CNC Şaftı"
            dia = float(self.entry_dia.get().strip())
            length = float(self.entry_len.get().strip())
            dens = float(self.entry_dens.get().strip())
            mat_price = float(self.entry_mat_price.get().strip())
            ctime = float(self.entry_time.get().strip())
            rate = float(self.entry_rate.get().strip())
            batch = int(self.entry_batch.get().strip())
            markup = float(self.entry_markup.get().strip())

            res = CostEngine.calculate(
                part_name=part,
                diameter_mm=dia,
                length_mm=length,
                density_g_cm3=dens,
                price_per_kg_tl=mat_price,
                cycle_time_min=ctime,
                machine_hour_rate_tl=rate,
                tool_wear_cost_tl=25.0,
                setup_time_min=30.0,
                labor_hour_rate_tl=350.0,
                batch_size=batch,
                markup_percent=markup
            )
            self.current_result = res

            # Kartlar
            self.cards["weight"][2].configure(text=f"{res.weight_kg:.3f} kg")
            self.cards["base"][2].configure(text=f"{res.base_unit_cost:.2f} TL")
            self.cards["price"][2].configure(text=f"{res.final_unit_price:.2f} TL")
            self.cards["total"][2].configure(text=f"{res.total_batch_price:,.2f} TL")

            # Döküm Metni
            lines = [
                f"═" * 58,
                f"  MALİYET KALEMLERİ DÖKÜMÜ ({res.batch_size} Adet İçin)",
                f"═" * 58,
                f" • Hammadde Bedeli ({res.weight_kg:.3f} kg @ {mat_price:.1f} TL/kg) : {res.material_cost:8.2f} TL / adet",
                f" • CNC Tezgâh Ücreti ({ctime:.1f} dk @ {rate:.0f} TL/saat)   : {res.machine_cost:8.2f} TL / adet",
                f" • Kesici Uç & Takım Aşınma Payı             : {res.tool_cost:8.2f} TL / adet",
                f" • Ayar & İşçilik Amortismanı ({batch} adede bölünmüş) : {res.setup_cost:8.2f} TL / adet",
                f"─" * 58,
                f" • NET BİRİM İMALAT MALİYETİ                  : {res.base_unit_cost:8.2f} TL",
                f" • Kâr Payı (%{markup:.0f})                                : +{res.profit_margin_tl:7.2f} TL",
                f" • BİRİM TEKLİF SATIŞ FİYATI                  : {res.final_unit_price:8.2f} TL",
                f"═" * 58,
                f" TOPLAM PARTİ TEKLİF BEDELİ ({res.batch_size} Adet) : {res.total_batch_price:,.2f} TL",
            ]
            self.txt_breakdown.delete("1.0", "end")
            self.txt_breakdown.insert("1.0", "\n".join(lines))

        except Exception:
            pass

    def _on_export_pdf(self):
        if not self.current_result:
            messagebox.showwarning("Uyarı", "Önce maliyet hesabını çalıştırınız.")
            return

        pdf_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Belgeleri", "*.pdf"), ("Tüm Dosyalar", "*.*")],
            initialfile="fiyat_teklif_mektubu.pdf"
        )
        if pdf_path:
            try:
                rep_data = self.main_app.tabs["REPORTS"].get_report_metadata()
                QuotationReportGenerator.generate_pdf(
                    cost_res=self.current_result,
                    output_pdf_path=pdf_path,
                    customer_name="Sayın Müşteri / Firma Yetkilisi",
                    company_name=rep_data.get("company", "Hassas Talaşlı İmalat Sanayi A.Ş."),
                    prepared_by=rep_data.get("operator", "İmalat ve Fiyatlandırma Sorumlusu")
                )
                messagebox.showinfo("Başarılı", f"Fiyat Teklif Mektubu PDF olarak kaydedildi:\n{pdf_path}")
            except Exception as e:
                messagebox.showerror("Hata", f"PDF oluşturulamadı: {e}")

    def apply_theme(self):
        self.configure(fg_color=COLORS["bg_app"])
        self.top_bar.configure(fg_color=COLORS["card_bg"])
        self.lbl_head.configure(text_color=COLORS["text_primary"])
        self.lbl_guide.configure(text_color=COLORS["text_secondary"])

        self.left_card.configure(fg_color=COLORS["card_bg"])
        self.right_card.configure(fg_color=COLORS["card_bg"])
        self.breakdown_card.configure(fg_color=COLORS["entry_bg"])

        self.lbl_in_t.configure(text_color=COLORS["accent_cyan"])
        self.lbl_p.configure(text_color=COLORS["text_primary"])
        self.lbl_res_t.configure(text_color=COLORS["accent_cyan"])
        self.lbl_bk_t.configure(text_color=COLORS["accent_cyan"])

        for ent in [self.entry_part, self.entry_dia, self.entry_len, self.entry_dens, self.entry_mat_price, self.entry_time, self.entry_rate, self.entry_batch, self.entry_markup]:
            ent.configure(fg_color=COLORS["entry_bg"], text_color=COLORS["text_primary"], border_color=COLORS["entry_border"])

        self.btn_calc.configure(fg_color=COLORS["accent_primary"], hover_color=COLORS["accent_hover"], text_color="#ffffff")
        self.btn_pdf.configure(fg_color=COLORS["btn_pdf"], hover_color=COLORS["btn_pdf_hover"], text_color="#ffffff")
        self.btn_pull_gcode.configure(fg_color=COLORS["entry_bg"], hover_color=COLORS["sidebar_hover"], text_color=COLORS["accent_cyan"])
        self.txt_breakdown.configure(fg_color=COLORS["entry_bg"], text_color=COLORS["text_primary"])

        for key, (box, lbl_t, lbl_v) in self.cards.items():
            box.configure(fg_color=COLORS["entry_bg"])
            lbl_t.configure(text_color=COLORS["text_secondary"])
            val_col = COLORS["accent_cyan"] if (key in ["price", "total"]) else COLORS["text_primary"]
            lbl_v.configure(text_color=val_col)
