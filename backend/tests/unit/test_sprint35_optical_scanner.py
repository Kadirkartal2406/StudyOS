import pytest
from app.services.optical_scanner_service import OpticalScanRequest, OpticalScanResponse

def test_optical_scan_request_schema():
    req = OpticalScanRequest(image_base64="data:image/png;base64,...", exam_type="kpss", question_count=20)
    assert req.exam_type == "kpss"
    assert req.question_count == 20
