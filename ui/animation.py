"""
ui.animation
~~~~~~~~~~~~
CustomTkinter için yumuşak renk geçişleri (Color Morphing),
kayan menü (Slide-out) ve buton tıklama animasyon motoru.
"""

def hex_to_rgb(hex_str: str) -> tuple:
    hex_str = hex_str.lstrip("#")
    if len(hex_str) == 3:
        hex_str = "".join([c*2 for c in hex_str])
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple) -> str:
    return "#{:02x}{:02x}{:02x}".format(
        max(0, min(255, int(rgb[0]))),
        max(0, min(255, int(rgb[1]))),
        max(0, min(255, int(rgb[2])))
    )


def interpolate_hex(hex1: str, hex2: str, factor: float) -> str:
    """İki renk arasında faktöre (0.0 - 1.0) göre ara RGB rengini hesaplar."""
    try:
        r1, g1, b1 = hex_to_rgb(hex1)
        r2, g2, b2 = hex_to_rgb(hex2)
        r = r1 + (r2 - r1) * factor
        g = g1 + (g2 - g1) * factor
        b = b1 + (b2 - b1) * factor
        return rgb_to_hex((r, g, b))
    except Exception:
        return hex2


class ThemeColorMorph:
    """
    Tema değişimlerinde sert renk parlamasını önleyip renkleri
    kademeli (morph) olarak yumuşatan animasyon kontrolcüsü.
    """

    @staticmethod
    def morph(root_widget, widgets_to_color, on_step_callback, on_finish_callback, steps=7, interval_ms=20):
        def _step(current_step):
            if current_step <= steps:
                factor = current_step / float(steps)
                # Yumuşak ease-out eğrisi: factor = 1 - (1 - factor)^2
                eased = 1.0 - (1.0 - factor) ** 2
                on_step_callback(eased)
                root_widget.after(interval_ms, lambda: _step(current_step + 1))
            else:
                on_finish_callback()

        _step(0)
