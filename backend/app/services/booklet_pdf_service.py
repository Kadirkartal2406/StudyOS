"""Sprint 23 — Daily booklet PDF (questions + blank optical sheet)."""

from __future__ import annotations

import io
from pathlib import Path

from app.models.assessment import AssessmentSession
# EAE Sprint 5+1 — Native vector PDF renderer for EAE visual assets
from app.services.booklet_pdf_eae_renderer import BookletPdfEaeRenderer

_FONT_CANDIDATES = (
    Path(__file__).resolve().parents[1] / "assets" / "fonts" / "arial.ttf",
    Path(__file__).resolve().parents[1] / "assets" / "fonts" / "DejaVuSans.ttf",
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("C:/Windows/Fonts/arial.ttf"),
)

import re

def _clean_math_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("$", "")
    text = text.replace(r"\cdot", "·")
    text = text.replace(r"\ge", "≥")
    text = text.replace(r"\le", "≤")
    text = text.replace(r"\neq", "≠")
    text = text.replace(r"\mathbb{Q}", "Q")
    text = text.replace(r"\in", "∈")
    # \frac{A}{B} -> A/B
    text = re.sub(r"\\frac\{([^}]+)\}\{([^}]+)\}", r"\1/\2", text)
    text = re.sub(r"\\left\(", "(", text)
    text = re.sub(r"\\right\)", ")", text)
    text = text.replace("\n", " ")
    return text


def _register_font() -> str:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    for path in _FONT_CANDIDATES:
        if path.is_file():
            name = "BookletFont"
            try:
                pdfmetrics.registerFont(TTFont(name, str(path)))
                return name
            except Exception:
                continue
    return "Helvetica"


