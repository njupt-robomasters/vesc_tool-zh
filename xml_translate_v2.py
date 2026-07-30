import sys
import os
import xml.etree.ElementTree as ET

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "res", "config")

groupName_translations = {
    "General": "\u901a\u7528",
    "Additional Info": "\u9644\u52a0\u4fe1\u606f",
    "VESC Remote": "VESC \u9065\u63a7\u5668",
    "PID Controllers": "PID \u63a7\u5236\u5668",
    "BMS": "BMS",
    "BLDC": "BLDC",
    "DC": "DC",
    "FOC": "FOC",
    "CAN": "CAN",
}

subgroupName_translations = {
    "General": "\u901a\u7528",
    "Sensors": "\u4f20\u611f\u5668",
    "Current": "\u7535\u6d41",
    "Voltage": "\u7535\u538b",
    "Wattage": "\u529f\u7387",
    "Temperature": "\u6e29\u5ea6",
    "Advanced": "\u9ad8\u7ea7",
    "Sensorless": "\u65e0\u611f",
    "Hall Sensors": "\u970d\u5c14\u4f20\u611f\u5668",
    "Encoder": "\u7f16\u7801\u5668",
    "Filter": "\u6ee4\u6ce2\u5668",
    "Filters": "\u6ee4\u6ce2\u5668",
    "Offsets": "\u504f\u79fb",
    "Field Weakening": "\u5f31\u78c1",
    "Setup": "\u8bbe\u7f6e",
    "Quality": "\u8d28\u91cf",
    "Mapping": "\u6620\u5c04",
    "Throttle Curve": "\u6cb9\u95e8\u66f2\u7ebf",
    "VSS": "VSS",
    "HFI": "HFI",
    "RPM": "RPM",
    "BMS": "BMS",
}

