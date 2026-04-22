"""
pdf_generator.py — Stately Editorial medical report builder (ReportLab).
Assembled in 4 steps: styles (pdf_styles.py), page components, content blocks, main builder.
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
    TableStyle, HRFlowable, KeepTogether,
)
from reportlab.platypus.flowables import Flowable

from .pdf_styles import (
    PAPER, PAPER_ALT, CARD, INK, INK_SUB, INK_MUTED, RULE, RULE_SOFT,
    ACCENT, ACCENT_DARK, ACCENT_LIGHT,
    STATUS_NORMAL, STATUS_NORMAL_BG, STATUS_LOW, STATUS_LOW_BG,
    STATUS_HIGH, STATUS_HIGH_BG, STATUS_CRITICAL, STATUS_CRIT_BG,
    make_styles, status_pill, severity_colour,
)

W, H = A4          # 595.28 x 841.89 pt
ML = 18 * mm       # left margin
MR = 18 * mm       # right margin
MT = 18 * mm       # top margin
MB = 18 * mm       # bottom margin
CW = W - ML - MR   # content width


# ── Page callback ───────────────────────────────────────────────

def on_page(canvas, doc):
    """Warm sand page background + running footer on every page."""
    canvas.saveState()
    canvas.setFillColor(PAPER)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)

    # Footer rule
    footer_y = MB - 4 * mm
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(ML, footer_y + 6, W - MR, footer_y + 6)

    # Footer text
    canvas.setFont("Courier", 8)
    canvas.setFillColor(INK_MUTED)
    canvas.drawString(ML, footer_y, "Gamalathge Healthcare  ·  Confidential")
    page_num = f"Page {doc.page}"
    canvas.drawRightString(W - MR, footer_y, page_num)
    canvas.restoreState()


# ── Wordmark row ────────────────────────────────────────────────

def wordmark_row(chapter_label: str = "") -> list:
    """Clinic name left, chapter label right — sits at top of cover page."""
    ST = make_styles()
    data = [[
        Paragraph("Gamalathge Healthcare", ST["wordmark"]),
        Paragraph(chapter_label.upper(), ST["wordmark_right"]),
    ]]
    t = Table(data, colWidths=[CW * 0.65, CW * 0.35])
    t.setStyle(TableStyle([
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
    ]))
    return [
        t,
        HRFlowable(width=CW, thickness=0.5, color=RULE, spaceAfter=8),
    ]


# ── Patient banner ──────────────────────────────────────────────

def patient_banner(patient_info: dict) -> list:
    """Cover patient identity block: 'Prepared for' + large italic name + metadata strip."""
    ST = make_styles()
    name = patient_info.get("name", "Unknown Patient")
    meta_items = [
        ("AGE",      patient_info.get("age", "—")),
        ("SEX",      patient_info.get("sex", "—").capitalize()),
        ("DOB",      patient_info.get("dob", "—")),
        ("ID",       patient_info.get("id", "—")),
        ("DATE",     patient_info.get("report_date", "—")),
    ]

    # Metadata strip: equal columns
    n = len(meta_items)
    col_w = CW / n
    label_row = [Paragraph(k, ST["label"]) for k, _ in meta_items]
    value_row = [Paragraph(str(v), ST["mono_sm"]) for _, v in meta_items]

    meta_table = Table(
        [label_row, value_row],
        colWidths=[col_w] * n,
    )
    meta_table.setStyle(TableStyle([
        ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))

    elems = [
        Spacer(1, 10),
        HRFlowable(width=CW, thickness=1.5, color=ACCENT, spaceAfter=10),
        Paragraph("Prepared for", ST["body_lg_center"]),
        Paragraph(name, ST["display_patient_name"]),
        Spacer(1, 10),
        meta_table,
        HRFlowable(width=CW, thickness=1.5, color=ACCENT, spaceBefore=10, spaceAfter=14),
    ]
    return elems


# ── Section header ──────────────────────────────────────────────

def section_header(n: int, title: str, subtitle: str = "") -> list:
    """§ N marker in terracotta + title + optional italic subtitle + hairline rule."""
    ST = make_styles()
    marker = Paragraph(f"<font color='#{ACCENT.hexval()[2:]}'>§ {n:02d}</font>  {title}",
                       ST["section_title"])
    elems: list = [Spacer(1, 12), marker]
    if subtitle:
        elems.append(Paragraph(subtitle, ST["section_subtitle"]))
    elems.append(HRFlowable(width=CW, thickness=0.5, color=RULE, spaceBefore=2, spaceAfter=8))
    return elems
