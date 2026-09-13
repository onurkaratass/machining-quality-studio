"""
app_gui.py
~~~~~~~~~~
SPC İstatistiksel Proses Kontrol Masaüstü Grafik Arayüzü.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy import stats

from spc import CapabilityAnalyzer, CapabilityStatus


class SPCApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SPC Analiz ve Kalite Kontrol Sistemi")
        self.geometry("1180x760")
        self.minsize(1000, 680)

        # Stil Ayarları
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.configure(bg="#f4f6f9")

        self.measurements = []
        self._build_ui()

    def _build_ui(self):
        # Üst Başlık
        header = tk.Frame(self, bg="#1e293b", height=55)
        header.pack(fill=tk.X, side=tk.TOP)
        title_label = tk.Label(
            header,
            text="İSTATİSTİKSEL PROSES KONTROL (SPC) & YETERLİLİK ANALİZÖRÜ",
            font=("Segoe UI", 13, "bold"),
            fg="#ffffff",
            bg="#1e293b",
            padx=20,
            pady=12,
        )
        title_label.pack(side=tk.LEFT)

        # Ana Gövde
        main_pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg="#f4f6f9", sashwidth=4)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Sol Panel (Girdi ve Kontroller)
        left_frame = tk.Frame(main_pane, bg="#ffffff", bd=1, relief=tk.SOLID, padx=14, pady=14)
        main_pane.add(left_frame, width=350)

        # Sağ Panel (Grafik ve Çıktılar)
        right_frame = tk.Frame(main_pane, bg="#ffffff", bd=1, relief=tk.SOLID, padx=10, pady=10)
        main_pane.add(right_frame)

        self._build_inputs(left_frame)
        self._build_outputs(right_frame)

    def _build_inputs(self, parent):
        tk.Label(parent, text="Spesifikasyon ve Veri Girişi", font=("Segoe UI", 11, "bold"), bg="#ffffff", fg="#0f172a").pack(anchor="w", pady=(0, 10))

        # Parça Adı
        tk.Label(parent, text="Parça / Operasyon Adı:", bg="#ffffff", font=("Segoe UI", 9)).pack(anchor="w")
        self.entry_part = ttk.Entry(parent)
        self.entry_part.insert(0, "CNC Torna Mil Çapı (Ø25)")
        self.entry_part.pack(fill=tk.X, pady=(2, 8))

        # Nominal
        tk.Label(parent, text="Nominal Ölçü (mm):", bg="#ffffff", font=("Segoe UI", 9)).pack(anchor="w")
        self.entry_nominal = ttk.Entry(parent)
        self.entry_nominal.insert(0, "25.000")
        self.entry_nominal.pack(fill=tk.X, pady=(2, 8))

        # USL ve LSL
        grid_tol = tk.Frame(parent, bg="#ffffff")
        grid_tol.pack(fill=tk.X, pady=(0, 8))

        tk.Label(grid_tol, text="Alt Limit (LSL):", bg="#ffffff", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
        tk.Label(grid_tol, text="Üst Limit (USL):", bg="#ffffff", font=("Segoe UI", 9)).grid(row=0, column=1, sticky="w", padx=(10, 0))

        self.entry_lsl = ttk.Entry(grid_tol, width=14)
        self.entry_lsl.insert(0, "24.950")
        self.entry_lsl.grid(row=1, column=0, sticky="we", pady=(2, 0))

        self.entry_usl = ttk.Entry(grid_tol, width=14)
        self.entry_usl.insert(0, "25.050")
        self.entry_usl.grid(row=1, column=1, sticky="we", padx=(10, 0), pady=(2, 0))

        # CSV Yükleme Butonu
        btn_csv = tk.Button(parent, text="📁 Ölçüm CSV Dosyası Yükle", bg="#f1f5f9", fg="#0f172a", relief=tk.GROOVE, font=("Segoe UI", 9, "bold"), command=self._load_csv, pady=6)
        btn_csv.pack(fill=tk.X, pady=(10, 5))

        self.lbl_file_status = tk.Label(parent, text="Henüz dosya seçilmedi (Demo verisi hazır)", font=("Segoe UI", 8, "italic"), bg="#ffffff", fg="#64748b")
        self.lbl_file_status.pack(anchor="w")

        # Manuel Veri Kutusu
        tk.Label(parent, text="Veya Değerleri Buraya Yapıştırın (satır satır):", bg="#ffffff", font=("Segoe UI", 8)).pack(anchor="w", pady=(10, 2))
        self.txt_manual = tk.Text(parent, height=7, font=("Consolas", 9), relief=tk.SOLID, bd=1)
        self.txt_manual.pack(fill=tk.X, pady=(0, 10))

        # Örnek Sentetik Veri Doldur
        sample_vals = np.random.normal(25.012, 0.011, 40)
        self.txt_manual.insert("1.0", "\n".join([f"{v:.4f}" for v in sample_vals]))

        # Analiz Butonu
        btn_run = tk.Button(parent, text="⚡ Analizi Başlat", bg="#2563eb", fg="#ffffff", activebackground="#1d4ed8", activeforeground="#ffffff", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, pady=8, command=self._run_analysis)
        btn_run.pack(fill=tk.X, pady=(10, 0))

    def _build_outputs(self, parent):
        # Matplotlib Çizim Alanı
        self.fig = Figure(figsize=(7, 4.2), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Alt Özet Kartları Paneli
        self.cards_frame = tk.Frame(parent, bg="#ffffff", pady=8)
        self.cards_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.card_cp = self._create_card(self.cards_frame, "Cp (Potansiyel)", "--")
        self.card_cpk = self._create_card(self.cards_frame, "Cpk (Fiili)", "--")
        self.card_mean = self._create_card(self.cards_frame, "Ortalama", "--")
        self.card_status = self._create_card(self.cards_frame, "Proses Durumu", "Bekleniyor...", is_wide=True)

    def _create_card(self, parent, title, initial_val, is_wide=False):
        frame = tk.Frame(parent, bg="#f8fafc", bd=1, relief=tk.SOLID, padx=12, pady=6)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        lbl_t = tk.Label(frame, text=title, font=("Segoe UI", 8, "bold"), bg="#f8fafc", fg="#64748b")
        lbl_t.pack(anchor="w")
        lbl_v = tk.Label(frame, text=initial_val, font=("Segoe UI", 11 if not is_wide else 9, "bold"), bg="#f8fafc", fg="#0f172a")
        lbl_v.pack(anchor="w", pady=(2, 0))
        return lbl_v

    def _load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Dosyaları", "*.csv"), ("Tüm Dosyalar", "*.*")])
        if path:
            try:
                df = pd.read_csv(path)
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) == 0:
                    messagebox.showerror("Hata", "CSV içinde sayısal ölçüm sütunu bulunamadı.")
                    return
                vals = df[numeric_cols[0]].dropna().tolist()
                self.txt_manual.delete("1.0", tk.END)
                self.txt_manual.insert("1.0", "\n".join([f"{v:.4f}" for v in vals]))
                self.lbl_file_status.config(text=f"Yüklendi: {len(vals)} numune ({numeric_cols[0]})", fg="#16a34a")
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya okunamadı: {str(e)}")

    def _run_analysis(self):
        try:
            nominal = float(self.entry_nominal.get().strip())
            usl = float(self.entry_usl.get().strip())
            lsl = float(self.entry_lsl.get().strip())
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayısal tolerans değerleri giriniz.")
            return

        raw_text = self.txt_manual.get("1.0", tk.END).strip()
        lines = [line.strip().replace(",", ".") for line in raw_text.splitlines() if line.strip()]
        
        try:
            data = [float(val) for val in lines]
        except ValueError:
            messagebox.showerror("Hata", "Manuel veri kutusundaki tüm satırlar sayı olmalıdır.")
            return

        if len(data) < 2:
            messagebox.showerror("Hata", "Analiz için en az 2 adet ölçüm verisi girilmelidir.")
            return

        try:
            analyzer = CapabilityAnalyzer(nominal=nominal, usl=usl, lsl=lsl)
            result = analyzer.analyze(data)
        except Exception as err:
            messagebox.showerror("Analiz Hatası", str(err))
            return

        # Kartları Güncelle
        self.card_cp.config(text=f"{result.cp:.3f}")
        self.card_cpk.config(text=f"{result.cpk:.3f}", fg="#16a34a" if result.cpk >= 1.33 else "#dc2626")
        self.card_mean.config(text=f"{result.mean:.4f} mm")
        self.card_status.config(text=result.status.value.split("(")[0].strip())

        # Grafiği Çiz
        self._plot(data, result)

    def _plot(self, data, res):
        self.ax.clear()
        arr = np.array(data)

        # Histogram
        self.ax.hist(arr, bins="auto", density=True, alpha=0.55, color="#2b5c8f", edgecolor="#16385c", label="Ölçüm Dağılımı")

        # Gauss Eğrisi
        margin = res.tolerance_span * 0.25
        x_axis = np.linspace(min(res.lsl - margin, min(arr)), max(res.usl + margin, max(arr)), 500)
        pdf = stats.norm.pdf(x_axis, loc=res.mean, scale=res.std_dev)
        self.ax.plot(x_axis, pdf, color="#0f172a", linewidth=2, label="Gauss Eğrisi")

        # Limit Çizgileri
        self.ax.axvline(res.lsl, color="#dc2626", linestyle="--", linewidth=1.8, label="LSL")
        self.ax.axvline(res.usl, color="#dc2626", linestyle="--", linewidth=1.8, label="USL")
        self.ax.axvline(res.nominal, color="#16a34a", linestyle="-", linewidth=1.6, label="Nominal")
        self.ax.axvline(res.mean, color="#ea580c", linestyle=":", linewidth=1.8, label="Ortalama")

        self.ax.set_title(f"{self.entry_part.get()} - Dağılım ve Spesifikasyon Analizi", fontsize=11, fontweight="bold")
        self.ax.legend(loc="upper right", fontsize=8)
        self.ax.grid(True, linestyle="--", alpha=0.4)
        self.fig.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    app = SPCApp()
    app.mainloop()
