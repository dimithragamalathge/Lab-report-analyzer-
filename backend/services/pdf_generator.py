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


# ── Executive summary block ─────────────────────────────────────

def exec_summary_block(text: str, stats: dict) -> list:
    """Warm sand block with terracotta left border + 4-stat strip below."""
    ST = make_styles()

    total    = stats.get("total", 0)
    in_range = stats.get("in_range", 0)
    flagged  = stats.get("flagged", 0)
    critical = stats.get("critical", 0)

    summary_table = Table(
        [[Paragraph(text, ST["body"])]],
        colWidths=[CW - 8],
    )
    summary_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), PAPER_ALT),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBEFORE",    (0, 0), (0, -1), 3, ACCENT),
    ]))

    stat_labels  = ["TOTAL TESTS", "IN RANGE", "FLAGGED", "CRITICAL"]
    stat_values  = [str(total), str(in_range), str(flagged), str(critical)]
    stat_colours = [INK_SUB, STATUS_NORMAL, STATUS_HIGH, STATUS_CRITICAL]

    label_cells = [Paragraph(l, ST["label"]) for l in stat_labels]
    value_cells = [
        Paragraph(f"<font color='#{c.hexval()[2:]}'>{v}</font>", ST["section_title"])
        for v, c in zip(stat_values, stat_colours)
    ]

    stats_table = Table(
        [label_cells, value_cells],
        colWidths=[CW / 4] * 4,
    )
    stats_table.setStyle(TableStyle([
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEABOVE",     (0, 0), (-1, 0), 0.5, RULE),
        ("LINEBELOW",     (0, -1), (-1, -1), 0.5, RULE),
        ("LINEBETWEEN",   (0, 0), (-1, -1), 0.5, RULE_SOFT),
        ("BACKGROUND",    (0, 0), (-1, -1), PAPER_ALT),
    ]))

    return [summary_table, Spacer(1, 4), stats_table, Spacer(1, 14)]


# ── Critical values box ─────────────────────────────────────────

def critical_box(critical_values: list) -> list:
    """Oxblood background box listing critical/panic values."""
    if not critical_values:
        return []

    ST = make_styles()
    white = colors.HexColor("#ffffff")

    header_style = ParagraphStyle(
        "_crit_head", fontName="Helvetica-Bold", fontSize=10,
        textColor=white, leading=14,
    )
    item_style = ParagraphStyle(
        "_crit_item", fontName="Courier", fontSize=9,
        textColor=white, leading=13,
    )

    rows = [[Paragraph("CRITICAL VALUES — IMMEDIATE REVIEW REQUIRED", header_style)]]
    for cv in critical_values:
        analyte = cv.get("analyte", "")
        result  = cv.get("result", "")
        unit    = cv.get("unit", "")
        note    = cv.get("note", "")
        rows.append([Paragraph(f"  {analyte}:  {result} {unit}   {note}", item_style)])

    t = Table(rows, colWidths=[CW])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), STATUS_CRITICAL),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("LINEBELOW",     (0, 0), (0, 0), 0.5, colors.HexColor("#7a3428")),
    ]))
    return [KeepTogether([t]), Spacer(1, 10)]


# ── Lab panel table ─────────────────────────────────────────────

def lab_panel(panel_name: str, rows: list) -> list:
    """Per-panel lab table: alternating warm-sand/white rows, status pills, Courier values."""
    ST = make_styles()

    header = [
        Paragraph("ANALYTE",      ST["label"]),
        Paragraph("RESULT",       ST["label"]),
        Paragraph("UNIT",         ST["label"]),
        Paragraph("REFERENCE",    ST["label"]),
        Paragraph("STATUS",       ST["label"]),
    ]
    col_w = [CW * f for f in (0.30, 0.15, 0.12, 0.27, 0.16)]

    table_rows = [header]
    style_cmds = [
        ("BACKGROUND",    (0, 0), (-1, 0), ACCENT_LIGHT),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.4, RULE_SOFT),
    ]

    for i, row in enumerate(rows):
        bg = CARD if i % 2 == 0 else PAPER_ALT
        r = i + 1
        style_cmds.append(("BACKGROUND", (0, r), (-1, r), bg))

        severity = row.get("severity", "normal")
        val_colour = severity_colour(severity)

        table_rows.append([
            Paragraph(row.get("analyte", ""), ST["body_sm"]),
            Paragraph(
                f"<font color='#{val_colour.hexval()[2:]}'><b>{row.get('result', '')}</b></font>",
                ST["mono"],
            ),
            Paragraph(row.get("unit", ""), ST["mono_sm"]),
            Paragraph(row.get("lab_ref_range", row.get("reference", "")), ST["mono_sm"]),
            status_pill(row.get("status", row.get("severity", "normal"))),
        ])

    t = Table(table_rows, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle(style_cmds))

    panel_label = Paragraph(panel_name.upper(), ST["label_upper"])
    return [Spacer(1, 6), panel_label, Spacer(1, 3), t, Spacer(1, 10)]


