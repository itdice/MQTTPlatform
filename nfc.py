#
# nfc.py
# Wireless Network Term Project
#
# Created by IT DICE on 2023/06/05.
#
import subprocess

with subprocess.Popen(["nfc-poll"], stdout=subprocess.PIPE) as process:
    nfc_raw_data: str = process.stdout.read().decode("utf-8")
    nfc_uid = nfc_raw_data[nfc_raw_data.find('UID')+14:nfc_raw_data.find('UID')+28]

print(f"Result => {nfc_uid}")
