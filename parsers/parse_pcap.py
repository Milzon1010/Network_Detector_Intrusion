import shutil
import subprocess
import pandas as pd
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

FIELDS = [
    "frame.time_epoch", "ip.src", "ip.dst", "frame.len", "ip.proto",
    "tcp.srcport", "tcp.dstport", "udp.srcport", "udp.dstport", "frame.protocols"
]

def parse_pcap_file(pcap_path: str) -> pd.DataFrame:
    try:
        logger.info(f"🔍 Parsing file: {pcap_path}")

        tshark_path = shutil.which("tshark")
        if tshark_path is None:
            raise FileNotFoundError("❌ TShark tidak ditemukan. Pastikan sudah terinstall dan ditambahkan ke PATH.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_csv:
            temp_csv_path = temp_csv.name

        tshark_cmd = [
            tshark_path,
            "-r", pcap_path,
            "-T", "fields",
            "-Eheader=y",
            "-Eseparator=,", 
            "-Equote=d"
        ]

        for field in FIELDS:
            tshark_cmd += ["-e", field]

        logger.debug(f"📤 Running tshark command: {' '.join(tshark_cmd)}")
        with open(temp_csv_path, "w") as f:
            subprocess.run(tshark_cmd, stdout=f, stderr=subprocess.PIPE, check=True)

        df = pd.read_csv(temp_csv_path)
        os.remove(temp_csv_path)

        df.rename(columns={
            "frame.time_epoch": "time", "ip.src": "src", "ip.dst": "dst", "frame.len": "length",
            "ip.proto": "protocol", "tcp.srcport": "tcp_srcport", "tcp.dstport": "tcp_dstport",
            "udp.srcport": "udp_srcport", "udp.dstport": "udp_dstport", "frame.protocols": "layers"
        }, inplace=True)

        df["time"] = pd.to_numeric(df["time"], errors="coerce")
        df["length"] = pd.to_numeric(df["length"], errors="coerce")

        logger.info(f"✅ Parsed successfully. Rows: {len(df)}")
        return df

    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Tshark error: {e.stderr.decode().strip()}")
    except Exception as e:
        logger.error(f"❌ Parsing error: {e}")

    return pd.DataFrame()
