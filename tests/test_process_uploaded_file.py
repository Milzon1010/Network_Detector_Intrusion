import pytest
import pandas as pd
from core.file_processor import process_uploaded_file

class DummyUpload:
    def __init__(self, content: bytes, name: str):
        self._content = content
        self.name = name
        self.size = len(content)

    def read(self):
        return self._content

def test_process_uploaded_file_valid_csv():
    csv_content = b"col1,col2\n1,2\n3,4"
    dummy = DummyUpload(csv_content, "test.csv")
    df, msg = process_uploaded_file(dummy)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "berhasil" in msg.lower()

def test_process_uploaded_file_large_file():
    large_content = b"a,b\n" + b"1,2\n" * (200 * 1024 * 1024 // 4)
    dummy = DummyUpload(large_content, "large.csv")
    df, msg = process_uploaded_file(dummy)
    assert df.empty
    assert "terlalu besar" in msg.lower()

def test_process_uploaded_file_invalid():
    dummy = DummyUpload(b"not,a,real,file", "invalid.xyz")
    df, msg = process_uploaded_file(dummy)
    assert df.empty
    assert "gagal" in msg.lower() or "error" in msg.lower()
