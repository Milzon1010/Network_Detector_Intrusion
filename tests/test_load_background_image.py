# File: tests/test_load_background_image.py

import os
import base64
import pytest
from core.file_processor import load_background_image

def test_load_background_image_success(tmp_path):
    img_path = tmp_path / "dummy.jpg"
    img_path.write_bytes(b"\xFF\xD8\xFF\xE0" + b"\x00" * 100)  # minimal JPEG header

    result = load_background_image(str(img_path))

    assert isinstance(result, str)
    assert base64.b64decode(result).startswith(b"\xFF\xD8")

def test_load_background_image_file_not_found():
    result = load_background_image("nonexistent.jpg")
    assert result is None