mcconf_enumName_translations = {
    "Nonsynchronous HISW": "\u975e\u540c\u6b65 HISW",
    "Synchronous": "\u540c\u6b65",
    "Bipolar": "\u53cc\u6781\u6027",
    "Integrate": "\u79ef\u5206",
    "Encoder Slip": "\u7f16\u7801\u5668\u6ed1\u52a8",
    "Overspeed": "\u8d85\u901f",
    "Underspeed": "\u6b20\u901f",
    "Absolute Overspeed": "\u7edd\u5bf9\u8d85\u901f",
    "Unused": "\u672a\u4f7f\u7528",
    "Hall Sensors": "\u970d\u5c14\u4f20\u611f\u5668",
    "AB Encoder (No Index Pulse)": "AB \u7f16\u7801\u5668\uff08\u65e0\u7d22\u5f15\u8109\u51b2\uff09",
    "V0 Only": "\u4ec5 V0",
    "V0 and V7": "V0 \u548c V7",
    "V0 and V7 Interpolation": "V0 \u548c V7 \u63d2\u503c",
    "Longest Zero Time": "\u6700\u957f\u96f6\u65f6\u95f4",
    "All Sensors Combined": "\u6240\u6709\u4f20\u611f\u5668\u7ec4\u5408",
    "High Current": "\u5927\u7535\u6d41",
    "Factor": "\u7cfb\u6570",
    "Lambda and Factor": "Lambda \u548c\u7cfb\u6570",
    "Six Vectors": "\u516d\u77e2\u91cf",
    "Id Single Pulse": "Id \u5355\u8109\u51b2",
    "Id Double Pulse": "Id \u53cc\u8109\u51b2",
    "IQ Target": "IQ \u76ee\u6807",
    "IQ Measured": "IQ \u6d4b\u91cf\u503c",
    "Corrected Position": "\u6821\u6b63\u4f4d\u7f6e",
    "Observer": "\u89c2\u6d4b\u5668",
    "Fast Estimator": "\u5feb\u901f\u4f30\u7b97\u5668",
    "Faster Estimator": "\u66f4\u5feb\u4f30\u7b97\u5668",
    "ABI Encoder": "ABI \u7f16\u7801\u5668",
    "AS5047 Encoder": "AS5047 \u7f16\u7801\u5668",
    "AD2S1205 Resolver": "AD2S1205 \u65cb\u8f6c\u53d8\u538b\u5668",
    "Sin/Cos Encoder": "\u6b63\u4f59\u5f26\u7f16\u7801\u5668",
    "TS5700N8501 Encoder": "TS5700N8501 \u7f16\u7801\u5668",
    "TS5700N8501 Encoder (Multiturn)": "TS5700N8501 \u7f16\u7801\u5668\uff08\u591a\u5708\uff09",
    "MT6816 Encoder (SPI)": "MT6816 \u7f16\u7801\u5668\uff08SPI\uff09",
    "AS5X47U Encoder (SPI)": "AS5X47U \u7f16\u7801\u5668\uff08SPI\uff09",
    "AS5X47U Encoder": "AS5X47U \u7f16\u7801\u5668",
    "BISSC Encoder (SPI)": "BISSC \u7f16\u7801\u5668\uff08SPI\uff09",
    "TLE5012 Encoder (SSC SW)": "TLE5012 \u7f16\u7801\u5668\uff08SSC SW\uff09",
    "TLE5012 Encoder (SSC HW)": "TLE5012 \u7f16\u7801\u5668\uff08SSC HW\uff09",
    "Custom Encoder": "\u81ea\u5b9a\u4e49\u7f16\u7801\u5668",
    "PWM + ABI": "PWM + ABI",
    "AMT22 (SW SPI)": "AMT22\uff08SW SPI\uff09",
    "Current Limit": "\u7535\u6d41\u9650\u5236",
    "OC Latch Shutdown": "OC \u9501\u5b58\u5173\u65ad",
    "Report Only": "\u4ec5\u62a5\u544a",
    "On after 2 seconds": "2 \u79d2\u540e\u4eae",
    "On after 5 seconds": "5 \u79d2\u540e\u4eae",
    "On after 10 seconds": "10 \u79d2\u540e\u4eae",
    "On when running": "\u8fd0\u884c\u65f6\u4eae",
    "On when not running": "\u505c\u6b62\u65f6\u4eae",
    "Temp motor > 50 C": "\u7535\u673a\u6e29\u5ea6 > 50\u00b0C",
    "Temp mosfet > 50 C": "MOSFET \u6e29\u5ea6 > 50\u00b0C",
    "Temp motor > 70 C": "\u7535\u673a\u6e29\u5ea6 > 70\u00b0C",
    "Temp mosfet > 70 C": "MOSFET \u6e29\u5ea6 > 70\u00b0C",
    "Temp motor or mosfet > 50 C": "\u7535\u673a\u6216 MOSFET \u6e29\u5ea6 > 50\u00b0C",
    "Temp motor or mosfet > 70 C": "\u7535\u673a\u6216 MOSFET \u6e29\u5ea6 > 70\u00b0C",
    "NTC 10K at 25 C": "NTC 10K \u5728 25\u00b0C",
    "NTC 10K at 25\u00b0C": "NTC 10K \u5728 25\u00b0C",
    "PTC 1K at 100 C": "PTC 1K \u5728 100\u00b0C",
    "PTC 1K at 100 \u00b0C": "PTC 1K \u5728 100\u00b0C",
    "NTC 100K at 25 C": "NTC 100K \u5728 25\u00b0C",
    "NTC 100K at 25\u00b0C": "NTC 100K \u5728 25\u00b0C",
    "NTC Custom": "\u81ea\u5b9a\u4e49 NTC",
    "PTC Custom": "\u81ea\u5b9a\u4e49 PTC",
    "BATTERY_TYPE_LIION_3_0__4_2": "\u9502\u79bb\u5b50 3.0-4.2V",
    "BATTERY_TYPE_LIIRON_2_6__3_6": "\u9502\u94c1 2.6-3.6V",
    "BATTERY_TYPE_LEAD_ACID": "\u94c5\u9178",
    "No sensor": "\u65e0\u4f20\u611f\u5668",
    "Other Sensor": "\u5176\u4ed6\u4f20\u611f\u5668",
    "Overtemp": "\u8fc7\u6e29",
    "VCell Min": "\u7535\u82af\u6700\u4f4e\u7535\u538b",
    "VCell Max": "\u7535\u82af\u6700\u9ad8\u7535\u538b",
    "USB Only": "\u4ec5 USB",
    "Any Interface": "\u4efb\u610f\u63a5\u53e3",
    "Calibrate on Boot": "\u542f\u52a8\u65f6\u6821\u51c6",
    "Write Enabled": "\u5199\u5165\u5df2\u542f\u7528",
    "Auto Calibrate": "\u81ea\u52a8\u6821\u51c6",
    "Off": "\u5173",
    "Delay": "\u5ef6\u8fdf",
    "Disabled": "\u7981\u7528",
    "Hybrid": "\u6df7\u5408",
    "None": "\u65e0",
    "Sensored": "\u6709\u611f",
    "Sensorless": "\u65e0\u611f",
    "PLL": "\u9501\u76f8\u73af",
    "PWM": "PWM",
    "SOC": "SOC",
    "VESC BMS": "VESC BMS",
    "Lambda": "Lambda",
    "45 Deg V0 HFI": "45\u00b0 V0 \u9ad8\u9891\u6ce8\u5165",
    "45 Deg V0V7 HFI (Silent)": "45\u00b0 V0V7 \u9ad8\u9891\u6ce8\u5165\uff08\u9759\u97f3)",
    "Coupled V0 HFI": "\u8026\u5408 V0 \u9ad8\u9891\u6ce8\u5165",
    "Coupled V0V7 HFI (Silent)": "\u8026\u5408 V0V7 \u9ad8\u9891\u6ce8\u5165\uff08\u9759\u97f3)",
    "PID Position Control: 180": "PID \u4f4d\u7f6e\u63a7\u5236\uff1a180",
    "PID Position Control: 180\u00b0": "PID \u4f4d\u7f6e\u63a7\u5236\uff1a180\u00b0",
    "PID Position Control: 360": "PID \u4f4d\u7f6e\u63a7\u5236\uff1a360",
    "PID Position Control: 360\u00b0": "PID \u4f4d\u7f6e\u63a7\u5236\uff1a360\u00b0",
}

