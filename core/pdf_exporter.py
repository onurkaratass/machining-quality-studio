from core.machining_calc import CostResult
"""
core.pdf_exporter
~~~~~~~~~~~~~~~~~
ReportLab tabanlı, Unicode ve Türkçe karakter (%100 UTF-8) destekli kurumsal PDF Kalite Sertifikası üretici.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from core.spc_engine import SPCResult


def _ensure_unicode_fonts():
    """Sistemdeki Unicode TTF yazı tipini bulup ReportLab'e tanıtır (Türkçe harf desteği için)."""
    try:
        pdfmetrics.getFont("AppUnicode")
        return "AppUnicode", "AppUnicode-Bold"
    except KeyError:
        pass

    reg_candidates = [
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\segui.ttf",
        "C:\\Windows\\Fonts\\tahoma.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf"
    ]
    bold_candidates = [
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\seguibd.ttf",
        "C:\\Windows\\Fonts\\tahomabd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    ]

    r_path = next((p for p in reg_candidates if os.path.exists(p)), None)
    b_path = next((p for p in bold_candidates if os.path.exists(p)), None)

    if r_path:
        pdfmetrics.registerFont(TTFont("AppUnicode", r_path))
    else:
        return "Helvetica", "Helvetica-Bold"

    if b_path:
        pdfmetrics.registerFont(TTFont("AppUnicode-Bold", b_path))
    else:
        pdfmetrics.registerFont(TTFont("AppUnicode-Bold", r_path))

    return "AppUnicode", "AppUnicode-Bold"


class QualityReportGenerator:
    @staticmethod
    def generate_pdf(
        result: SPCResult,
        plot_image_path: str,
        output_pdf_path: str,
        part_name: str = "Hassas CNC Şaftı",
        machine_code: str = "CNC-LATHE-01",
        operator_name: str = "Kalite Kontrol Sorumlusu",
        company_name: str = "Hassas Talaşlı İmalat Sanayi ve Ticaret A.Ş."
    ) -> str:
        font_reg, font_bold = _ensure_unicode_fonts()

        doc = SimpleDocTemplate(
            output_pdf_path,
            pagesize=A4,
            rightMargin=1.2 * cm,
            leftMargin=1.2 * cm,
            topMargin=1.0 * cm,
            bottomMargin=1.0 * cm
        )

        elements = []

        # Başlık Stilleri (Unicode Fontlarla)
        header_style = ParagraphStyle(
            name='HeaderStyle',
            fontName=font_bold,
            fontSize=15,
            leading=19,
            textColor=colors.HexColor('#0f172a'),
            alignment=1
        )
        sub_style = ParagraphStyle(
            name='SubStyle',
            fontName=font_reg,
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#475569'),
            alignment=1
        )
        section_title = ParagraphStyle(
            name='SectionTitle',
            fontName=font_bold,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#1e293b')
        )
        cell_style = ParagraphStyle(
            name='CellStyle',
            fontName=font_reg,
            fontSize=8,
            leading=11,
            textColor=colors.HexColor('#1e293b')
        )
        cell_bold = ParagraphStyle(
            name='CellBold',
            fontName=font_bold,
            fontSize=8,
            leading=11,
            textColor=colors.HexColor('#0f172a')
        )

        # 1. Başlık Alanı
        elements.append(Paragraph(company_name.upper(), header_style))
        elements.append(Spacer(1, 0.1 * cm))
        elements.append(Paragraph("PROSES YETERLİLİK VE İLK PARÇA ONAY SERTİFİKASI (SPC / FAI REPORT)", sub_style))
        elements.append(Spacer(1, 0.4 * cm))

        # 2. Üst Bilgi Kartı Tablosu
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        meta_data = [
            [
                Paragraph("<b>İş Parçası Adı:</b>", cell_style), Paragraph(part_name, cell_bold),
                Paragraph("<b>Tarih / Saat:</b>", cell_style), Paragraph(now_str, cell_bold)
            ],
            [
                Paragraph("<b>Tezgâh / İstasyon:</b>", cell_style), Paragraph(machine_code, cell_bold),
                Paragraph("<b>İnceleyen Sorumlu:</b>", cell_style), Paragraph(operator_name, cell_bold)
            ],
            [
                Paragraph("<b>Nominal Ölçü:</b>", cell_style), Paragraph(f"{result.nominal:.4f} mm", cell_bold),
                Paragraph("<b>Tolerans Limitleri:</b>", cell_style), Paragraph(f"{result.lsl:.4f} / {result.usl:.4f} mm", cell_bold)
            ]
        ]
        t_meta = Table(meta_data, colWidths=[3.4*cm, 5.8*cm, 3.8*cm, 5.5*cm])
        t_meta.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(t_meta)
        elements.append(Spacer(1, 0.35 * cm))

        # 3. İstatistik ve Yeterlilik Özeti Tablosu
        stat_color = colors.HexColor('#16a34a') if result.cpk >= 1.33 else colors.HexColor('#dc2626')
        stats_data = [
            [
                Paragraph("<b>Örneklem (N)</b>", cell_style),
                Paragraph("<b>Ortalama (X̄)</b>", cell_style),
                Paragraph("<b>Std. Sapma (s)</b>", cell_style),
                Paragraph("<b>Potansiyel (Cp)</b>", cell_style),
                Paragraph("<b>Fiili (Cpk)</b>", cell_style),
                Paragraph("<b>Fire Oranı (PPM)</b>", cell_style)
            ],
            [
                Paragraph(str(result.sample_size), cell_bold),
                Paragraph(f"{result.mean:.4f} mm", cell_bold),
                Paragraph(f"{result.std_dev:.4f} mm", cell_bold),
                Paragraph(f"{result.cp:.3f}", cell_bold),
                Paragraph(f"<font color='{stat_color.hexval()}'><b>{result.cpk:.3f}</b></font>", cell_bold),
                Paragraph(f"{result.ppm_total:.1f} PPM", cell_bold)
            ]
        ]
        t_stats = Table(stats_data, colWidths=[3.1*cm, 3.1*cm, 3.1*cm, 3.1*cm, 3.1*cm, 3.1*cm])
        t_stats.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#ffffff')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(t_stats)
        elements.append(Spacer(1, 0.35 * cm))

        # 4. Grafik Alanı
        if os.path.exists(plot_image_path):
            elements.append(Paragraph("PROSES DAĞILIMI, GAUSS EĞRİSİ VE SPESİFİKASYON LİMİTLERİ", section_title))
            elements.append(Spacer(1, 0.15 * cm))
            elements.append(Image(plot_image_path, width=18.5 * cm, height=8.6 * cm))
            elements.append(Spacer(1, 0.35 * cm))

        # 5. Otomatik Tezgâh Teşhisi ve Karar
        diag_data = [
            [
                Paragraph("<b>TEŞHİS VE İMALAT AKSİYONU:</b>", cell_bold),
                Paragraph(result.diagnosis_note, cell_style)
            ],
            [
                Paragraph("<b>GENEL DEĞERLENDİRME:</b>", cell_bold),
                Paragraph(f"<b>{result.status.value}</b>", cell_bold)
            ]
        ]
        t_diag = Table(diag_data, colWidths=[6.5*cm, 12.0*cm])
        t_diag.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(t_diag)
        elements.append(Spacer(1, 0.45 * cm))

        # 6. Kalite Kontrol Onay / İmza Kutuları
        approval_data = [
            [
                Paragraph("<b>Ölçümü Yapan (Kalite Kontrol)</b>", cell_style),
                Paragraph("<b>İmalat Sorumlusu (Şef / Mühendis)</b>", cell_style),
                Paragraph("<b>Nihai Parti Kararı</b>", cell_style)
            ],
            [
                Paragraph("<br/><br/>İmza: .......................................", cell_style),
                Paragraph("<br/><br/>İmza: .......................................", cell_style),
                Paragraph("<br/>[   ] KABUL<br/>[   ] ŞARTLI KABUL<br/>[   ] RET / HURDA", cell_bold)
            ]
        ]
        t_appr = Table(approval_data, colWidths=[6.2*cm, 6.2*cm, 6.2*cm])
        t_appr.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#94a3b8')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(t_appr)

        doc.build(elements)
        return output_pdf_path


class QuotationReportGenerator:
    @staticmethod
    def generate_pdf(
        cost_res: CostResult,
        output_pdf_path: str,
        customer_name: str = "Müşteri / Firma Adı",
        company_name: str = "Hassas Talaşlı İmalat Sanayi ve Ticaret A.Ş.",
        prepared_by: str = "İmalat ve Fiyatlandırma Birimi",
        lead_time_days: int = 7
    ) -> str:
        font_reg, font_bold = _ensure_unicode_fonts()
        doc = SimpleDocTemplate(
            output_pdf_path,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.2 * cm,
            bottomMargin=1.2 * cm
        )
        elements = []

        header_style = ParagraphStyle('HeadQ', fontName=font_bold, fontSize=16, leading=20, textColor=colors.HexColor('#0f172a'), alignment=1)
        sub_style = ParagraphStyle('SubQ', fontName=font_reg, fontSize=9, leading=12, textColor=colors.HexColor('#475569'), alignment=1)
        cell_style = ParagraphStyle('CellQ', fontName=font_reg, fontSize=9, leading=12, textColor=colors.HexColor('#1e293b'))
        cell_bold = ParagraphStyle('CellQB', fontName=font_bold, fontSize=9, leading=12, textColor=colors.HexColor('#0f172a'))
        price_bold = ParagraphStyle('PriceQB', fontName=font_bold, fontSize=12, leading=15, textColor=colors.HexColor('#0071e3'))

        elements.append(Paragraph(company_name.upper(), header_style))
        elements.append(Spacer(1, 0.1 * cm))
        elements.append(Paragraph("TALAŞLI İMALAT FİYAT TEKLİF MEKTUBU (MACHINING QUOTATION)", sub_style))
        elements.append(Spacer(1, 0.5 * cm))

        now_str = datetime.now().strftime("%Y-%m-%d")
        meta_data = [
            [Paragraph("<b>Teklif Verilen Firma:</b>", cell_style), Paragraph(customer_name, cell_bold),
             Paragraph("<b>Teklif Tarihi:</b>", cell_style), Paragraph(now_str, cell_bold)],
            [Paragraph("<b>İş Parçası Adı:</b>", cell_style), Paragraph(cost_res.part_name, cell_bold),
             Paragraph("<b>Teslim Süresi:</b>", cell_style), Paragraph(f"{lead_time_days} İş Günü", cell_bold)],
            [Paragraph("<b>Parti Adedi (Sipariş):</b>", cell_style), Paragraph(f"{cost_res.batch_size} Adet", cell_bold),
             Paragraph("<b>Hazırlayan:</b>", cell_style), Paragraph(prepared_by, cell_bold)]
        ]
        t_meta = Table(meta_data, colWidths=[4.0*cm, 5.5*cm, 3.5*cm, 5.0*cm])
        t_meta.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(t_meta)
        elements.append(Spacer(1, 0.5 * cm))

        # Maliyet Detay Tablosu
        breakdown_data = [
            [Paragraph("<b>Maliyet Kalemi / Açıklama</b>", cell_bold), Paragraph("<b>Birim Tutar</b>", cell_bold), Paragraph("<b>Parti Toplamı</b>", cell_bold)],
            [Paragraph(f"Hammadde Bedeli ({cost_res.weight_kg:.2f} kg / adet)", cell_style), Paragraph(f"{cost_res.material_cost:.2f} TL", cell_style), Paragraph(f"{cost_res.material_cost * cost_res.batch_size:.2f} TL", cell_style)],
            [Paragraph("CNC Tezgâh İşleme Ücreti", cell_style), Paragraph(f"{cost_res.machine_cost:.2f} TL", cell_style), Paragraph(f"{cost_res.machine_cost * cost_res.batch_size:.2f} TL", cell_style)],
            [Paragraph("Takım Aşınma & Kesici Uç Maliyeti", cell_style), Paragraph(f"{cost_res.tool_cost:.2f} TL", cell_style), Paragraph(f"{cost_res.tool_cost * cost_res.batch_size:.2f} TL", cell_style)],
            [Paragraph("Tezgâh Ayar & İşçilik Payı", cell_style), Paragraph(f"{cost_res.setup_cost:.2f} TL", cell_style), Paragraph(f"{cost_res.setup_cost * cost_res.batch_size:.2f} TL", cell_style)],
            [Paragraph("<b>Net Birim İmalat Maliyeti:</b>", cell_bold), Paragraph(f"<b>{cost_res.base_unit_cost:.2f} TL</b>", cell_bold), Paragraph(f"<b>{cost_res.base_unit_cost * cost_res.batch_size:.2f} TL</b>", cell_bold)],
            [Paragraph("<b>FİNAL TEKLİF FİYATI (KÂR DAHİL):</b>", cell_bold), Paragraph(f"<b>{cost_res.final_unit_price:.2f} TL</b>", price_bold), Paragraph(f"<b>{cost_res.total_batch_price:.2f} TL</b>", price_bold)],
        ]
        t_break = Table(breakdown_data, colWidths=[9.0*cm, 4.5*cm, 4.5*cm])
        t_break.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#eff6ff')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(t_break)
        elements.append(Spacer(1, 0.8 * cm))

        # Şartlar ve Onay
        terms_text = (
            "<b>Teklif Koşulları:</b><br/>"
            "1. Bu teklif hazırlandığı tarihten itibaren 15 takvim günü boyunca geçerlidir.<br/>"
            "2. Fiyatlara KDV dahil değildir.<br/>"
            "3. Teslimat işbu teklifin onaylanmasını ve hammadde teminini takiben başlar.<br/>"
            "4. İmalat ISO 9001 kalite standartlarına ve teknik resim toleranslarına uygun olarak gerçekleştirilecektir."
        )
        elements.append(Paragraph(terms_text, cell_style))
        elements.append(Spacer(1, 1.0 * cm))

        sign_data = [
            [Paragraph("<b>Teklifi Hazırlayan (Firma Yetkilisi)</b>", cell_style), Paragraph("<b>Teklifi Onaylayan (Müşteri Yetkilisi)</b>", cell_style)],
            [Paragraph("<br/><br/>İmza / Kaşe: ...................................", cell_style), Paragraph("<br/><br/>İmza / Kaşe: ...................................", cell_style)]
        ]
        t_sign = Table(sign_data, colWidths=[9.0*cm, 9.0*cm])
        t_sign.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#94a3b8')),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(t_sign)

        doc.build(elements)
        return output_pdf_path
