# core/auto_parser.py

import os
import logging
import pandas as pd
from pathlib import Path

from core.preprocessor import preprocess_packets
from parsers.parse_pcap_tshark_ipv6 import parse_pcap_file  # ✅ Aktifkan parser

logger = logging.getLogger(__name__)

def parse_pcap_auto(filepath: str) -> pd.DataFrame:
    try:
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"File tidak ditemukan: {filepath}")

        ext = Path(filepath).suffix.lower()

        # === Handle PCAP/PCAPNG ===
        if ext in [".pcap", ".pcapng"]:
            logger.info(f"🔍 Memproses file PCAP: {filepath}")
            try:
                df = parse_pcap_file(filepath)
            except Exception as parse_err:
                logger.warning(f"⚠️ Parsing PCAP gagal (pyshark/tshark mungkin tidak tersedia): {parse_err}")
                return pd.DataFrame()

        # === Handle CSV ===
        elif ext == ".csv":
            logger.info(f"📄 Membaca file CSV: {filepath}")
            df = pd.read_csv(filepath)

        else:
            raise ValueError(f"❌ Format file tidak didukung: {ext}")

        # === Preprocessing jika data valid ===
        if df is not None and not df.empty:
            df = preprocess_packets(df)
            logger.info(f"✅ Data selesai diproses & dipreproses. Baris: {len(df)}")
            return df

        return pd.DataFrame()

    except Exception as e:
        logger.error(f"❌ Parsing gagal: {e}")
        return pd.DataFrame()
