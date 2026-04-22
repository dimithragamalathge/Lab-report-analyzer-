"""
pdf_styles.py — Stately Editorial colour palette, typography map, and ParagraphStyle factory.
Warm sand background · Terracotta accent · Deep ink · ReportLab builtins only.
"""
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import Paragraph

# ── Colour palette ─────────────────────────────────────────────
PAPER       = colors.HexColor("#faf6ef")   # warm sand — page background
PAPER_ALT   = colors.HexColor("#f2ecdf")   # deeper sand — alternating rows
CARD        = colors.HexColor("#ffffff")   # white card surfaces
INK         = colors.HexColor("#2a2420")   # deep warm near-black
INK_SUB     = colors.HexColor("#6b6156")   # medium warm brown
INK_MUTED   = colors.HexColor("#a8a095")   # light taupe
RULE        = colors.HexColor("#e3dccb")   # hairline rules
RULE_SOFT   = colors.HexColor("#ebe5d5")   # soft separator

ACCENT      = colors.HexColor("#b85c3e")   # terracotta
ACCENT_DARK = colors.HexColor("#8a3f26")   # deep terracotta
ACCENT_LIGHT= colors.HexColor("#f0ddd2")   # pale terracotta tint

STATUS_NORMAL    = colors.HexColor("#6b8668")
STATUS_NORMAL_BG = colors.HexColor("#e8ede2")
STATUS_LOW       = colors.HexColor("#b5873a")
STATUS_LOW_BG    = colors.HexColor("#f3e9d4")
STATUS_HIGH      = colors.HexColor("#b85c3e")
STATUS_HIGH_BG   = colors.HexColor("#f0ddd2")
STATUS_CRITICAL  = colors.HexColor("#5a2418")
STATUS_CRIT_BG   = colors.HexColor("#e8c3b8")


