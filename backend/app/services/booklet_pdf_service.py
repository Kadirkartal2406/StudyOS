"""Sprint 23 — Daily booklet PDF (cover + questions + blank optical sheet)."""

from __future__ import annotations

import io
import re
import textwrap
from datetime import date
from pathlib import Path
from typing import Any

from app.models.assessment import AssessmentSession
from app.services.booklet_pdf_eae_renderer import BookletPdfEaeRenderer
from app.services.booklet_pdf_theme import DEFAULT_EXAM_DURATION_MINUTES, THEME, BookletPdfTheme

_FONT_DIR = Path(__file__).resolve().parents[1] / "assets" / "fonts"
_FONT_REGULAR_CANDIDATES = (
    _FONT_DIR / "arial.ttf",
    _FONT_DIR / "DejaVuSans.ttf",
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("C:/Windows/Fonts/arial.ttf"),
    Path("C:/Windows/Fonts/segoeui.ttf"),
)
_FONT_BOLD_CANDIDATES = (
    _FONT_DIR / "arialbd.ttf",
    _FONT_DIR / "DejaVuSans-Bold.ttf",
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("C:/Windows/Fonts/arialbd.ttf"),
    Path("C:/Windows/Fonts/segoeuib.ttf"),
)


def _clean_math_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("$", "")
    replacements = (
        (r"\cdot", "·"),
        (r"\times", "×"),
        (r"\div", "÷"),
        (r"\pm", "±"),
        (r"\mp", "∓"),
        (r"\ge", "≥"),
        (r"\geq", "≥"),
        (r"\le", "≤"),
        (r"\leq", "≤"),
        (r"\neq", "≠"),
        (r"\approx", "≈"),
        (r"\infty", "∞"),
        (r"\pi", "π"),
        (r"\theta", "θ"),
        (r"\alpha", "α"),
        (r"\beta", "β"),
        (r"\gamma", "γ"),
        (r"\delta", "δ"),
        (r"\lambda", "λ"),
        (r"\mu", "μ"),
        (r"\sigma", "σ"),
        (r"\omega", "ω"),
        (r"\int", "∫"),
        (r"\sum", "∑"),
        (r"\prod", "∏"),
        (r"\partial", "∂"),
        (r"\mathbb{Q}", "ℚ"),
        (r"\mathbb{R}", "ℝ"),
        (r"\mathbb{N}", "ℕ"),
        (r"\mathbb{Z}", "ℤ"),
        (r"\in", "∈"),
        (r"\notin", "∉"),
        (r"\subset", "⊂"),
        (r"\subseteq", "⊆"),
        (r"\cup", "∪"),
        (r"\cap", "∩"),
        (r"\to", "→"),
        (r"\rightarrow", "→"),
        (r"\Rightarrow", "⇒"),
        (r"\ldots", "…"),
        (r"\dots", "…"),
        (r"\degree", "°"),
        (r"^\circ", "°"),
        (r"\,", " "),
        (r"\;", " "),
        (r"\:", " "),
        (r"\!", ""),
        (r"\\", ""),
    )
    for src, dst in replacements:
        text = text.replace(src, dst)
    text = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1)/(\2)", text)
    text = re.sub(r"\\sqrt\{([^{}]+)\}", r"√(\1)", text)
    text = re.sub(r"\\sqrt\[([^\]]+)\]\{([^{}]+)\}", r"\1√(\2)", text)
    text = re.sub(r"\\left\s*", "", text)
    text = re.sub(r"\\right\s*", "", text)
    text = re.sub(r"\\text\{([^{}]+)\}", r"\1", text)
    text = re.sub(r"\\mathrm\{([^{}]+)\}", r"\1", text)
    text = re.sub(r"\\mathbf\{([^{}]+)\}", r"\1", text)
    text = re.sub(r"\\overline\{([^{}]+)\}", r"\1̄", text)
    text = re.sub(r"\\hat\{([^{}]+)\}", r"\1̂", text)
    text = re.sub(r"\^\{([^{}]+)\}", r"^\1", text)
    text = re.sub(r"_\{([^{}]+)\}", r"_\1", text)
    text = re.sub(r"\\([a-zA-Z]+)", r"\1", text)
    text = text.replace("{", "").replace("}", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = text.replace("\n", " ").strip()
    return text


def _register_fonts() -> tuple[str, str]:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    regular = "Helvetica"
    bold = "Helvetica-Bold"
    for path in _FONT_REGULAR_CANDIDATES:
        if path.is_file():
            try:
                pdfmetrics.registerFont(TTFont("BookletFont", str(path)))
                regular = "BookletFont"
                break
            except Exception:
                continue
    for path in _FONT_BOLD_CANDIDATES:
        if path.is_file():
            try:
                pdfmetrics.registerFont(TTFont("BookletFont-Bold", str(path)))
                bold = "BookletFont-Bold"
                break
            except Exception:
                continue
    if bold == "Helvetica-Bold" and regular == "BookletFont":
        bold = regular
    return regular, bold


def _hex(color: str):
    from reportlab.lib.colors import HexColor

    return HexColor(f"#{color.lstrip('#')}")


def _choice_keys(choices: dict[str, Any]) -> list[str]:
    """Render only keys that exist — LGS 4-choice never draws E."""
    order = ("A", "B", "C", "D", "E")
    present = {str(k).upper() for k in (choices or {})}
    return [k for k in order if k in present]


def _format_tr_date(value: date | str | None) -> str:
    months = (
        "Ocak",
        "Şubat",
        "Mart",
        "Nisan",
        "Mayıs",
        "Haziran",
        "Temmuz",
        "Ağustos",
        "Eylül",
        "Ekim",
        "Kasım",
        "Aralık",
    )
    if value is None:
        return "—"
    if isinstance(value, str):
        try:
            value = date.fromisoformat(value[:10])
        except ValueError:
            return value
    return f"{value.day} {months[value.month - 1]} {value.year}"


def _tr_upper(text: str) -> str:
    """Turkish-aware uppercase for exam booklet headers."""
    table = str.maketrans({"i": "İ", "ı": "I", "ş": "Ş", "ğ": "Ğ", "ü": "Ü", "ö": "Ö", "ç": "Ç"})
    return (text or "").translate(table).upper()


def _exam_label(exam_type: str | None) -> str:
    raw = (exam_type or "").strip()
    if not raw:
        return "DENEME"
    return _tr_upper(raw.replace("_", " "))


def _duration_minutes(session: Any, theme: BookletPdfTheme = THEME) -> int:
    plan = dict(getattr(session, "section_plan", None) or {})
    for key in ("duration_minutes", "time_limit_minutes", "duration"):
        if plan.get(key):
            try:
                return max(1, int(plan[key]))
            except (TypeError, ValueError):
                pass
    exam = str(getattr(session, "exam_type", "") or "").strip().lower()
    if exam in DEFAULT_EXAM_DURATION_MINUTES:
        return DEFAULT_EXAM_DURATION_MINUTES[exam]
    count = int(getattr(session, "requested_count", 0) or 0)
    return max(30, count)


def _section_rows(session: Any, questions: list[Any]) -> list[dict[str, Any]]:
    plan = dict(getattr(session, "section_plan", None) or {})
    sections = [s for s in (plan.get("sections") or []) if isinstance(s, dict)]
    counts: dict[str, int] = {}
    for q in questions:
        sc = str(getattr(q, "subject_code", None) or "genel")
        counts[sc] = counts.get(sc, 0) + 1

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for sec in sections:
        code = str(sec.get("subject_code") or "")
        if not code:
            continue
        seen.add(code)
        topics = sec.get("topics") or []
        topic_names = [
            str(t.get("topic_name") or t.get("topic_code") or "").strip()
            for t in topics
            if isinstance(t, dict)
        ]
        topic_names = [t for t in topic_names if t]
        planned = sum(int(t.get("count") or 0) for t in topics if isinstance(t, dict))
        n = counts.get(code, planned)
        rows.append(
            {
                "code": code,
                "name": str(sec.get("subject_name") or code),
                "topics": ", ".join(topic_names[:4]) if topic_names else "—",
                "count": n,
            }
        )
    for code, n in counts.items():
        if code in seen:
            continue
        rows.append({"code": code, "name": code, "topics": "—", "count": n})
    return rows


def _wrap(text: str, width: int) -> list[str]:
    text = (text or "").strip()
    if not text:
        return [""]
    return textwrap.wrap(text, width=width, break_long_words=True, replace_whitespace=True) or [text]


def _question_meta(q: Any) -> dict[str, Any]:
    meta: dict[str, Any] = {}
    if hasattr(q, "metadata_") and isinstance(q.metadata_, dict):
        meta.update(q.metadata_)
    qie = getattr(q, "qie_card", None)
    if isinstance(qie, dict):
        meta.update(qie)
    return meta


class _BookletPainter:
    def __init__(
        self,
        canvas_obj: Any,
        font: str,
        font_bold: str,
        theme: BookletPdfTheme = THEME,
    ) -> None:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm

        self.c = canvas_obj
        self.font = font
        self.font_bold = font_bold
        self.theme = theme
        self.width, self.height = A4
        self.margin_x = theme.margin_x_mm * mm
        self.margin_top = theme.margin_top_mm * mm
        self.margin_bottom = theme.margin_bottom_mm * mm
        self.footer_reserve = theme.footer_reserve_mm * mm
        self.content_bottom = self.margin_bottom + self.footer_reserve
        self.y = self.height - self.margin_top
        self.page_index = 1
        self.show_footer = False
        self.content_width = self.width - 2 * self.margin_x
        # ÖSYM-style two-column question flow
        self.two_col = False
        self.gutter = theme.col_gutter_mm * mm
        self.col_width = (self.content_width - self.gutter) / 2
        self.col_xs = [self.margin_x, self.margin_x + self.col_width + self.gutter]
        self.column = 0
        self.col_top_y = self.y

    @property
    def col_x(self) -> float:
        return self.col_xs[self.column] if self.two_col else self.margin_x

    @property
    def active_width(self) -> float:
        return self.col_width if self.two_col else self.content_width

    def hex(self, key: str):
        return _hex(getattr(self.theme, key))

    def set_fill(self, key: str) -> None:
        self.c.setFillColor(self.hex(key))

    def set_stroke(self, key: str) -> None:
        self.c.setStrokeColor(self.hex(key))

    def draw_footer(self) -> None:
        if not self.show_footer:
            return
        c = self.c
        y_line = self.margin_bottom + self.footer_reserve - 4
        self.set_stroke("rule")
        c.setLineWidth(0.6)
        c.line(self.margin_x, y_line, self.width - self.margin_x, y_line)
        c.setFont(self.font, self.theme.footer_pt)
        self.set_fill("footer")
        c.drawCentredString(self.width / 2, self.margin_bottom + 4, str(self.page_index))
        c.drawString(self.margin_x, self.margin_bottom + 4, self.theme.brand_name)
        c.drawRightString(
            self.width - self.margin_x,
            self.margin_bottom + 4,
            self.theme.brand_url,
        )

    def _draw_column_rule(self) -> None:
        if not self.two_col:
            return
        mid = self.margin_x + self.col_width + self.gutter / 2
        self.set_stroke("rule_strong")
        self.c.setLineWidth(0.45)
        self.c.line(mid, self.content_bottom + 2, mid, self.height - self.margin_top)

    def begin_question_pages(self) -> None:
        """Enter ÖSYM two-column mode on a fresh question page."""
        self.two_col = True
        self.new_page(numbered=True)
        self.column = 0
        self.col_top_y = self.y
        self._draw_column_rule()

    def new_page(self, *, numbered: bool = True) -> None:
        self.draw_footer()
        self.c.showPage()
        self.page_index += 1
        self.show_footer = numbered
        self.y = self.height - self.margin_top
        self.column = 0
        self.col_top_y = self.y
        if self.two_col and numbered:
            self._draw_column_rule()

    def ensure(self, space: float) -> None:
        """Single-column ensure (instructions / TOC / optical)."""
        if self.y < self.content_bottom + space:
            was = self.two_col
            self.two_col = False
            self.new_page(numbered=True)
            self.two_col = was

    def _advance_column_or_page(self) -> None:
        if self.column == 0:
            self.column = 1
            self.y = self.col_top_y
        else:
            self.new_page(numbered=True)

    def ensure_col(self, space: float) -> None:
        """Keep question blocks inside the active ÖSYM column."""
        if not self.two_col:
            self.ensure(space)
            return
        if self.y < self.content_bottom + space:
            self._advance_column_or_page()

    def draw_cover(self, session: Any, question_count: int) -> None:
        c = self.c
        t = self.theme
        self.show_footer = False

        # Soft geometric accents (print-safe, low ink)
        c.saveState()
        c.setFillColor(self.hex("accent_muted"))
        c.setFillAlpha(0.28)
        path = c.beginPath()
        path.moveTo(self.width * 0.58, self.height)
        path.lineTo(self.width, self.height)
        path.lineTo(self.width, self.height * 0.62)
        path.close()
        c.drawPath(path, fill=1, stroke=0)
        path2 = c.beginPath()
        path2.moveTo(0, 0)
        path2.lineTo(self.width * 0.42, 0)
        path2.lineTo(0, self.height * 0.34)
        path2.close()
        c.drawPath(path2, fill=1, stroke=0)
        c.restoreState()

        # Brand mark
        cx = self.width / 2
        y = self.height - 42
        self.set_fill("accent")
        c.circle(cx, y, 11, stroke=0, fill=1)
        self.set_fill("white")
        c.setFont(self.font_bold, 9)
        c.drawCentredString(cx, y - 3, "S")
        y -= 28
        c.setFont(self.font_bold, t.cover_brand_pt)
        self.set_fill("text")
        c.drawCentredString(cx, y, t.brand_name)
        y -= 14
        c.setFont(self.font, 9)
        self.set_fill("text_secondary")
        c.drawCentredString(cx, y, t.brand_tagline)

        y = self.height * 0.58
        c.setFont(self.font_bold, t.cover_title_pt)
        self.set_fill("text")
        c.drawCentredString(cx, y, t.booklet_title)
        y -= 28
        c.setFont(self.font_bold, t.cover_exam_pt)
        self.set_fill("accent")
        c.drawCentredString(cx, y, _exam_label(getattr(session, "exam_type", None)))

        # Meta chips
        y -= 48
        from reportlab.lib.units import mm

        chip_w = 52 * mm
        gap = 8 * mm
        total_w = 3 * chip_w + 2 * gap
        x0 = (self.width - total_w) / 2
        meta = [
            ("TARİH", _format_tr_date(getattr(session, "challenge_date", None))),
            ("SÜRE", f"{_duration_minutes(session)} Dakika"),
            ("SORU SAYISI", f"{question_count} Soru"),
        ]
        for i, (label, value) in enumerate(meta):
            x = x0 + i * (chip_w + gap)
            self.set_fill("chip_bg")
            self.set_stroke("accent_soft")
            c.setLineWidth(1)
            c.roundRect(x, y - 28, chip_w, 46, 6, stroke=1, fill=1)
            c.setFont(self.font, t.cover_meta_label_pt)
            self.set_fill("accent")
            c.drawCentredString(x + chip_w / 2, y + 6, label)
            c.setFont(self.font_bold, t.cover_meta_value_pt)
            self.set_fill("text")
            c.drawCentredString(x + chip_w / 2, y - 12, value[:28])

        # Subject strip if available
        rows = _section_rows(session, list(getattr(session, "questions", None) or []))
        if rows:
            y -= 70
            c.setFont(self.font, 9)
            self.set_fill("text_secondary")
            names = "  ·  ".join(r["name"] for r in rows[:6])
            for line in _wrap(names, 90):
                c.drawCentredString(cx, y, line)
                y -= 12

        # Footer brand rule
        self.set_stroke("accent")
        c.setLineWidth(1.2)
        c.line(self.margin_x, 36, self.width - self.margin_x, 36)
        c.setFont(self.font, 9)
        self.set_fill("text_secondary")
        c.drawCentredString(cx, 22, t.brand_url)

    def draw_instructions(self, session: Any, question_count: int) -> None:
        self.new_page(numbered=True)
        t = self.theme
        c = self.c
        c.setFont(self.font_bold, 16)
        self.set_fill("accent")
        c.drawString(self.margin_x, self.y, "AÇIKLAMALAR")
        self.y -= 8
        self.set_stroke("accent")
        c.setLineWidth(1.2)
        c.line(self.margin_x, self.y, self.width - self.margin_x, self.y)
        self.y -= 22

        exam = _exam_label(getattr(session, "exam_type", None))
        duration = _duration_minutes(session)
        bullets = [
            f"Bu kitapçık StudyOS {exam} günlük denemesidir.",
            f"Kitapçıkta toplam {question_count} soru bulunmaktadır.",
            f"Önerilen süre yaklaşık {duration} dakikadır.",
            "Her sorunun yalnızca bir doğru cevabı vardır.",
            "Cevaplarınızı optik forma veya uygulamadaki Optik girişine işaretleyiniz.",
            "Soru metni ve şıkları dikkatle okuyunuz; şekilli sorularda görselleri inceleyiniz.",
            "Bu bir hazırlık materyalidir; resmi sınav belgesi değildir.",
        ]
        c.setFont(self.font, t.body_pt)
        self.set_fill("text")
        for i, item in enumerate(bullets, start=1):
            for j, line in enumerate(_wrap(f"{i}. {item}", 95)):
                self.ensure(16)
                indent = self.margin_x if j == 0 else self.margin_x + 14
                c.drawString(indent, self.y, line)
                self.y -= 15
            self.y -= 4

        self.y -= 10
        self.ensure(70)
        box_h = 58
        self.set_stroke("warning_border")
        self.set_fill("chip_bg")
        c.setLineWidth(1.4)
        c.roundRect(self.margin_x, self.y - box_h + 12, self.content_width, box_h, 5, stroke=1, fill=1)
        c.setFont(self.font_bold, 10)
        self.set_fill("accent")
        c.drawString(self.margin_x + 12, self.y, "UYARILAR")
        self.y -= 16
        c.setFont(self.font, 9)
        self.set_fill("text")
        warnings = [
            "Kitapçık içeriği yapay zekâ destekli üretim ve doğrulama süreçlerinden geçer.",
            "Resmî ÖSYM materyali değildir; telifli içerik kopyalanmamıştır.",
            "Sonucu uygulamada kaydederek gelişiminizi takip edebilirsiniz.",
        ]
        for wline in warnings:
            for line in _wrap(f"• {wline}", 92):
                c.drawString(self.margin_x + 12, self.y, line)
                self.y -= 12

    def draw_toc(self, session: Any, questions: list[Any]) -> None:
        rows = _section_rows(session, questions)
        if not rows:
            return
        self.new_page(numbered=True)
        c = self.c
        t = self.theme
        c.setFont(self.font_bold, 16)
        self.set_fill("accent")
        c.drawString(self.margin_x, self.y, "İÇİNDEKİLER")
        self.y -= 8
        self.set_stroke("accent")
        c.setLineWidth(1.2)
        c.line(self.margin_x, self.y, self.width - self.margin_x, self.y)
        self.y -= 24

        # Header row
        col_test = self.margin_x
        col_topic = self.margin_x + 130
        c.setFont(self.font_bold, 9)
        self.set_fill("text_secondary")
        c.drawString(col_test, self.y, "TEST")
        c.drawString(col_topic, self.y, "KONU")
        c.drawRightString(self.width - self.margin_x, self.y, "SORU")
        self.y -= 6
        self.set_stroke("rule")
        c.setLineWidth(0.6)
        c.line(self.margin_x, self.y, self.width - self.margin_x, self.y)
        self.y -= 16

        total = 0
        for i, row in enumerate(rows):
            self.ensure(28)
            if i % 2 == 0:
                self.set_fill("chip_bg")
                c.setFillColor(self.hex("chip_bg"))
                c.rect(self.margin_x - 2, self.y - 4, self.content_width + 4, 20, stroke=0, fill=1)
            c.setFont(self.font_bold, 10)
            self.set_fill("text")
            c.drawString(col_test, self.y, str(row["name"])[:28])
            c.setFont(self.font, 9)
            self.set_fill("text_secondary")
            c.drawString(col_topic, self.y, str(row["topics"])[:48])
            c.setFont(self.font_bold, 10)
            self.set_fill("text")
            c.drawRightString(self.width - self.margin_x, self.y, str(row["count"]))
            total += int(row["count"])
            self.y -= 22

        self.y -= 6
        self.ensure(28)
        self.set_fill("accent")
        c.roundRect(self.margin_x, self.y - 6, self.content_width, 24, 4, stroke=0, fill=1)
        c.setFont(self.font_bold, 11)
        self.set_fill("white")
        c.drawString(self.margin_x + 10, self.y, "TOPLAM")
        c.drawRightString(self.width - self.margin_x - 10, self.y, str(total))
        self.y -= 30

    def draw_section_header(self, exam: str, section_name: str, count: int) -> None:
        """Full-width test banner; always restarts left column (ÖSYM style)."""
        t = self.theme
        # Prefer a clean left-column start for each test
        near_top = self.y >= self.col_top_y - 2
        if self.two_col and (self.column != 0 or not near_top):
            usable = self.y - self.content_bottom
            if self.column != 0 or usable < 90:
                self.new_page(numbered=True)

        self.column = 0
        c = self.c
        title = f"{exam} / {_tr_upper(section_name)} TESTİ"
        c.setFont(self.font_bold, t.section_title_pt)
        self.set_fill("accent")
        c.drawString(self.margin_x, self.y, title[:72])
        c.setFont(self.font, t.section_sub_pt)
        self.set_fill("text_secondary")
        c.drawRightString(
            self.width - self.margin_x,
            self.y,
            f"Bu testte {count} soru vardır.",
        )
        self.y -= 7
        self.set_stroke("accent")
        c.setLineWidth(1.0)
        c.line(self.margin_x, self.y, self.width - self.margin_x, self.y)
        self.y -= t.after_section_gap
        self.col_top_y = self.y
        if self.two_col:
            self._draw_column_rule()

    def _estimate_block_height(
        self,
        stem_lines: list[str],
        choice_line_groups: list[list[str]],
        has_eae: bool,
        *,
        inline_choices: bool = False,
    ) -> float:
        t = self.theme
        h = len(stem_lines) * t.stem_leading + 4
        if inline_choices:
            h += t.choice_leading + t.choice_gap
        else:
            for group in choice_line_groups:
                h += len(group) * t.choice_leading + t.choice_gap
        if has_eae:
            h += 78
        h += t.after_question_gap
        return h

    def _choices_fit_inline(self, choices: dict[str, Any], keys: list[str]) -> bool:
        """ÖSYM short-option row: A) …  B) … when all options are compact."""
        if not keys:
            return False
        parts = []
        for key in keys:
            raw = _clean_math_text(str(choices.get(key, "")))
            if len(raw) > 12:
                return False
            parts.append(f"{key}) {raw}")
        # Rough fit into one column line
        return len("   ".join(parts)) <= self.theme.col_wrap_choice + 8

    def draw_question(self, q: Any, display_no: int) -> None:
        from reportlab.graphics import renderPDF

        t = self.theme
        wrap_stem = t.col_wrap_stem if self.two_col else 92
        wrap_choice = t.col_wrap_choice if self.two_col else 88
        stem = _clean_math_text(getattr(q, "stem", "") or "")
        stem_lines = _wrap(f"{display_no}.  {stem}", wrap_stem)
        choices = dict(getattr(q, "choices", None) or {})
        keys = _choice_keys(choices)
        inline = self._choices_fit_inline(choices, keys)
        choice_groups: list[list[str]] = []
        if not inline:
            for key in keys:
                raw = _clean_math_text(str(choices.get(key, "")))
                choice_groups.append(_wrap(f"{key})  {raw}", wrap_choice))

        meta = _question_meta(q)
        eae_svg = meta.get("eae_svg_content")
        has_eae = bool(eae_svg)
        eae_h = 78.0 if has_eae else 0.0
        needed = self._estimate_block_height(
            stem_lines, choice_groups, has_eae, inline_choices=inline
        )
        max_col = self.height - self.margin_top - self.content_bottom - 4
        self.ensure_col(min(needed, max_col))

        c = self.c
        x0 = self.col_x

        # Question number bold + stem (ÖSYM: number stands out)
        first = stem_lines[0] if stem_lines else f"{display_no}."
        num = f"{display_no}."
        rest = first[len(num) :].lstrip() if first.startswith(num) else first
        c.setFont(self.font_bold, t.question_pt)
        self.set_fill("text")
        c.drawString(x0, self.y, num)
        num_w = c.stringWidth(num + " ", self.font_bold, t.question_pt)
        c.setFont(self.font, t.question_pt)
        c.drawString(x0 + num_w, self.y, rest)
        self.y -= t.stem_leading
        for line in stem_lines[1:]:
            self.ensure_col(t.stem_leading)
            x0 = self.col_x
            c.setFont(self.font, t.question_pt)
            self.set_fill("text")
            c.drawString(x0 + 12, self.y, line)
            self.y -= t.stem_leading

        self.y -= 2

        if inline:
            self.ensure_col(t.choice_leading + t.choice_gap)
            x0 = self.col_x
            parts = [
                f"{key}) {_clean_math_text(str(choices.get(key, '')))}" for key in keys
            ]
            c.setFont(self.font, t.choice_pt)
            self.set_fill("text")
            c.drawString(x0 + 10, self.y, "   ".join(parts))
            self.y -= t.choice_leading + t.choice_gap
        else:
            for group in choice_groups:
                group_h = len(group) * t.choice_leading + t.choice_gap
                self.ensure_col(group_h)
                x0 = self.col_x
                for idx, line in enumerate(group):
                    if idx == 0 and line[:2] in {f"{k})" for k in keys}:
                        # Bold choice letter
                        label, _, body = line.partition(")")
                        c.setFont(self.font_bold, t.choice_pt)
                        self.set_fill("text")
                        c.drawString(x0 + 8, self.y, f"{label})")
                        lw = c.stringWidth(f"{label}) ", self.font_bold, t.choice_pt)
                        c.setFont(self.font, t.choice_pt)
                        c.drawString(x0 + 8 + lw, self.y, body.lstrip())
                    else:
                        c.setFont(self.font, t.choice_pt)
                        self.set_fill("text")
                        indent = x0 + 8 if idx == 0 else x0 + 22
                        c.drawString(indent, self.y, line)
                    self.y -= t.choice_leading
                self.y -= t.choice_gap

        if eae_svg:
            try:
                eae_renderer = BookletPdfEaeRenderer()
                highlight: list[str] = []
                if meta.get("correct_node_id"):
                    highlight.append(str(meta["correct_node_id"]))
                if meta.get("highlight_node_ids"):
                    highlight.extend(str(x) for x in meta["highlight_node_ids"])
                drawing = eae_renderer.create_vector_drawing(
                    svg_content=eae_svg,
                    target_width=min(150.0, self.active_width - 4),
                    target_height=70.0,
                    highlight_node_ids=highlight or None,
                )
                self.ensure_col(eae_h)
                x0 = self.col_x
                renderPDF.draw(drawing, c, x0, self.y - 68)
                self.y -= eae_h
            except Exception:
                pass

        self.y -= t.after_question_gap

    def draw_optical_form(self, questions: list[Any]) -> None:
        self.two_col = False
        self.new_page(numbered=True)
        c = self.c
        t = self.theme
        c.setFont(self.font_bold, 14)
        self.set_fill("accent")
        c.drawString(self.margin_x, self.y, "OPTİK FORM (BOŞ)")
        self.y -= 8
        self.set_stroke("accent")
        c.setLineWidth(1.1)
        c.line(self.margin_x, self.y, self.width - self.margin_x, self.y)
        self.y -= 18
        c.setFont(self.font, 9)
        self.set_fill("text_secondary")
        c.drawString(
            self.margin_x,
            self.y,
            "Her soru için bir şıkkı işaretleyin. Uygulamada Optik ile girin.",
        )
        self.y -= 22

        col_w = self.content_width / 4
        for i, q in enumerate(questions):
            self.ensure(22)
            col = i % 4
            if col == 0 and i > 0:
                self.y -= 18
            x = self.margin_x + col * col_w
            c.setFont(self.font_bold, 9)
            self.set_fill("text")
            c.drawString(x, self.y, f"{getattr(q, 'ord_index', i) + 1}.")
            bx = x + 16
            keys = _choice_keys(dict(getattr(q, "choices", None) or {})) or list("ABCDE")
            for key in keys:
                c.setStrokeColor(self.hex("text"))
                c.circle(bx, self.y + 3, 4.5, stroke=1, fill=0)
                c.setFont(self.font, 7)
                self.set_fill("text_secondary")
                c.drawCentredString(bx, self.y - 9, key)
                bx += 13


def build_booklet_pdf(session: AssessmentSession) -> bytes:
    """Render booklet PDF without answer key; append blank optical page."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    font, font_bold = _register_fonts()
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    painter = _BookletPainter(c, font, font_bold, THEME)

    questions = sorted(session.questions or [], key=lambda q: q.ord_index)
    q_count = len(questions) or int(getattr(session, "requested_count", 0) or 0)

    painter.draw_cover(session, q_count)
    painter.draw_instructions(session, q_count)
    painter.draw_toc(session, questions)

    section_names = {
        s.get("subject_code"): s.get("subject_name") or s.get("subject_code")
        for s in (session.section_plan or {}).get("sections", [])
        if isinstance(s, dict)
    }
    section_counts: dict[str, int] = {}
    for q in questions:
        sc = str(getattr(q, "subject_code", None) or "")
        section_counts[sc] = section_counts.get(sc, 0) + 1

    exam = _exam_label(getattr(session, "exam_type", None))
    current_subject: str | None = None

    if questions:
        painter.begin_question_pages()

    for q in questions:
        sc = str(getattr(q, "subject_code", None) or "")
        if sc and sc != current_subject:
            current_subject = sc
            name = str(section_names.get(sc, sc) or sc)
            painter.draw_section_header(exam, name, section_counts.get(sc, 0))
        painter.draw_question(q, int(getattr(q, "ord_index", 0)) + 1)

    painter.draw_optical_form(questions)
    painter.draw_footer()
    c.save()
    return buf.getvalue()


def build_assessment_report_pdf(session: AssessmentSession) -> bytes:
    """Sprint 23 M23.9 — submitted session score report (summary + wrongs)."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    if session.status != "submitted":
        raise ValueError("Report PDF requires a submitted session")

    font, font_bold = _register_fonts()
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    margin = THEME.margin_x_mm * mm
    y = height - THEME.margin_top_mm * mm
    bottom = THEME.margin_bottom_mm * mm + THEME.footer_reserve_mm * mm

    def new_page() -> None:
        nonlocal y
        c.showPage()
        c.setFont(font, 11)
        y = height - THEME.margin_top_mm * mm

    def ensure(space: float = 40) -> None:
        nonlocal y
        if y < bottom + space:
            new_page()

    def line(text: str, size: int = 11, gap: float = 14, bold: bool = False) -> None:
        nonlocal y
        ensure(gap + 4)
        c.setFont(font_bold if bold else font, size)
        c.setFillColor(_hex(THEME.text))
        c.drawString(margin, y, text[:110])
        y -= gap

    title = session.subject_name or "Assessment Raporu"
    line(title, size=16, gap=20, bold=True)
    line(
        f"Sınav: {_exam_label(session.exam_type)}  ·  "
        f"Tarih: {_format_tr_date(session.challenge_date)}  ·  "
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

    section_names = {
        s.get("subject_code"): s.get("subject_name") or s.get("subject_code")
        for s in (session.section_plan or {}).get("sections", [])
        if isinstance(s, dict)
    }
    by_subj: dict[str, list[int]] = {}
    questions = sorted(session.questions or [], key=lambda q: q.ord_index)
    for q in questions:
        sc = q.subject_code or "genel"
        bucket = by_subj.setdefault(sc, [0, 0, 0])
        if q.is_correct is True:
            bucket[0] += 1
        elif q.is_correct is False:
            bucket[1] += 1
        else:
            bucket[2] += 1

    if by_subj:
        y -= 6
        line("Ders özeti", size=13, gap=16, bold=True)
        for sc, (dc, dw, db) in by_subj.items():
            name = section_names.get(sc, sc)
            line(f"  {name}: {dc}D / {dw}Y / {db}B", size=10, gap=13)

    y -= 8
    line("Yanlış / boş sorular", size=13, gap=16, bold=True)
    wrongs = [q for q in questions if q.is_correct is not True]
    if not wrongs:
        line("Tüm sorular doğru.", size=10)
    for q in wrongs:
        ensure(55)
        stem = _clean_math_text(q.stem or "")
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
