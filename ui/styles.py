"""
ui.styles
~~~~~~~~~
Apple tarzı modern renk paleti, tipografi ve tema tanımlamaları.
"""

THEMES = {
    "NAVY": {
        "key": "NAVY",
        "name": "Koyu Lacivert",
        "mode": "dark",
        "bg_app": "#0b1329",
        "sidebar_bg": "#111c38",
        "sidebar_btn": "#162344",
        "sidebar_hover": "#1e315f",
        "sidebar_active": "#0071e3",
        "card_bg": "#162344",
        "card_border": "#223561",
        "card_header": "#1b2c56",
        "accent_primary": "#0071e3",
        "accent_hover": "#0077ed",
        "accent_success": "#10b981",
        "accent_warning": "#f59e0b",
        "accent_danger": "#ef4444",
        "accent_cyan": "#38bdf8",
        "text_primary": "#ffffff",
        "text_secondary": "#94a3b8",
        "entry_bg": "#0f172a",
        "entry_border": "#283963",
        "dropdown_bg": "#0f172a",
        "dropdown_menu": "#162344",
        "dropdown_text": "#ffffff",
        "dropdown_hover": "#0071e3",
        "plot_bg": "#0f172a",
        "plot_card": "#162344",
        "plot_text": "#ffffff",
        "plot_grid": "#1e293b",
        "btn_pdf": "#059669",
        "btn_pdf_hover": "#047857",
        "btn_png": "#0284c7",
        "btn_png_hover": "#0369a1",
    },
    "BLACK": {
        "key": "BLACK",
        "name": "Gece Siyahı (OLED)",
        "mode": "dark",
        "bg_app": "#000000",
        "sidebar_bg": "#0a0a0a",
        "sidebar_btn": "#141414",
        "sidebar_hover": "#222222",
        "sidebar_active": "#0071e3",
        "card_bg": "#121212",
        "card_border": "#222222",
        "card_header": "#181818",
        "accent_primary": "#0071e3",
        "accent_hover": "#0077ed",
        "accent_success": "#10b981",
        "accent_warning": "#f59e0b",
        "accent_danger": "#ef4444",
        "accent_cyan": "#38bdf8",
        "text_primary": "#f5f5f7",
        "text_secondary": "#a1a1aa",
        "entry_bg": "#080808",
        "entry_border": "#262626",
        "dropdown_bg": "#080808",
        "dropdown_menu": "#161616",
        "dropdown_text": "#ffffff",
        "dropdown_hover": "#0071e3",
        "plot_bg": "#050505",
        "plot_card": "#121212",
        "plot_text": "#ffffff",
        "plot_grid": "#222222",
        "btn_pdf": "#059669",
        "btn_pdf_hover": "#047857",
        "btn_png": "#0284c7",
        "btn_png_hover": "#0369a1",
    },
    "LIGHT": {
        "key": "LIGHT",
        "name": "Açık Beyaz (Apple Clean)",
        "mode": "light",
        "bg_app": "#f5f5f7",
        "sidebar_bg": "#ffffff",
        "sidebar_btn": "#f2f2f7",
        "sidebar_hover": "#e5e5ea",         # Açık temada yumuşak gri hover
        "sidebar_active": "#0071e3",
        "card_bg": "#ffffff",
        "card_border": "#e5e5ea",
        "card_header": "#fbfbfd",
        "accent_primary": "#0071e3",
        "accent_hover": "#0077ed",
        "accent_success": "#16a34a",
        "accent_warning": "#d97706",
        "accent_danger": "#dc2626",
        "accent_cyan": "#0071e3",
        "text_primary": "#1d1d1f",
        "text_secondary": "#6e6e73",
        "entry_bg": "#fbfbfd",
        "entry_border": "#d1d1d6",
        "dropdown_bg": "#f2f2f7",
        "dropdown_menu": "#ffffff",
        "dropdown_text": "#1d1d1f",
        "dropdown_hover": "#0071e3",
        "plot_bg": "#ffffff",
        "plot_card": "#ffffff",
        "plot_text": "#1d1d1f",
        "plot_grid": "#e5e5ea",
        "btn_pdf": "#059669",
        "btn_pdf_hover": "#047857",
        "btn_png": "#0284c7",
        "btn_png_hover": "#0369a1",
    }
}

CURRENT_THEME_KEY = "NAVY"
COLORS = dict(THEMES[CURRENT_THEME_KEY])


def switch_theme(theme_key: str):
    global CURRENT_THEME_KEY
    if theme_key in THEMES:
        CURRENT_THEME_KEY = theme_key
        COLORS.clear()
        COLORS.update(THEMES[theme_key])

FONTS = {
    "family": "Segoe UI",
    "mono": "Consolas",
    "title": ("Segoe UI", 14, "bold"),
    "header": ("Segoe UI", 12, "bold"),
    "body": ("Segoe UI", 10),
    "small": ("Segoe UI", 9),
}
