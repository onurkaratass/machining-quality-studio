"""
ui.tab_feedback
~~~~~~~~~~~~~~~
Kullanıcı İstek, Öneri ve Hata Bildirim (Feedback & Bug Report) Sekmesi.
"""

import urllib.parse
import webbrowser
from tkinter import messagebox
import customtkinter as ctk
from ui.styles import COLORS
from ui.components import ModernPillSwitch


class TabFeedback(ctk.CTkFrame):
    DEVELOPER_EMAIL = "karatasonur172@gmail.com"

    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color=COLORS["bg_app"], corner_radius=0)
        self.main_app = main_app
        self._build_ui()

    def _build_ui(self):
        # 1. Üst Başlık
        self.top_bar = ctk.CTkFrame(self, fg_color=COLORS["card_bg"], corner_radius=12)
        self.top_bar.pack(fill="x", padx=16, pady=(12, 6))

        self.lbl_head = ctk.CTkLabel(
            self.top_bar,
            text="İSTEK, ÖNERİ VE HATA BİLDİRİM MERKEZİ",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.lbl_head.pack(anchor="w", padx=18, pady=(10, 2))

        self.lbl_sub = ctk.CTkLabel(
            self.top_bar,
            text="Uygulamada görmek istediğiniz yeni özellikleri, bulduğunuz bug'ları veya önerilerinizi doğrudan geliştiriciye iletin.",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLORS["text_secondary"],
            wraplength=1050,
            justify="left"
        )
        self.lbl_sub.pack(anchor="w", padx=18, pady=(0, 10))

        # 2. Ana Kart
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        self.card = ctk.CTkFrame(self.content, fg_color=COLORS["card_bg"], corner_radius=14)
        self.card.pack(fill="both", expand=True)

        # Bildirim Türü (Çizgisiz, Kusursuz Modern Kapsül)
        self.lbl_type = ctk.CTkLabel(
            self.card,
            text="Bildirim Türünü Seçiniz:",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["accent_cyan"]
        )
        self.lbl_type.pack(anchor="w", padx=20, pady=(16, 6))

        self.seg_type = ModernPillSwitch(
            self.card,
            values=["💡 Yeni Özellik / İstek", "🐛 Hata Bildirimi (Bug)", "⭐ Genel Görüş & Öneri"],
            default="💡 Yeni Özellik / İstek",
            height=38
        )
        self.seg_type.pack(fill="x", padx=20, pady=(0, 14))

        # Form Alanları
        form = ctk.CTkFrame(self.card, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=(0, 10))

        # Kullanıcı Adı
        self.lbl_sender = ctk.CTkLabel(form, text="Adınız / Firma (İsteğe Bağlı):", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_sender.pack(anchor="w")
        self.entry_sender = ctk.CTkEntry(form, placeholder_text="Örn: Ahmet Yılmaz (CNC Atölyesi)", corner_radius=8, height=38, font=ctk.CTkFont(family="Segoe UI", size=11))
        self.entry_sender.pack(fill="x", pady=(2, 10))

        # Konu Başlığı
        self.lbl_subject = ctk.CTkLabel(form, text="Konu Başlığı:", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_subject.pack(anchor="w")
        self.entry_subject = ctk.CTkEntry(form, placeholder_text="Örn: X-bar Kontrol Kartı eklenebilir mi?", corner_radius=8, height=38, font=ctk.CTkFont(family="Segoe UI", size=11))
        self.entry_subject.pack(fill="x", pady=(2, 10))

        # Mesaj / Açıklama
        self.lbl_body = ctk.CTkLabel(form, text="Detaylı Açıklama / Hata Mesajı:", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=COLORS["text_primary"])
        self.lbl_body.pack(anchor="w")
        self.txt_msg = ctk.CTkTextbox(form, corner_radius=10, height=130, font=ctk.CTkFont(family="Segoe UI", size=11))
        self.txt_msg.pack(fill="x", pady=(2, 14))

        # Alt Butonlar
        btn_box = ctk.CTkFrame(self.card, fg_color="transparent")
        btn_box.pack(fill="x", padx=20, pady=(0, 14))

        self.btn_send = ctk.CTkButton(
            btn_box,
            text="✉️ E-posta ile Gönder",
            corner_radius=10,
            height=42,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            text_color="#ffffff",
            command=self._on_send_email
        )
        self.btn_send.pack(side="left", padx=(0, 10))

        self.btn_copy = ctk.CTkButton(
            btn_box,
            text="📋 Metni Panoya Kopyala",
            corner_radius=10,
            height=42,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=COLORS["entry_bg"],
            hover_color=COLORS["sidebar_hover"],
            text_color=COLORS["text_primary"],
            command=self._on_copy_clipboard
        )
        self.btn_copy.pack(side="left")

        # İletişim Bilgi Kutusu
        self.contact_box = ctk.CTkFrame(self.card, fg_color=COLORS["entry_bg"], corner_radius=10)
        self.contact_box.pack(fill="x", padx=20, pady=(0, 16))

        self.lbl_contact = ctk.CTkLabel(
            self.contact_box,
            text=f"📬 Doğrudan İletişim ve Destek: {self.DEVELOPER_EMAIL}\n"
                 "Tüm hata bildirimleri ve yeni özellik talepleri geliştirici tarafından incelenip sonraki sürümlere eklenmektedir.",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLORS["text_secondary"],
            justify="left"
        )
        self.lbl_contact.pack(anchor="w", padx=14, pady=10)

    def _prepare_message_text(self):
        feedback_type = self.seg_type.get()
        sender = self.entry_sender.get().strip() or "İsimsiz Kullanıcı"
        subject = self.entry_subject.get().strip() or "Geri Bildirim"
        detail = self.txt_msg.get("1.0", "end").strip()

        full_subject = f"[Machining Studio] {feedback_type} - {subject}"
        full_body = (
            f"Bildirim Türü: {feedback_type}\n"
            f"Gönderen: {sender}\n"
            f"Konu: {subject}\n\n"
            f"Detaylı Açıklama:\n{detail}\n\n"
            f"-----------------------------------------\n"
            f"Gönderildiği Uygulama: Machining & Quality Studio Suite"
        )
        return full_subject, full_body

    def _on_send_email(self):
        detail = self.txt_msg.get("1.0", "end").strip()
        if not detail:
            messagebox.showwarning("Eksik Bilgi", "Lütfen bir açıklama veya hata detayı yazınız.")
            return

        subject, body = self._prepare_message_text()
        mailto = f"mailto:{self.DEVELOPER_EMAIL}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"

        try:
            webbrowser.open(mailto)
            messagebox.showinfo("Yönlendirildi", "Varsayılan e-posta uygulamanız açıldı. Gönder butonuna basarak iletebilirsiniz.")
        except Exception as e:
            messagebox.showerror("Hata", f"E-posta istemcisi açılamadı: {e}\nLütfen 'Metni Panoya Kopyala' butonunu kullanınız.")

    def _on_copy_clipboard(self):
        detail = self.txt_msg.get("1.0", "end").strip()
        if not detail:
            messagebox.showwarning("Eksik Bilgi", "Lütfen bir açıklama veya hata detayı yazınız.")
            return

        subject, body = self._prepare_message_text()
        self.clipboard_clear()
        self.clipboard_append(f"Kime: {self.DEVELOPER_EMAIL}\nKonu: {subject}\n\n{body}")
        messagebox.showinfo("Kopyalandı", f"Bildirim metni panoya kopyalandı!\nDoğrudan {self.DEVELOPER_EMAIL} adresine yapıştırıp gönderebilirsiniz.")

    def apply_theme(self):
        self.configure(fg_color=COLORS["bg_app"])
        self.top_bar.configure(fg_color=COLORS["card_bg"])
        self.lbl_head.configure(text_color=COLORS["text_primary"])
        self.lbl_sub.configure(text_color=COLORS["text_secondary"])

        self.card.configure(fg_color=COLORS["card_bg"])
        self.lbl_type.configure(text_color=COLORS["accent_cyan"])
        self.seg_type.update_theme()

        self.lbl_sender.configure(text_color=COLORS["text_primary"])
        self.lbl_subject.configure(text_color=COLORS["text_primary"])
        self.lbl_body.configure(text_color=COLORS["text_primary"])

        self.entry_sender.configure(fg_color=COLORS["entry_bg"], text_color=COLORS["text_primary"], border_color=COLORS["entry_border"])
        self.entry_subject.configure(fg_color=COLORS["entry_bg"], text_color=COLORS["text_primary"], border_color=COLORS["entry_border"])
        self.txt_msg.configure(fg_color=COLORS["entry_bg"], text_color=COLORS["text_primary"], border_color=COLORS["entry_border"])

        self.btn_send.configure(fg_color=COLORS["accent_primary"], hover_color=COLORS["accent_hover"], text_color="#ffffff")
        self.btn_copy.configure(fg_color=COLORS["entry_bg"], hover_color=COLORS["sidebar_hover"], text_color=COLORS["text_primary"])

        self.contact_box.configure(fg_color=COLORS["entry_bg"])
        self.lbl_contact.configure(text_color=COLORS["text_secondary"])
