"""
Unit tests for Booklet PDF EAE Native Vector Renderer.
"""

import pytest
from reportlab.graphics.shapes import Drawing

from app.services.booklet_pdf_eae_renderer import BookletPdfEaeRenderer


@pytest.fixture
def sample_svg():
    return """<svg viewBox="0 0 1000 500" xmlns="http://www.w3.org/2000/svg">
        <path id="turkey_admin_v1::province::konya" d="M 30 40 L 50 60 L 70 40 Z"/>
    </svg>"""


def test_booklet_pdf_eae_renderer(sample_svg):
    renderer = BookletPdfEaeRenderer()
    drawing = renderer.create_vector_drawing(sample_svg, target_width=300, target_height=150)

    assert isinstance(drawing, Drawing)
    assert drawing.width == 300
    assert drawing.height == 150
    assert len(drawing.contents) > 0


def test_booklet_pdf_highlight_node(sample_svg):
    renderer = BookletPdfEaeRenderer()
    drawing = renderer.create_vector_drawing(
        sample_svg,
        highlight_node_ids=["turkey_admin_v1::province::konya"],
    )
    assert isinstance(drawing, Drawing)
    assert len(drawing.contents) > 0


def test_booklet_pdf_highlight_node(sample_svg):
    renderer = BookletPdfEaeRenderer()
    drawing = renderer.create_vector_drawing(
        sample_svg,
        highlight_node_ids=["turkey_admin_v1::province::konya"],
    )
    assert isinstance(drawing, Drawing)
    assert len(drawing.contents) > 0
