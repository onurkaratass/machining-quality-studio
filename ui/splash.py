"""
ui.splash
~~~~~~~~~
Apple tarzı açılış ekranı: Büyüyüp küçülen (bounce) logo ve yumuşak saydamlaşma (fade-out) geçişi.
"""

import math
import os
import tkinter as tk
from PIL import Image, ImageTk


class AnimatedSplashScreen:
    """
    Uygulama açılışında siyah ekranda logoyu büyütüp küçülten (bounce)
    ve ardından ekranı yumuşakça soldurarak (fade-out) ana pencereyi açan animasyon motoru.
    """

    def __init__(self, root, on_complete_callback):
        self.root = root
        self.on_complete = on_complete_callback

        # Ana pencereyi başlangıçta gizle
        self.root.withdraw()

        # Kenarlıksız bağımsız splash penceresi
        self.splash = tk.Toplevel(self.root)
        self.splash.overrideredirect(True)
        self.splash.configure(bg="#000000")

        # Ekranın tam ortasına yerleştir
        self.width = 500
        self.height = 360
        sw = self.splash.winfo_screenwidth()
        sh = self.splash.winfo_screenheight()
        x = max(0, (sw - self.width) // 2)
        y = max(0, (sh - self.height) // 2)
        self.splash.geometry(f"{self.width}x{self.height}+{x}+{y}")

        # Çizim tuvali
        self.canvas = tk.Canvas(
            self.splash,
            width=self.width,
            height=self.height,
            bg="#000000",
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Orijinal logoyu yükle (Büyütülmüş ve şeffaf zeminli)
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
        logo_path = os.path.join(assets_dir, "logo.png")
        self.base_logo = None
        if os.path.exists(logo_path):
            try:
                self.base_logo = Image.open(logo_path).convert("RGBA")
            except Exception:
                self.base_logo = None

        self.step = 0
        self.total_bounce_steps = 26
        self.center_x = self.width // 2
        self.center_y = self.height // 2 - 25

        self._animate_bounce()

    def _ease_bounce(self, t: float) -> float:
        """Sönümlü yay/zıplama fonksiyonu (0.0 -> 1.15 -> 1.0)"""
        return 1.0 - math.exp(-6.5 * t) * math.cos(10.0 * t)

    def _render_frame(self, scale: float):
        self.canvas.delete("all")
        if scale <= 0.05:
            return

        cx, cy = self.center_x, self.center_y
        base_size = 170
        curr_size = int(base_size * scale)

        if self.base_logo and curr_size > 5:
            try:
                resized = self.base_logo.resize((curr_size, curr_size), Image.Resampling.LANCZOS)
                self.tk_logo = ImageTk.PhotoImage(resized)
                self.canvas.create_image(cx, cy, image=self.tk_logo, anchor="center")
            except Exception:
                self._draw_vector_fallback(cx, cy, scale)
        else:
            self._draw_vector_fallback(cx, cy, scale)

        # Tipografi (Apple Minimalizm)
        if scale > 0.6:
            self.canvas.create_text(
                cx, cy + 105,
                text="MACHINING & QUALITY STUDIO",
                fill="#ffffff",
                font=("Segoe UI", 12, "bold")
            )
            self.canvas.create_text(
                cx, cy + 128,
                text="Precision Manufacturing & Process Capability Engine",
                fill="#86868b",
                font=("Segoe UI", 8)
            )

    def _draw_vector_fallback(self, cx, cy, scale):
        r = 60 * scale
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#38bdf8", width=max(1, int(4 * scale)))
        self.canvas.create_oval(cx - r/3, cy - r/3, cx + r/3, cy + r/3, fill="#ffffff", outline="")

    def _animate_bounce(self):
        if self.step <= self.total_bounce_steps:
            t = self.step / float(self.total_bounce_steps)
            scale = self._ease_bounce(t)
            self._render_frame(scale)
            self.step += 1
            self.splash.after(16, self._animate_bounce)
        else:
            self.splash.after(220, self._start_fadeout)

    def _start_fadeout(self):
        self.fade_steps = 10
        self.fade_current = 0
        self._animate_fade()

    def _animate_fade(self):
        if self.fade_current <= self.fade_steps:
            alpha = max(0.0, 1.0 - (self.fade_current / float(self.fade_steps)))
            try:
                self.splash.wm_attributes("-alpha", alpha)
            except Exception:
                pass
            self.fade_current += 1
            self.splash.after(20, self._animate_fade)
        else:
            self.splash.destroy()
            self.root.deiconify()
            try:
                self.root.wm_attributes("-alpha", 1.0)
            except Exception:
                pass
            self.root.lift()
            self.on_complete()