appconf_enumName_translations = {
    "Status 1": "\u72b6\u6001 1",
    "Status 2": "\u72b6\u6001 2",
    "Status 3": "\u72b6\u6001 3",
    "Status 4": "\u72b6\u6001 4",
    "Status 5": "\u72b6\u6001 5",
    "Status 6": "\u72b6\u6001 6",
    "ALWAYS_OFF": "\u59cb\u7ec8\u5173\u95ed",
    "ALWAYS_ON": "\u59cb\u7ec8\u5f00\u542f",
    "TOGGLE_BUTTON_ONLY": "\u4ec5\u5207\u6362\u6309\u94ae",
    "OFF_AFTER_10S": "10 \u79d2\u540e\u5173\u95ed",
    "OFF_AFTER_1M": "1 \u5206\u949f\u540e\u5173\u95ed",
    "OFF_AFTER_5M": "5 \u5206\u949f\u540e\u5173\u95ed",
    "OFF_AFTER_10M": "10 \u5206\u949f\u540e\u5173\u95ed",
    "OFF_AFTER_30M": "30 \u5206\u949f\u540e\u5173\u95ed",
    "OFF_AFTER_1H": "1 \u5c0f\u65f6\u540e\u5173\u95ed",
    "OFF_AFTER_5H": "5 \u5c0f\u65f6\u540e\u5173\u95ed",
    "Comm Bridge": "\u901a\u4fe1\u6865",
    "UAVCAN and VESC": "UAVCAN \u548c VESC",
    "Current Control": "\u7535\u6d41\u63a7\u5236",
    "Duty Cycle Control": "\u5360\u7a7a\u6bd4\u63a7\u5236",
    "RPM Control": "RPM \u63a7\u5236",
    "Motor Current": "\u7535\u673a\u7535\u6d41",
    "Input Current": "\u8f93\u5165\u7535\u6d41",
    "PPM Low": "PPM \u4f4e",
    "PPM High": "PPM \u9ad8",
    "ADC2 Low": "ADC2 \u4f4e",
    "ADC2 High": "ADC2 \u9ad8",
    "No App": "\u65e0\u5e94\u7528",
    "PPM and UART": "PPM \u548c UART",
    "ADC and UART": "ADC \u548c UART",
    "Nunchuk (I2C, Nyko Kama)": "Nunchuk\uff08I2C\uff0cNyko Kama\uff09",
    "Custom User App": "\u81ea\u5b9a\u4e49\u7528\u6237\u5e94\u7528",
    "ADC and PAS": "ADC \u548c PAS",
    "Current No Reverse": "\u7535\u6d41\u65e0\u53cd\u8f6c",
    "Current No Reverse With Brake": "\u7535\u6d41\u65e0\u53cd\u8f6c\u5e26\u5239\u8f66",
    "Duty Cycle No Reverse": "\u5360\u7a7a\u6bd4\u65e0\u53cd\u8f6c",
    "PID Speed Control": "PID \u901f\u5ea6\u63a7\u5236",
    "PID Speed Control No Reverse": "PID \u901f\u5ea6\u63a7\u5236\u65e0\u53cd\u8f6c",
    "Current Hyst Reverse With Brake": "\u7535\u6d41\u6ede\u56de\u53cd\u8f6c\u5e26\u5239\u8f66",
    "Current Smart Reverse": "\u7535\u6d41\u667a\u80fd\u53cd\u8f6c",
    "Exponential": "\u6307\u6570",
    "Natural": "\u81ea\u7136",
    "Polynomial": "\u591a\u9879\u5f0f",
    "Regular": "\u5e38\u89c4",
    "No Fault": "\u65e0\u6545\u969c",
    "Current Reverse Center": "\u7535\u6d41\u53cd\u8f6c\u56de\u4e2d",
    "Current Reverse Button": "\u7535\u6d41\u53cd\u8f6c\u6309\u94ae",
    "Current Reverse ADC2 Brake Button": "\u7535\u6d41\u53cd\u8f6c ADC2 \u5239\u8f66\u6309\u94ae",
    "Current Reverse Button Brake Center": "\u7535\u6d41\u53cd\u8f6c\u6309\u94ae\u5239\u8f66\u56de\u4e2d",
    "Current No Reverse Brake Center": "\u7535\u6d41\u65e0\u53cd\u8f6c\u5239\u8f66\u56de\u4e2d",
    "Current No Reverse Brake Button": "\u7535\u6d41\u65e0\u53cd\u8f6c\u5239\u8f66\u6309\u94ae",
    "Current No Reverse Brake ADC2": "\u7535\u6d41\u65e0\u53cd\u8f6c\u5239\u8f66 ADC2",
    "Duty Cycle Reverse Center": "\u5360\u7a7a\u6bd4\u53cd\u8f6c\u56de\u4e2d",
    "Duty Cycle Reverse Button": "\u5360\u7a7a\u6bd4\u53cd\u8f6c\u6309\u94ae",
    "PID Speed": "PID \u901f\u5ea6",
    "PID Speed Reverse Center": "PID \u901f\u5ea6\u53cd\u8f6c\u56de\u4e2d",
    "PID Speed Reverse Button": "PID \u901f\u5ea6\u53cd\u8f6c\u6309\u94ae",
    "Enable Cruise Control": "\u542f\u7528\u5de1\u822a\u63a7\u5236",
    "Invert CC Button": "\u53cd\u8f6c\u5de1\u822a\u6309\u94ae",
    "Invert Reverse Button": "\u53cd\u8f6c\u53cd\u5411\u6309\u94ae",
    "Current Bidirectional": "\u7535\u6d41\u53cc\u5411",
    "OFF": "\u5173\u95ed",
    "1 Byte": "1 \u5b57\u8282",
    "2 Byte": "2 \u5b57\u8282",
    "Cadence": "\u8e0f\u9891",
    "Constant Torque": "\u6052\u626d\u77e9",
    "Quadrature": "\u6b63\u4ea4",
    "CAN_BAUD_10K": "CAN \u6ce2\u7279\u7387 10K",
    "CAN_BAUD_20K": "CAN \u6ce2\u7279\u7387 20K",
    "CAN_BAUD_50K": "CAN \u6ce2\u7279\u7387 50K",
    "CAN_BAUD_75K": "CAN \u6ce2\u7279\u7387 75K",
    "CAN_BAUD_100K": "CAN \u6ce2\u7279\u7387 100K",
    "CAN_BAUD_125K": "CAN \u6ce2\u7279\u7387 125K",
    "CAN_BAUD_250K": "CAN \u6ce2\u7279\u7387 250K",
    "CAN_BAUD_500K": "CAN \u6ce2\u7279\u7387 500K",
    "CAN_BAUD_1M": "CAN \u6ce2\u7279\u7387 1M",
    "AHRS_MODE_MADGWICK": "Madgwick \u7b97\u6cd5",
    "AHRS_MODE_MADGWICK_FUSION": "Madgwick \u878d\u5408",
    "AHRS_MODE_MAHONY": "Mahony \u7b97\u6cd5",
    "IMU_TYPE_OFF": "\u5173\u95ed",
    "IMU_TYPE_INTERNAL": "\u5185\u90e8",
    "IMU_TYPE_EXTERNAL_MPU9X50": "\u5916\u90e8 MPU9X50",
    "IMU_TYPE_EXTERNAL_ICM20948": "\u5916\u90e8 ICM20948",
    "IMU_TYPE_EXTERNAL_BMI160": "\u5916\u90e8 BMI160",
    "IMU_TYPE_EXTERNAL_LSM6DS3": "\u5916\u90e8 LSM6DS3",
    "IMU_FILTER_LOW": "\u4f4e",
    "IMU_FILTER_MEDIUM": "\u4e2d",
    "IMU_FILTER_HIGH": "\u9ad8",
    "ADC": "ADC",
    "Current": "\u7535\u6d41",
    "Duty Cycle": "\u5360\u7a7a\u6bd4",
    "PAS": "\u8e0f\u677f\u8f85\u52a9",
    "PPM": "PPM",
    "NRF": "NRF",
    "UART": "UART",
    "UAVCAN": "UAVCAN",
    "VESC": "VESC",
    "Current No Reverse Brake": "\u7535\u6d41\u65e0\u53cd\u8f6c\u5239\u8f66",
}


