# tools/pcap_to_csv.py

import subprocess
import argparse
import shutil
import os

FIELDS = [
    "frame.time_epoch",
    "ip.src",
    "ip.dst",
    "frame.len",
    "ip.proto",
    "tcp.srcport",
    "tcp.dstport",
    "udp.srcport",
    "udp.dstport",
    "frame.protocols"
]

def convert_pcap_to_csv(pcap_path: str, output_csv: str):
    tshark_path = shutil.which("tshark")
    if not tshark_path:
        print("❌ TShark not found. Please install Wireshark/TShark and add to PATH.")
        return

    tshark_cmd = [
        tshark_path,
        "-r", pcap_path,
        "-T", "fields",
        "-E", "header=y",
        "-E", "separator=/,",
        "-E", "quote=d"
    ]

    for field in FIELDS:
        tshark_cmd += ["-e", field]

    print(f"🚀 Converting {pcap_path} to {output_csv} ...")

    try:
        # 🔧 Cegah error: buat folder kalau belum ada
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)

        with open(output_csv, "w") as f:
            subprocess.run(tshark_cmd, stdout=f, stderr=subprocess.PIPE, check=True)
        print("✅ Conversion complete!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr.decode()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert .pcap file to .csv using TShark.")
    parser.add_argument("pcap_path", help="Path to the input .pcap file")
    parser.add_argument("output_csv", help="Path to save the output .csv file")
    args = parser.parse_args()

    convert_pcap_to_csv(args.pcap_path, args.output_csv)
