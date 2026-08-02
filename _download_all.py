import os
import urllib.request

# All firmware versions available in res/config
versions = ["3.55","3.56","3.57","3.58","3.59","3.60","3.61","3.62","3.63","3.64","3.65","3.66",
            "4.00","4.01","4.02",
            "5.00","5.01","5.02","5.03",
            "6.00","6.02","6.05","6.06","7.00"]

files = ["parameters_mcconf.xml", "parameters_appconf.xml", "info.xml"]
base_url = "https://raw.githubusercontent.com/vedderb/vesc_tool/master/res/config"

total = 0
for ver in versions:
    os.makedirs(f"res/config/{ver}", exist_ok=True)
    for fname in files:
        url = f"{base_url}/{ver}/{fname}"
        dest = f"res/config/{ver}/{fname}"
        try:
            print(f"Downloading {ver}/{fname}...", end=" ")
            urllib.request.urlretrieve(url, dest)
            size = os.path.getsize(dest)
            print(f"OK ({size} bytes)")
            total += 1
        except Exception as e:
            print(f"FAILED: {e}")

print(f"\nDownloaded {total}/72 files")