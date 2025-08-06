# File: core/file_processor.py

import os
import base64
import pandas as pd
import tempfile
from pathlib import Path
import logging
from core.auto_parser import parse_pcap_auto

logger = logging.getLogger(__name__)

def process_uploaded_file(uploaded_file) -> tuple[pd.DataFrame, str]:
    try:
        if uploaded_file.size > 200 * 1024 * 1024:
            return pd.DataFrame(), "❌ File terlalu besar. Maksimal 200MB."

        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        df = parse_pcap_auto(tmp_path)

        try:
            os.unlink(tmp_path)
        except Exception as e:
            logger.warning(f"Could not delete temporary file: {e}")

        if df is not None and not df.empty:
            return df, f"✅ File berhasil diproses! Jumlah baris: {len(df):,}"
        return pd.DataFrame(), "❌ Gagal memproses file atau data kosong."

    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return pd.DataFrame(), f"❌ Error memproses file: {str(e)}"

def load_background_image(image_path: str) -> str | None:
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                img_bytes = img_file.read()
                return base64.b64encode(img_bytes).decode()
    except Exception as e:
        logger.warning(f"Could not load background image: {e}")
    return None