def build_booklet_pdf(session: AssessmentSession) -> bytes:
    """Render booklet PDF without answer key; append blank optical page."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    font = _register_font()
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    margin = 18 * mm
    y = height - margin

    def new_page() -> None:
        nonlocal y
        c.showPage()
        c.setFont(font, 11)
        y = height - margin

    def ensure(space: float = 40) -> None:
        nonlocal y
        if y < margin + space:
            new_page()

    c.setFont(font, 16)
    title = session.subject_name or "Günün Denemesi"
    c.drawString(margin, y, title)
    y -= 18
    c.setFont(font, 10)
    c.drawString(
        margin,
        y,
        f"Sınav: {session.exam_type.upper()}  ·  Tarih: {session.challenge_date}  ·  "
        f"{session.requested_count} soru",
    )
    y -= 22

    section_names = {
        s.get("subject_code"): s.get("subject_name") or s.get("subject_code")
        for s in (session.section_plan or {}).get("sections", [])
        if isinstance(s, dict)
    }
    current_subject: str | None = None
    questions = sorted(session.questions or [], key=lambda q: q.ord_index)

    for q in questions:
        ensure(70)
        sc = q.subject_code
        if sc and sc != current_subject:
            current_subject = sc
            y -= 6
            c.setFont(font, 13)
            c.drawString(margin, y, str(section_names.get(sc, sc)))
            y -= 16
            c.setFont(font, 10)

        import textwrap
        
        stem = _clean_math_text(q.stem)
        # Format the stem as a paragraph with word wrapping
        stem_lines = textwrap.wrap(f"{q.ord_index + 1}. {stem}", width=105)
        for idx, line in enumerate(stem_lines):
            ensure(14)
            indent = margin + 12 if idx > 0 else margin
            c.drawString(indent, y, line)
            y -= 14

        choices = dict(q.choices or {})
        for key in ("A", "B", "C", "D", "E"):
            if key not in choices:
                continue
            choice_text = _clean_math_text(str(choices[key]))
            # Format choices with word wrapping
            choice_lines = textwrap.wrap(f"{key}) {choice_text}", width=100)
            for idx, line in enumerate(choice_lines):
                ensure(14)
                indent = margin + 18 if idx > 0 else margin + 6
                c.drawString(indent, y, line)
                y -= 13

        # EAE Sprint 5+1 — Render SVG visual asset as native ReportLab vector drawing
        q_meta = dict(q.metadata_ or {}) if hasattr(q, "metadata_") else {}
        eae_svg = q_meta.get("eae_svg_content")
        if eae_svg:
            try:
                from reportlab.graphics import renderPDF
                eae_renderer = BookletPdfEaeRenderer()
                highlight = []
                if q_meta.get("correct_node_id"):
                    highlight.append(str(q_meta["correct_node_id"]))
                if q_meta.get("highlight_node_ids"):
                    highlight.extend(str(x) for x in q_meta["highlight_node_ids"])
                drawing = eae_renderer.create_vector_drawing(
                    svg_content=eae_svg,
                    target_width=170.0,  # ~60% of A4 text width in points
                    target_height=100.0,
                    highlight_node_ids=highlight or None,
                )
                ensure(110)
                renderPDF.draw(drawing, c, margin, y - 105)
                y -= 112
            except Exception:
                pass  # Graceful degradation: skip vector draw, text already rendered

        y -= 8

    # Blank optical sheet
    new_page()
    c.setFont(font, 14)
    c.drawString(margin, y, "Optik Form (boş)")
    y -= 20
    c.setFont(font, 9)
    c.drawString(margin, y, "Her soru için bir şıkkı işaretleyin. Uygulamada Optik ile girin.")
    y -= 24

    col_w = (width - 2 * margin) / 4
    for i, q in enumerate(questions):
        ensure(18)
        col = i % 4
        if col == 0 and i > 0:
            y -= 16
        x = margin + col * col_w
        c.drawString(x, y, f"{q.ord_index + 1}.")
        bx = x + 18
        for key in ("A", "B", "C", "D", "E"):
            c.circle(bx, y + 3, 5, stroke=1, fill=0)
            c.drawString(bx - 2, y - 8, key)
            bx += 14

    c.save()
    return buf.getvalue()


def build_assessment_report_pdf(session: AssessmentSession) -> bytes:
    """Sprint 23 M23.9 — submitted session score report (summary + wrongs)."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    if session.status != "submitted":
        raise ValueError("Report PDF requires a submitted session")

    font = _register_font()
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    margin = 18 * mm
    y = height - margin

    def new_page() -> None:
        nonlocal y
        c.showPage()
        c.setFont(font, 11)
        y = height - margin

    def ensure(space: float = 40) -> None:
        nonlocal y
        if y < margin + space:
            new_page()

    def line(text: str, size: int = 11, gap: float = 14) -> None:
        nonlocal y
        ensure(gap + 4)
        c.setFont(font, size)
        c.drawString(margin, y, text[:110])
        y -= gap

    title = session.subject_name or "Assessment Raporu"
    line(title, size=16, gap=20)
    line(
        f"Sınav: {session.exam_type.upper()}  ·  "
        f"Tarih: {session.challenge_date or '-'}  ·  "
        f"{session.requested_count} soru",
        size=10,
        gap=16,
    )
    correct = int(session.correct_count or 0)
    wrong = int(session.wrong_count or 0)
    blank = int(session.blank_count or 0)
    acc = float(session.accuracy or 0) * 100
    line(f"Doğru: {correct}  Yanlış: {wrong}  Boş: {blank}  Başarı: %{acc:.0f}", size=12)
    if session.commentary:
        line(f"Yorum: {session.commentary[:200]}", size=10, gap=16)

    # Subject breakdown from section_plan names
    section_names = {
        s.get("subject_code"): s.get("subject_name") or s.get("subject_code")
        for s in (session.section_plan or {}).get("sections", [])
        if isinstance(s, dict)
    }
    by_subj: dict[str, list[int]] = {}
    questions = sorted(session.questions or [], key=lambda q: q.ord_index)
    for q in questions:
        sc = q.subject_code or "genel"
        bucket = by_subj.setdefault(sc, [0, 0, 0])  # c,w,b
        if q.is_correct is True:
            bucket[0] += 1
        elif q.is_correct is False:
            bucket[1] += 1
        else:
            bucket[2] += 1

    if by_subj:
        y -= 6
        line("Ders özeti", size=13, gap=16)
        for sc, (dc, dw, db) in by_subj.items():
            name = section_names.get(sc, sc)
            line(f"  {name}: {dc}D / {dw}Y / {db}B", size=10, gap=13)

    y -= 8
    line("Yanlış / boş sorular", size=13, gap=16)
    wrongs = [q for q in questions if q.is_correct is not True]
    if not wrongs:
        line("Tüm sorular doğru.", size=10)
    for q in wrongs:
        ensure(55)
        stem = (q.stem or "").replace("\n", " ")
        line(f"{q.ord_index + 1}. {stem[:130]}", size=10, gap=13)
        if len(stem) > 130:
            line(stem[130:260], size=9, gap=12)
        line(
            f"  Senin: {q.selected_key or '—'}  ·  Doğru: {q.correct_key}",
            size=9,
            gap=12,
        )
        expl = (q.wrong_explain or q.explanation or "").strip()
        if expl.startswith("{"):
            try:
                import json

                data = json.loads(expl)
                expl = str(data.get("explanation") or expl)
            except Exception:
                pass
        if expl:
            line(f"  {expl[:160]}", size=8, gap=11)
        y -= 4

    c.save()
    return buf.getvalue()
