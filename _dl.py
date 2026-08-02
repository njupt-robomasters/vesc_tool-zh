import re, os, urllib.request

# Download all XML files for all versions
versions = ["3.55","3.56","3.57","3.58","3.59","3.60","3.61","3.62","3.63","3.64","3.65","3.66",
            "4.00","4.01","4.02","5.00","5.01","5.02","5.03",
            "6.00","6.02","6.05","6.06","7.00"]

files = ["parameters_mcconf.xml", "parameters_appconf.xml", "info.xml"]
base = "https://raw.githubusercontent.com/vedderb/vesc_tool/master/res/config"

# Use urllib with timeout
import socket
socket.setdefaulttimeout(30)

for ver in versions:
    os.makedirs(f"res/config/{ver}", exist_ok=True)
    for fn in files:
        url = f"{base}/{ver}/{fn}"
        path = f"res/config/{ver}/{fn}"
        try:
            urllib.request.urlretrieve(url, path)
            print(f"OK: {ver}/{fn}")
        except Exception as e:
            print(f"ERR: {ver}/{fn}: {e}")

print("Done")