# ── CVD risk table ──────────────────────────────────────────────

def risk_table(cvd_risk: dict) -> list:
    """2-column risk factor card for CVD section."""
    ST = make_styles()
    if not cvd_risk:
        return []

    risk_pct  = cvd_risk.get("risk_percent_10yr", "—")
    category  = cvd_risk.get("risk_category", "—")
    method    = cvd_risk.get("method", "WHO SEAR-B")
    threshold = cvd_risk.get("treatment_threshold_met", False)
    reclassif = cvd_risk.get("reclassification_factors", [])
    override  = cvd_risk.get("clinical_override")
    missing   = cvd_risk.get("missing_variables", [])

    cat_colour = {
        "LOW": STATUS_NORMAL, "MODERATE": STATUS_LOW,
        "HIGH": STATUS_HIGH,  "VERY HIGH": STATUS_CRITICAL,
    }.get(str(category).upper(), INK_SUB)

    left_rows = [
        [Paragraph("10-YEAR CVD RISK", ST["label"]),
         Paragraph(
             f"<font color='#{cat_colour.hexval()[2:]}'><b>{risk_pct}%</b></font>",
             ST["section_title"],
         )],
        [Paragraph("RISK CATEGORY", ST["label"]),
         Paragraph(str(category), ST["body"])],
        [Paragraph("METHOD", ST["label"]),
         Paragraph(method, ST["body_sm"])],
        [Paragraph("STATIN THRESHOLD", ST["label"]),
         Paragraph("Met (≥10%)" if threshold else "Not met (<10%)", ST["body_sm"])],
    ]
    if override:
        left_rows.append([Paragraph("CLINICAL OVERRIDE", ST["label"]),
                          Paragraph(override, ST["body_sm"])])

    left_t = Table(left_rows, colWidths=[CW * 0.22, CW * 0.33])
    left_t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), CARD),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 7),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 7),
        ("LINEBELOW",     (0, 0), (-1, -2), 0.4, RULE_SOFT),
        ("BOX",           (0, 0), (-1, -1), 0.5, RULE),
    ]))

    rf_items = reclassif if reclassif else ["None identified"]
    rf_paras = [Paragraph(f"▸  {f}", ST["body_sm"]) for f in rf_items]
    if missing:
        rf_paras.append(Spacer(1, 4))
        rf_paras.append(Paragraph("Missing variables:", ST["label"]))
        for m in missing:
            rf_paras.append(Paragraph(f"  {m}", ST["body_sm"]))

    right_t = Table([[Paragraph("RECLASSIFICATION FACTORS", ST["label_upper"])],
                     *[[p] for p in rf_paras]],
                    colWidths=[CW * 0.40])
    right_t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), CARD),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 7),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 7),
        ("BOX",           (0, 0), (-1, -1), 0.5, RULE),
    ]))

    outer = Table([[left_t, Spacer(4, 1), right_t]], colWidths=[CW * 0.55, 4, CW * 0.40])
    outer.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))

    note = Paragraph(
        "South Asian 1.4× calibration applied (Tillin 2013 · INTERHEART). "
        "NICE NG238 2023 · ESC/EAS 2021.",
        ST["disclaimer"],
    )
    return [outer, Spacer(1, 4), note, Spacer(1, 10)]


# ── Patient summary block ───────────────────────────────────────

def patient_summary_block(summary_text: str) -> list:
    """Pale terracotta tint block with terracotta left border."""
    ST = make_styles()
    t = Table(
        [[Paragraph(summary_text, ST["body"])]],
        colWidths=[CW - 8],
    )
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), ACCENT_LIGHT),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBEFORE",    (0, 0), (0, -1), 3, ACCENT),
    ]))
    return [t, Spacer(1, 10)]


# ── Signature block ─────────────────────────────────────────────