def translate_element_text(element, translations, context_name):
    if element.text is not None:
        old_text = element.text.strip()
        if old_text in translations:
            new_text = translations[old_text]
            if old_text != new_text:
                element.text = new_text
                return True
    return False


def process_xml_file(filepath, file_type):
    modified = False
    tree = ET.parse(filepath)
    root = tree.getroot()

    if file_type == "mcconf":
        enum_translations = mcconf_enumName_translations
    else:
        enum_translations = appconf_enumName_translations

    for elem in root.iter():
        tag = elem.tag

        if tag == "groupName":
            if translate_element_text(elem, groupName_translations, "groupName"):
                modified = True

        elif tag == "subgroupName":
            if translate_element_text(elem, subgroupName_translations, "subgroupName"):
                modified = True

        elif tag == "enumNames":
            if translate_element_text(elem, enum_translations, "enumNames"):
                modified = True

    if modified:
        et = ET.ElementTree(root)
        et.write(filepath, encoding="utf-8", xml_declaration=True)
        print("Modified: %s" % filepath)

    return modified


def find_version_dirs(base_dir):
    version_dirs = []
    if not os.path.isdir(base_dir):
        print("Error: Directory not found: %s" % base_dir)
        return version_dirs

    for entry in os.listdir(base_dir):
        entry_path = os.path.join(base_dir, entry)
        if os.path.isdir(entry_path):
            mcconf_path = os.path.join(entry_path, "parameters_mcconf.xml")
            appconf_path = os.path.join(entry_path, "parameters_appconf.xml")
            if os.path.isfile(mcconf_path) and os.path.isfile(appconf_path):
                version_dirs.append(entry)
    return sorted(version_dirs)


def main():
    if not os.path.isdir(BASE_DIR):
        print("Error: res/config directory not found at %s" % BASE_DIR)
        sys.exit(1)

    versions = find_version_dirs(BASE_DIR)
    if not versions:
        print("No version directories found with expected XML files.")
        sys.exit(1)

    print("Found %d version directories." % len(versions))
    total_modified = 0

    for version in versions:
        ver_dir = os.path.join(BASE_DIR, version)

        mcconf_path = os.path.join(ver_dir, "parameters_mcconf.xml")
        appconf_path = os.path.join(ver_dir, "parameters_appconf.xml")

        m_modified = process_xml_file(mcconf_path, "mcconf")
        if m_modified:
            total_modified += 1

        a_modified = process_xml_file(appconf_path, "appconf")
        if a_modified:
            total_modified += 1

    print("Total files modified: %d" % total_modified)


if __name__ == "__main__":
    main()
