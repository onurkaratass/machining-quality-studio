"""
main.py
~~~~~~~
Machining & Quality Studio Ana Başlatıcısı (CustomTkinter + Apple Tarzı Splash Ekranı).
"""

import sys
import os

# CustomTkinter otomatik kontrol ve yükleme
try:
    import customtkinter as ctk
except ImportError:
    import subprocess
    print("[+] Modern CustomTkinter arayüz kütüphanesi yükleniyor, lütfen bekleyin...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
        import customtkinter as ctk
    except Exception as e:
        print(f"[!] Otomatik yükleme yapılamadı: {e}")
        print("Lütfen terminalde 'pip install customtkinter' komutunu çalıştırınız.")

from ui.main_window import MainWindow
from ui.splash import AnimatedSplashScreen


def main():
    app = MainWindow()

    # Uygulama ikonunu ayarla (Şeffaf zeminli logo)
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "logo_64.png")
    if os.path.exists(icon_path):
        try:
            from PIL import ImageTk, Image
            pil_img = Image.open(icon_path)
            tk_img = ImageTk.PhotoImage(pil_img)
            app.iconphoto(True, tk_img)
        except Exception:
            pass

    # Apple tarzı zıplayan logo ve solma animasyonlu açılış ekranı (Splash Screen)
    def on_splash_finish():
        pass

    AnimatedSplashScreen(app, on_splash_finish)

    app.mainloop()


if __name__ == "__main__":
    main()
