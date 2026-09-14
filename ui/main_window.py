"""
ui.main_window
~~~~~~~~~~~~~~
CustomTkinter tabanlı, Apple estetiğinde modern ana masaüstü penceresi,
G-Kod Simülatörü, Parça Maliyeti, Yüzey Pürüzlülüğü ve Kılavuz Tablosu ile donatılmış tam kapsamlı mühendislik istasyonu.
"""

import os
import customtkinter as ctk
from PIL import Image

from ui.styles import THEMES, CURRENT_THEME_KEY, COLORS, switch_theme
from ui.tab_limits import TabLimitsFits
from ui.tab_machining import TabMachining
from ui.tab_spc import TabSPC
from ui.tab_reports import TabReports
from ui.tab_feedback import TabFeedback
from ui.tab_gcode import TabGCode
from ui.tab_cost import TabCost
from ui.tab_surface import TabSurface
from ui.tab_thread import TabThread


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Machining & Quality Studio - CNC İmalat, Maliyet ve Kalite Mühendisliği İstasyonu")
        self.geometry("1400x900")
        self.minsize(1200, 760)

        # Doğal ve ferah masaüstü ölçeklendirmesi
        ctk.set_widget_scaling(1.10)
        ctk.set_window_scaling(1.0)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.active_tab_key = "SPC"
        self._leave_timer = None

        self._build_layout()

    def _build_layout(self):
        self.configure(fg_color=COLORS["bg_app"])

        # 1. En Üst Başlık Şeridi
        self.top_header = ctk.CTkFrame(self, height=62, corner_radius=0, fg_color=COLORS["sidebar_bg"])
        self.top_header.pack(fill="x", side="top")
        self.top_header.pack_propagate(False)

        # Sol: Şeffaf Büyütülmüş Logo ve Başlık
        brand_frame = ctk.CTkFrame(self.top_header, fg_color="transparent")
        brand_frame.pack(side="left", padx=20, pady=8)

        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
        logo_path = os.path.join(assets_dir, "logo.png")
        if os.path.exists(logo_path):
            try:
                pil_logo = Image.open(logo_path).convert("RGBA")
                self.logo_img = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(38, 38))
                logo_lbl = ctk.CTkLabel(brand_frame, text="", image=self.logo_img)
                logo_lbl.pack(side="left", padx=(0, 12))
            except Exception:
                pass

        self.lbl_title = ctk.CTkLabel(
            brand_frame,
            text="MACHINING & QUALITY STUDIO",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.lbl_title.pack(side="left")

        # Sağ: Hover ile Açılan Kusursuz Tema Seçici
        self._build_hover_theme_menu(self.top_header)

        # 2. Ana Gövde (Sol Sidebar + Sağ İçerik)
        self.body = ctk.CTkFrame(self, corner_radius=0, fg_color=COLORS["bg_app"])
        self.body.pack(fill="both", expand=True)

        # Sol Kenar Çubuğu (Sidebar)
        self.sidebar = ctk.CTkFrame(self.body, width=265, corner_radius=0, fg_color=COLORS["sidebar_bg"])
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # İçerik Alanı
        self.container = ctk.CTkFrame(self.body, corner_radius=0, fg_color=COLORS["bg_app"])
        self.container.pack(side="left", fill="both", expand=True)

        # Tüm Sekmeleri Başlat
        self.tabs = {}
        self.tabs["SPC"] = TabSPC(self.container, self)
        self.tabs["LIMITS"] = TabLimitsFits(self.container, self)
        self.tabs["SURFACE"] = TabSurface(self.container, self)
        self.tabs["MACHINING"] = TabMachining(self.container, self)
        self.tabs["GCODE"] = TabGCode(self.container, self)
        self.tabs["THREAD"] = TabThread(self.container, self)
        self.tabs["COST"] = TabCost(self.container, self)
        self.tabs["REPORTS"] = TabReports(self.container, self)
        self.tabs["FEEDBACK"] = TabFeedback(self.container, self)

        self._build_sidebar_content()

        self.show_tab("SPC")

    def _build_hover_theme_menu(self, parent):
        self.theme_area = ctk.CTkFrame(parent, fg_color="transparent")
        self.theme_area.pack(side="right", padx=20, pady=10)

        self.theme_menu_frame = ctk.CTkFrame(
            self.theme_area,
            fg_color=COLORS["entry_bg"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["card_border"]
        )

        self.btn_theme_light = ctk.CTkButton(
            self.theme_menu_frame,
            text="☀️ Açık",
            width=70,
            height=32,
            corner_radius=12,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="transparent",
            hover_color=COLORS["sidebar_hover"],
            text_color=COLORS["text_primary"],
            command=lambda: self._select_theme("LIGHT")
        )
        self.btn_theme_light.pack(side="left", padx=(6, 2), pady=3)

        self.btn_theme_navy = ctk.CTkButton(
            self.theme_menu_frame,
            text="🌌 Lacivert",
            width=80,
            height=32,
            corner_radius=12,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="transparent",
            hover_color=COLORS["sidebar_hover"],
            text_color=COLORS["text_primary"],
            command=lambda: self._select_theme("NAVY")
        )
        self.btn_theme_navy.pack(side="left", padx=2, pady=3)

        self.btn_theme_black = ctk.CTkButton(
            self.theme_menu_frame,
            text="🌑 Siyah",
            width=70,
            height=32,
            corner_radius=12,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="transparent",
            hover_color=COLORS["sidebar_hover"],
            text_color=COLORS["text_primary"],
            command=lambda: self._select_theme("BLACK")
        )
        self.btn_theme_black.pack(side="left", padx=(2, 6), pady=3)

        # Sabit Dairesel Buton
        self.btn_circle_trigger = ctk.CTkButton(
            self.theme_area,
            text="🎨",
            width=42,
            height=42,
            corner_radius=21,
            font=ctk.CTkFont(family="Segoe UI", size=16),
            fg_color=COLORS["entry_bg"],
            hover_color=COLORS["sidebar_hover"],
            text_color=COLORS["text_primary"],
            border_width=1,
            border_color=COLORS["card_border"],
            cursor="hand2",
            command=self._toggle_theme_menu
        )
        self.btn_circle_trigger.pack(side="right")

        for w in [self.theme_area, self.theme_menu_frame, self.btn_circle_trigger, self.btn_theme_light, self.btn_theme_navy, self.btn_theme_black]:
            w.bind("<Enter>", self._on_hover_enter)
            w.bind("<Leave>", self._on_hover_leave)

    def _on_hover_enter(self, event=None):
        if self._leave_timer:
            self.after_cancel(self._leave_timer)
            self._leave_timer = None
        self._show_theme_menu()

    def _on_hover_leave(self, event=None):
        if self._leave_timer:
            self.after_cancel(self._leave_timer)
        self._leave_timer = self.after(350, self._hide_theme_menu)

    def _show_theme_menu(self):
        if not self.theme_menu_frame.winfo_ismapped():
            self.theme_menu_frame.pack(side="left", padx=(0, 6), before=self.btn_circle_trigger)
            self.btn_circle_trigger.configure(fg_color=COLORS["accent_primary"], text_color="#ffffff")

    def _hide_theme_menu(self):
        if self.theme_menu_frame.winfo_ismapped():
            self.theme_menu_frame.pack_forget()
            self.btn_circle_trigger.configure(fg_color=COLORS["entry_bg"], text_color=COLORS["text_primary"])

    def _toggle_theme_menu(self):
        if self.theme_menu_frame.winfo_ismapped():
            self._hide_theme_menu()
        else:
            self._show_theme_menu()

    def _select_theme(self, theme_key: str):
        self.set_theme(theme_key)
        self._hide_theme_menu()

    def set_theme(self, theme_key: str):
        if theme_key not in THEMES:
            return

        switch_theme(theme_key)
        ctk.set_appearance_mode(COLORS["mode"])

        self.configure(fg_color=COLORS["bg_app"])
        self.top_header.configure(fg_color=COLORS["sidebar_bg"])
        self.lbl_title.configure(text_color=COLORS["text_primary"])
        self.body.configure(fg_color=COLORS["bg_app"])
        self.sidebar.configure(fg_color=COLORS["sidebar_bg"])
        self.container.configure(fg_color=COLORS["bg_app"])

        self.theme_menu_frame.configure(fg_color=COLORS["entry_bg"], border_color=COLORS["card_border"])
        self.btn_circle_trigger.configure(
            fg_color=COLORS["entry_bg"],
            hover_color=COLORS["sidebar_hover"],
            text_color=COLORS["text_primary"],
            border_color=COLORS["card_border"]
        )

        for btn in [self.btn_theme_light, self.btn_theme_navy, self.btn_theme_black]:
            btn.configure(hover_color=COLORS["sidebar_hover"], text_color=COLORS["text_primary"])

        if theme_key == "LIGHT":
            self.btn_theme_light.configure(fg_color=COLORS["accent_primary"], text_color="#ffffff")
            self.btn_theme_navy.configure(fg_color="transparent")
            self.btn_theme_black.configure(fg_color="transparent")
        elif theme_key == "BLACK":
            self.btn_theme_black.configure(fg_color=COLORS["accent_primary"], text_color="#ffffff")
            self.btn_theme_light.configure(fg_color="transparent")
            self.btn_theme_navy.configure(fg_color="transparent")
        else:
            self.btn_theme_navy.configure(fg_color=COLORS["accent_primary"], text_color="#ffffff")
            self.btn_theme_light.configure(fg_color="transparent")
            self.btn_theme_black.configure(fg_color="transparent")

        for sec in self.section_labels:
            sec.configure(text_color=COLORS["text_secondary"])

        self.footer_card.configure(fg_color=COLORS["card_bg"])
        self.lbl_stat.configure(text_color=COLORS["accent_success"])
        self.lbl_foot_sub.configure(text_color=COLORS["text_secondary"])

        for tab in self.tabs.values():
            if hasattr(tab, "apply_theme"):
                tab.apply_theme()

        self._refresh_sidebar_buttons()

    def _build_sidebar_content(self):
        self.nav_buttons = {}
        self.section_labels = []

        # Kategori 1: Kalite & Tolerans
        sec1 = ctk.CTkLabel(
            self.sidebar,
            text="KALİTE & TOLERANS",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=COLORS["text_secondary"]
        )
        sec1.pack(anchor="w", padx=20, pady=(14, 2))
        self.section_labels.append(sec1)

        self._add_nav_button("📊 SPC Kalite Analizi", "SPC")
        self._add_nav_button("📐 ISO 286 Tolerans & Geçme", "LIMITS")
        self._add_nav_button("✨ Yüzey Pürüzlülüğü (Ra)", "SURFACE")

        # Kategori 2: İmalat & Tezgâh Hesapları
        sec2 = ctk.CTkLabel(
            self.sidebar,
            text="İMALAT & TEZGÂH HESAPLARI",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=COLORS["text_secondary"]
        )
        sec2.pack(anchor="w", padx=20, pady=(12, 2))
        self.section_labels.append(sec2)

        self._add_nav_button("⚙️ CNC Kesme & Güç", "MACHINING")
        self._add_nav_button("🛠️ CNC G-Kod & Strok", "GCODE")
        self._add_nav_button("🔩 Diş & Kılavuz Tablosu", "THREAD")
        self._add_nav_button("💰 Parça Maliyeti & Teklif", "COST")

        # Kategori 3: Kurumsal & Destek
        sec3 = ctk.CTkLabel(
            self.sidebar,
            text="KURUMSAL & DESTEK",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=COLORS["text_secondary"]
        )
        sec3.pack(anchor="w", padx=20, pady=(12, 2))
        self.section_labels.append(sec3)

        self._add_nav_button("📄 Kalite Raporu & FAI", "REPORTS")
        self._add_nav_button("💬 İstek & Hata Bildirimi", "FEEDBACK")

        # Alt Bilgi Kartı
        self.footer_card = ctk.CTkFrame(self.sidebar, fg_color=COLORS["card_bg"], corner_radius=10)
        self.footer_card.pack(side="bottom", fill="x", padx=14, pady=12)

        self.lbl_stat = ctk.CTkLabel(
            self.footer_card,
            text="🟢 Sistem: Hazır (v1.3 Suite)",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=COLORS["accent_success"]
        )
        self.lbl_stat.pack(anchor="w", padx=12, pady=(6, 1))

        self.lbl_foot_sub = ctk.CTkLabel(
            self.footer_card,
            text="Destek: karatasonur172@gmail.com",
            font=ctk.CTkFont(family="Segoe UI", size=8),
            text_color=COLORS["text_secondary"]
        )
        self.lbl_foot_sub.pack(anchor="w", padx=12, pady=(0, 6))

    def _add_nav_button(self, text, key):
        btn = ctk.CTkButton(
            self.sidebar,
            text=f"  {text}",
            anchor="w",
            corner_radius=10,
            height=38,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="transparent",
            text_color=COLORS["text_primary"],
            hover_color=COLORS["sidebar_hover"],
            command=lambda k=key: self.show_tab(k)
        )
        btn.pack(fill="x", padx=10, pady=2)
        self.nav_buttons[key] = btn

    def _refresh_sidebar_buttons(self):
        for key, btn in self.nav_buttons.items():
            if key == self.active_tab_key:
                btn.configure(
                    fg_color=COLORS["sidebar_active"],
                    text_color="#ffffff",
                    hover_color=COLORS["accent_hover"]
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["text_primary"],
                    hover_color=COLORS["sidebar_hover"]
                )

    def show_tab(self, tab_key: str):
        self.active_tab_key = tab_key
        self._refresh_sidebar_buttons()

        for key, tab_widget in self.tabs.items():
            if key == tab_key:
                tab_widget.pack(fill="both", expand=True)
            else:
                tab_widget.pack_forget()

    def switch_to_spc_with_limits(self, part_name: str, nominal: float, usl: float, lsl: float):
        self.show_tab("SPC")
        self.tabs["SPC"].load_limits_from_fit(part_name, nominal, usl, lsl)