def make_styles() -> dict:
    """Return all named ParagraphStyles for the Stately Editorial design."""
    return {
        # Display — Times-BoldItalic (Playfair substitute)
        "display_xl": ParagraphStyle(
            "display_xl", fontName="Times-BoldItalic", fontSize=38,
            leading=42, textColor=INK,
        ),
        "display_patient_name": ParagraphStyle(
            "display_patient_name", fontName="Times-BoldItalic", fontSize=32,
            leading=38, textColor=INK, alignment=TA_CENTER,
        ),
        "section_title": ParagraphStyle(
            "section_title", fontName="Times-BoldItalic", fontSize=20,
            leading=24, textColor=INK, spaceAfter=2,
        ),
        "section_subtitle": ParagraphStyle(
            "section_subtitle", fontName="Times-Italic", fontSize=11,
            leading=15, textColor=INK_SUB, spaceAfter=8,
        ),

        # Body — Times-Roman (Source Serif substitute)
        "body": ParagraphStyle(
            "body", fontName="Times-Roman", fontSize=10.5,
            leading=16, textColor=INK,
        ),
        "body_sm": ParagraphStyle(
            "body_sm", fontName="Times-Roman", fontSize=9.5,
            leading=14, textColor=INK,
        ),
        "body_italic": ParagraphStyle(
            "body_italic", fontName="Times-Italic", fontSize=10.5,
            leading=16, textColor=INK_SUB,
        ),
        "body_lg_center": ParagraphStyle(
            "body_lg_center", fontName="Times-Italic", fontSize=13,
            leading=19, textColor=INK_SUB, alignment=TA_CENTER, spaceAfter=4,
        ),

        # Labels — Helvetica (Inter substitute)
        "label": ParagraphStyle(
            "label", fontName="Helvetica", fontSize=8,
            leading=11, textColor=INK_MUTED, letterSpacing=1.6,
        ),
        "label_accent": ParagraphStyle(
            "label_accent", fontName="Helvetica-Bold", fontSize=8,
            leading=11, textColor=ACCENT, letterSpacing=2.0,
        ),
        "label_ink": ParagraphStyle(
            "label_ink", fontName="Helvetica-Bold", fontSize=8.5,
            leading=12, textColor=INK_SUB, letterSpacing=1.4,
        ),
        "label_upper": ParagraphStyle(
            "label_upper", fontName="Helvetica-Bold", fontSize=8,
            leading=11, textColor=ACCENT_DARK, letterSpacing=2.0,
        ),

        # Monospace — Courier (JetBrains Mono substitute)
        "mono": ParagraphStyle(
            "mono", fontName="Courier", fontSize=10.5, leading=14, textColor=INK,
        ),
        "mono_sm": ParagraphStyle(
            "mono_sm", fontName="Courier", fontSize=9, leading=13, textColor=INK_MUTED,
        ),

        # Wordmark
        "wordmark": ParagraphStyle(
            "wordmark", fontName="Times-BoldItalic", fontSize=14,
            leading=18, textColor=INK,
        ),
        "wordmark_right": ParagraphStyle(
            "wordmark_right", fontName="Helvetica", fontSize=9,
            leading=13, textColor=INK_MUTED, letterSpacing=1.5, alignment=TA_RIGHT,
        ),

        # Footer / disclaimer
        "footer": ParagraphStyle(
            "footer", fontName="Times-Italic", fontSize=11,
            leading=14, textColor=INK_SUB,
        ),
        "footer_mono": ParagraphStyle(
            "footer_mono", fontName="Courier", fontSize=9,
            leading=13, textColor=INK_MUTED,
        ),
        "disclaimer": ParagraphStyle(
            "disclaimer", fontName="Times-Italic", fontSize=8.5,
            leading=13, textColor=INK_MUTED,
        ),

        # Signature
        "sig_name": ParagraphStyle(
            "sig_name", fontName="Times-BoldItalic", fontSize=22,
            leading=26, textColor=ACCENT,
        ),
        "sig_title": ParagraphStyle(
            "sig_title", fontName="Helvetica-Bold", fontSize=10,
            leading=14, textColor=INK,
        ),
        "sig_reg": ParagraphStyle(
            "sig_reg", fontName="Helvetica", fontSize=9.5,
            leading=13, textColor=INK_SUB,
        ),
        "sig_date": ParagraphStyle(
            "sig_date", fontName="Courier", fontSize=8.5,
            leading=12, textColor=INK_MUTED,
        ),
    }


# ── Status pill helper ─────────────────────────────────────────

_PILL_MAP = {
    "normal":   ("In range", STATUS_NORMAL,   STATUS_NORMAL_BG),
    "low":      ("Low",      STATUS_LOW,       STATUS_LOW_BG),
    "high":     ("High",     STATUS_HIGH,      STATUS_HIGH_BG),
    "critical": ("Critical", STATUS_CRITICAL,  STATUS_CRIT_BG),
    "mild":     ("Mild",     STATUS_LOW,       STATUS_LOW_BG),
    "moderate": ("Moderate", STATUS_HIGH,      STATUS_HIGH_BG),
    "severe":   ("Severe",   STATUS_CRITICAL,  STATUS_CRIT_BG),
}


def status_pill(status: str) -> Paragraph:
    label, fg, bg = _PILL_MAP.get(status.lower(), ("—", INK_MUTED, PAPER_ALT))
    style = ParagraphStyle(
        "_pill", fontName="Helvetica", fontSize=8, textColor=fg,
        backColor=bg, borderPadding=(2, 6, 2, 6), leading=12,
        alignment=TA_CENTER,
    )
    return Paragraph(label, style)


def severity_colour(severity: str) -> colors.HexColor:
    return {
        "normal":   STATUS_NORMAL,
        "mild":     STATUS_LOW,
        "moderate": STATUS_HIGH,
        "severe":   STATUS_CRITICAL,
        "critical": STATUS_CRITICAL,
    }.get(severity.lower(), INK_MUTED)
