"""
ui.components
~~~~~~~~~~~~~
Yüksek kaliteli modern UI bileşenleri, animasyonlu butonlar, placeholder alanları
ve beyaz çizgi hatası vermeyen Apple tarzı ModernPillSwitch kapsül seçici.
"""

import customtkinter as ctk
from ui.styles import COLORS


class ModernPillSwitch(ctk.CTkFrame):
    """
    CTkSegmentedButton'daki beyaz çizgi ve çerçeve bozulmalarını tamamen yok eden,
    gerçek Apple tarzı pürüzsüz kapsül buton bileşeni.
    """

    def __init__(self, master, values, command=None, default=None, height=38, **kwargs):
        super().__init__(master, fg_color=COLORS["entry_bg"], corner_radius=10, height=height, **kwargs)
        self.values = values
        self.command = command
        self.selected_value = default or values[0]
        self.buttons = {}

        self.inner_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.inner_frame.pack(fill="both", expand=True, padx=3, pady=3)

        for val in values:
            is_active = (val == self.selected_value)
            btn = ctk.CTkButton(
                self.inner_frame,
                text=val,
                height=height - 6,
                corner_radius=8,
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                fg_color=COLORS["accent_primary"] if is_active else "transparent",
                hover_color=COLORS["accent_hover"] if is_active else COLORS["sidebar_hover"],
                text_color="#ffffff" if is_active else COLORS["text_secondary"],
                command=lambda v=val: self._on_btn_click(v)
            )
            btn.pack(side="left", fill="both", expand=True, padx=2)
            self.buttons[val] = btn

    def _on_btn_click(self, val):
        self.selected_value = val
        self._refresh()
        if self.command:
            self.command(val)

    def set(self, val):
        if val in self.values:
            self.selected_value = val
            self._refresh()

    def get(self):
        return self.selected_value

    def _refresh(self):
        for val, btn in self.buttons.items():
            is_active = (val == self.selected_value)
            btn.configure(
                fg_color=COLORS["accent_primary"] if is_active else "transparent",
                hover_color=COLORS["accent_hover"] if is_active else COLORS["sidebar_hover"],
                text_color="#ffffff" if is_active else COLORS["text_secondary"]
            )

    def update_theme(self):
        self.configure(fg_color=COLORS["entry_bg"])
        self._refresh()
