import pytest
from app.services.photo_question_service import PhotoSolveRequest, PhotoSolveResponse

def test_photo_solve_request_schema():
    req = PhotoSolveRequest(image_base64="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")
    assert req.image_base64.startswith("data:image")
    assert req.subject_code is None