def signature_block(report_date: str) -> list:
    """Italic terracotta signature + SLMC number + hairline + disclaimer."""
    ST = make_styles()
    DISCLAIMER = (
        "This report reflects findings on the date of visit; reference ranges follow local "
        "laboratory standards. Risk calculations use the WHO SEAR-B CVD model with South "
        "Asian calibration (NICE NG238 · ESC/EAS 2021). It is intended as an interpretive "
        "supplement to clinical care, not a replacement for ongoing medical judgment. "
        "Confidential to the named patient."
    )
    return [
        Spacer(1, 16),
        HRFlowable(width=CW * 0.4, thickness=0.5, color=RULE),
        Spacer(1, 4),
        Paragraph("D. R. Gamalathge", ST["sig_name"]),
        Paragraph("MBBS  ·  SLMC No. 36999", ST["sig_title"]),
        Spacer(1, 2),
        Paragraph(f"Report date: {report_date}", ST["sig_date"]),
        Spacer(1, 8),
        HRFlowable(width=CW, thickness=0.5, color=RULE, spaceAfter=6),
        Paragraph(DISCLAIMER, ST["disclaimer"]),
    ]


# ── Main builder ────────────────────────────────────────────────

def build_medical_report(
    output_path: str,
    patient_info: dict,
    results_by_panel: list,
    clinical_interpretation: dict,
    critical_values: list,
    further_investigations: list,
    management_suggestions: list,
    patient_summary: str,
    cvd_risk: dict,
    action_plan: dict,
    follow_up_plan: dict,
    doctor_notes: str = "",
) -> None:
    """Assemble the full 11-section Stately Editorial PDF."""
    import os
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    ST = make_styles()
    doc = BaseDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=ML, rightMargin=MR,
        topMargin=MT, bottomMargin=MB + 10,
    )
    frame = Frame(ML, MB + 10, CW, H - MT - MB - 10, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=on_page)])

    story: list = []

    # ── Cover ──────────────────────────────────────────────────
    story += wordmark_row("Laboratory Report")
    story += patient_banner(patient_info)

    # Executive summary stats
    total_labs = sum(len(p["rows"]) for p in results_by_panel)
    sev_counts = {"normal": 0, "flagged": 0, "critical": 0}
    for p in results_by_panel:
        for row in p["rows"]:
            s = row.get("severity", "normal")
            if s in ("critical",):
                sev_counts["critical"] += 1
            elif s in ("mild", "moderate", "high", "low", "severe"):
                sev_counts["flagged"] += 1
            else:
                sev_counts["normal"] += 1

    summary_text = patient_info.get("summary", (
        f"This report summarises laboratory findings for {patient_info.get('name', 'the patient')} "
        f"on {patient_info.get('report_date', '')}. "
        f"Results include {total_labs} analytes across {len(results_by_panel)} panel(s). "
        "Please review flagged values and the clinical interpretation sections below."
    ))
    story += exec_summary_block(summary_text, {
        "total": total_labs,
        "in_range": sev_counts["normal"],
        "flagged": sev_counts["flagged"],
        "critical": sev_counts["critical"],
    })

    # § Critical values (if any)
    if critical_values:
        story += critical_box(critical_values)

    # § 01 Key Findings
    key_findings = clinical_interpretation.get("key_findings", [])
    if key_findings:
        story += section_header(1, "Key Findings")
        for i, f in enumerate(key_findings, 1):
            text = f.get("finding", f) if isinstance(f, dict) else str(f)
            story.append(Paragraph(f"{i}.  {text}", ST["body_italic"]))
            story.append(Spacer(1, 3))

    # § 02 Lab Results (per panel)
    story += section_header(2, "Laboratory Results")
    for panel in results_by_panel:
        story += lab_panel(panel["panel"], panel["rows"])

    # § 03 CVD Risk Assessment
    if cvd_risk:
        story += section_header(
            3, "CVD Risk Assessment",
            "WHO CVD Risk Charts 2019 (SEAR-B)  ·  NICE NG238 2023  ·  ESC/EAS 2021",
        )
        story += risk_table(cvd_risk)

    # § 04 Clinical Interpretation
    findings = clinical_interpretation.get("findings", [])
    if findings:
        story += section_header(4, "Clinical Interpretation")
        for f in findings:
            heading = f.get("heading", "")
            detail  = f.get("detail", "")
            if heading:
                story.append(Paragraph(heading, ST["label_ink"]))
            if detail:
                story.append(Paragraph(detail, ST["body"]))
            story.append(Spacer(1, 5))

    # § 05 Abnormal Results Summary
    severity_rows = clinical_interpretation.get("severity_summary", [])
    if severity_rows:
        story += section_header(5, "Abnormal Results Summary")
        hdr = [
            Paragraph("ANALYTE",      ST["label"]),
            Paragraph("RESULT",       ST["label"]),
            Paragraph("SEVERITY",     ST["label"]),
            Paragraph("SIGNIFICANCE", ST["label"]),
        ]
        tbl_rows = [hdr]
        sev_style = []
        for i, sr in enumerate(severity_rows):
            row_bg = {
                "mild":     STATUS_LOW_BG,
                "moderate": STATUS_HIGH_BG,
                "severe":   STATUS_CRIT_BG,
                "critical": STATUS_CRIT_BG,
                "high":     STATUS_HIGH_BG,
                "low":      STATUS_LOW_BG,
            }.get(sr.get("severity", "normal"), PAPER_ALT)
            sev_style.append(("BACKGROUND", (0, i + 1), (-1, i + 1), row_bg))
            tbl_rows.append([
                Paragraph(sr.get("analyte", ""),     ST["body_sm"]),
                Paragraph(sr.get("result", ""),      ST["mono"]),
                Paragraph(sr.get("severity", "").capitalize(), ST["body_sm"]),
                Paragraph(sr.get("significance", ""), ST["body_sm"]),
            ])
        col_w2 = [CW * f for f in (0.25, 0.18, 0.15, 0.42)]
        sev_t = Table(tbl_rows, colWidths=col_w2, repeatRows=1)
        sev_t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), ACCENT_LIGHT),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("LINEBELOW",     (0, 0), (-1, -1), 0.4, RULE_SOFT),
            *sev_style,
        ]))
        story.append(sev_t)
        story.append(Spacer(1, 10))

    # § 06 Further Investigations
    if further_investigations:
        story += section_header(6, "Further Investigations")
        for item in further_investigations:
            text = item.get("investigation", item) if isinstance(item, dict) else str(item)
            story.append(Paragraph(f"▸  {text}", ST["body"]))
            story.append(Spacer(1, 2))

    # § 07 Management Suggestions
    if management_suggestions:
        story += section_header(
            7, "Management Suggestions",
            "Guided by WHO  ·  NICE  ·  ESC/EAS (cited)",
        )
        for item in management_suggestions:
            text = item.get("suggestion", item) if isinstance(item, dict) else str(item)
            story.append(Paragraph(f"▸  {text}", ST["body"]))
            story.append(Spacer(1, 2))

    # § 08 Action Plan
    if action_plan:
        story += section_header(8, "Action Plan")
        for section_key, section_title in [
            ("diet", "Diet"), ("exercise", "Exercise"),
            ("sleep", "Sleep"), ("alcohol", "Alcohol"),
        ]:
            content = action_plan.get(section_key, "")
            if content:
                story.append(Paragraph(section_title.upper(), ST["label_upper"]))
                story.append(Spacer(1, 2))
                story.append(Paragraph(str(content), ST["body"]))
                story.append(Spacer(1, 6))

    # § 09 Follow-Up Plan
    if follow_up_plan:
        story += section_header(9, "Follow-Up Plan")
        repeat_tests = follow_up_plan.get("repeat_tests", [])
        red_flags    = follow_up_plan.get("red_flags", [])
        if repeat_tests:
            story.append(Paragraph("REPEAT TESTS", ST["label_upper"]))
            story.append(Spacer(1, 2))
            for rt in repeat_tests:
                story.append(Paragraph(f"▸  {rt}", ST["body"]))
                story.append(Spacer(1, 2))
            story.append(Spacer(1, 4))
        if red_flags:
            story.append(Paragraph("RED FLAGS — SEEK URGENT CARE (1990)", ST["label_upper"]))
            story.append(Spacer(1, 2))
            for rf in red_flags:
                story.append(Paragraph(f"▸  {rf}", ST["body"]))
                story.append(Spacer(1, 2))

    # § 10 Patient Summary
    if patient_summary:
        story += section_header(10, "Patient Summary")
        story += patient_summary_block(patient_summary)

    # Doctor's notes (if provided)
    if doctor_notes:
        story += section_header(11, "Clinician's Notes")
        story.append(Paragraph(doctor_notes, ST["body"]))

    # Signature
    report_date = patient_info.get("report_date", "")
    story += signature_block(report_date)

    doc.build(story)
