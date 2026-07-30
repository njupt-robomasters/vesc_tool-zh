#!/usr/bin/env python3
"""
Full XML translator using ElementTree for safe, structural translation.
Translates <longName> elements in parameters_mcconf.xml and parameters_appconf.xml
across all version directories under res/config/.
Only modifies elements with matching translations; leaves unknown text as-is.
"""

import os
import sys
import xml.etree.ElementTree as ET

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "res", "config")

LONGNAME_TRANSLATIONS = {
    # ===== mcconf: General Motor Settings =====
    "Motor Type": "电机类型",
    "Invert Motor Direction": "反转电机方向",
    "Sensor Port Mode": "传感器端口模式",
    "Encoder counts": "编码器计数",
    "Sensor Mode": "传感器模式",
    "PWM Mode": "PWM 模式",
    "Commutation Mode": "换向模式",
    "BMS Type": "BMS 类型",
    "BMS Limit Mode": "BMS 限制模式",

    # ===== mcconf: Current Limits =====
    "Motor Current Max": "电机最大电流",
    "Absolute Maximum Current": "绝对最大电流",
    "Slow ABS Current Limit": "慢速 ABS 电流限制",
    "Battery Current Max": "电池最大电流",
    "Battery Current Max Regen": "电池最大回生电流",
    "Input Current Limit Map Start": "最大输入电流斜坡起点",
    "Input Current Map Filter": "输入电流映射滤波",
    "Max Current Scale": "电流最大比例",
    "Min Current Scale": "电流最小比例",

    # ===== mcconf: Voltage Limits =====
    "Battery Voltage Cutoff Start": "电池电压截止起点",
    "Battery Voltage Cutoff End": "电池电压截止终点",
    "Battery Voltage Regen Cutoff Start": "电池回生电压截止起点",
    "Battery Voltage Regen Cutoff End": "电池回生电压截止终点",
    "Battery Filter Constant": "电池滤波常数",
    "Minimum Input Voltage": "最小输入电压",
    "Maximum Input Voltage": "最大输入电压",

    # ===== mcconf: RPM Limits =====
    "Max ERPM": "最大 ERPM",
    "Minimum ERPM": "最小 ERPM",
    "Max ERPM Reverse": "反向最大 ERPM",
    "ERPM Limit Start": "ERPM 限制起点",
    "Max ERPM Full Brake": "全刹车最大 ERPM",
    "Max ERPM Full Brake Current Control": "CC 全刹车最大 ERPM",

    # ===== mcconf: Duty Cycle =====
    "Minimum Duty Cycle": "最小占空比",
    "Maximum Duty Cycle": "最大占空比",
    "Duty Cycle Current Limit Start": "占空电流限制起点",

    # ===== mcconf: Power =====
    "Maximum Wattage": "最大功率",
    "Maximum Braking Wattage": "最大制动功率",

    # ===== mcconf: Temperature =====
    "MOSFET Temp Cutoff Start": "MOSFET 温度截止起点",
    "MOSFET Temp Cutoff End": "MOSFET 温度截止终点",
    "Motor Temp Cutoff Start": "电机温度截止起点",
    "Motor Temp Cutoff End": "电机温度截止终点",
    "Acceleration Temperature Decrease": "温度加速减速",
    "Motor Temperature Sensor Type": "电机温度传感器类型",
    "Beta Value for Motor Thermistor": "NTC 电机 Beta",
    "Coefficient for PTC Motor Thermistor": "PTC 电机系数",
    "Custom NTC/PTC Resistance": "自定义 NTC/PTC 电阻",
    "Custom NTC/PTC Base Temperature": "自定义 NTC/PTC 温度基准",

    # ===== mcconf: BLDC Settings =====
    "Cycle Integrator Limit": "周期积分限制",
    "BEMF Coupling": "BEMF 耦合常数",
    "Sensorless ERPM": "无感 ERPM",
    "Duty Ramp Step Max": "占空最大步长",
    "Current Backoff Gain": "电流回退增益",
    "Minimum Switching Frequency": "最小 PWM 频率",
    "Maximum Switching Frequency": "最大 PWM 频率",
    "Switching Frequency": "DC PWM 频率",
    "Phase Advance at BR ERPM": "全刹车相位提前",
    "BR ERPM": "全刹车 RPM",
    "Max Brake Current at Direction Change": "最大全刹车电流方向变化",

    # ===== mcconf: Hall Sensors =====
    "Hall Table [0]": "霍尔表 [0]",
    "Hall Table [1]": "霍尔表 [1]",
    "Hall Table [2]": "霍尔表 [2]",
    "Hall Table [3]": "霍尔表 [3]",
    "Hall Table [4]": "霍尔表 [4]",
    "Hall Table [5]": "霍尔表 [5]",
    "Hall Table [6]": "霍尔表 [6]",
    "Hall Table [7]": "霍尔表 [7]",
    "Hall Sensor Extra Samples": "霍尔额外采样",

    # ===== mcconf: FOC Motor Parameters =====
    "Motor Resistance (R)": "电机电阻（R）",
    "Motor Inductance (L)": "电机电感（L）",
    "Motor Inductance Difference (Lq - Ld)": "电机电感差（Lq - Ld）",
    "Motor Flux Linkage (\u03bb)": "电机磁链（\u03bb）",

    # ===== mcconf: FOC Current Controller =====
    "Current KP": "电流控制器 Kp",
    "Current KI": "电流控制器 Ki",

    # ===== mcconf: FOC Observer =====
    "Observer Gain (x1M)": "观测器增益（x1M）",
    "Observer Gain At Minimum Duty": "观测器增益（低速）",
    "Observer Type": "观测器类型",
    "Observer Offset": "观测器偏移",

    # ===== mcconf: FOC PLL / Ramp =====
    "Speed Tracker Kp": "PLL Kp",
    "Speed Tracker Ki": "PLL Ki",
    "Duty Downramp Kp": "占空下降斜坡 Kp",
    "Duty Downramp Ki": "占空下降斜坡 Ki",
    "Zero Vector Frequency": "零矢量频率",

    # ===== mcconf: FOC Dead Time =====
    "Dead Time Compensation": "死区补偿",

    # ===== mcconf: FOC Openloop =====
    "Openloop ERPM": "开环 ERPM",
    "Openloop ERPM at Min Current": "开环 低速 RPM",
    "Openloop Hysteresis": "SL 开环迟滞",
    "Openloop Lock Time": "SL 开环锁定时间",
    "Openloop Ramp Time": "SL 开环斜坡时间",
    "Openloop Time": "SL 开环时间",
    "Openloop Current Boost": "SL 开环增强 Q",
    "Openloop Current Max": "SL 开环最大 Q",

    # ===== mcconf: FOC Sensorless =====
    "Minimum ERPM Integrator": "开环 ERPM 起点",
    "Start Current Decrease": "启动电流衰减",
    "Start Current Decrease ERPM": "启动电流衰减 RPM",
    "Sensorless ERPM Hybrid": "无感混合 ERPM",
    "Sensorless ERPM HFI": "HFI SL ERPM",

    # ===== mcconf: FOC Encoder =====
    "Encoder Inverted": "编码器反转",
    "Encoder Offset": "编码器偏移",
    "Encoder Ratio": "编码器比率",

    # ===== mcconf: FOC Hall =====
    "Hall Interpolation ERPM": "霍尔插值 ERPM",
    "Sensored ERPM Start": "有感 ERPM 起点",

    # ===== mcconf: FOC Sampling =====
    "Control Sample Mode": "控制采样模式",
    "Current Sample Mode": "电流采样模式",

    # ===== mcconf: FOC Saturation / Temp Comp =====
    "Saturation Compensation Mode": "饱和补偿模式",
    "Saturation Compensation Factor": "饱和补偿因子",
    "Temp Comp": "温度补偿",
    "Temp Comp Base Temp": "温度补偿基准温度",

    # ===== mcconf: FOC Filter / Decoupling =====
    "Current Filter Constant": "电流滤波常数",
    "Current Controller Decoupling": "CC 解耦",

    # ===== mcconf: FOC HFI =====
    "HFI Ambiguity Resolve Mode": "HFI AMB 模式",
    "HFI Ambiguity Resolve Current": "HFI AMB 电流",
    "HFI Ambiguity Resolve Threshold": "HFI AMB 阈值",
    "HFI Start Voltage": "HFI 电压起点",
    "HFI Run Voltage": "HFI 电压运行",
    "HFI Max Voltage": "HFI 电压最大值",
    "HFI Gain": "HFI 增益",
    "HFI Max Error": "HFI 最大误差",
    "HFI Current Hysteresis": "HFI 迟滞",
    "HFI Reset ERPM": "HFI 重置 ERPM",
    "HFI Start Samples": "HFI 启动采样",
    "HFI Observer Override Time": "HFI 观测器覆盖时间",
    "HFI Samples": "HFI 采样",

    # ===== mcconf: FOC Offsets =====
    "Offset Calibration Mode": "偏移校准模式",
    "Current Offset 0": "电流偏移 0",
    "Current Offset 1": "电流偏移 1",
    "Current Offset 2": "电流偏移 2",
    "Voltage Offset 0": "电压偏移 0",
    "Voltage Offset 1": "电压偏移 1",
    "Voltage Offset 2": "电压偏移 2",
    "Voltage Offset Undriven 0": "电压未驱动偏移 0",
    "Voltage Offset Undriven 1": "电压未驱动偏移 1",
    "Voltage Offset Undriven 2": "电压未驱动偏移 2",

    # ===== mcconf: FOC Phase Filter =====
    "Enable Phase Filters": "相位滤波启用",
    "Maximum ERPM for phase filters": "相位滤波最大 ERPM",
    "Disable Phase Filter Fault Code": "相位滤波禁用故障码",

    # ===== mcconf: FOC Field Weakening / MTPA =====
    "MTPA Algorithm Mode": "MTPA 模式",
    "Field Weakening Current Max": "弱磁最大电流",
    "Field Weakening Duty Start": "弱磁占空起点",
    "Field Weakening Ramp Time": "弱磁斜坡时间",
    "Q Axis Current Factor": "弱磁 Q 电流系数",
    "Backoff Gain": "弱磁回退",

    # ===== mcconf: FOC Speed / Overmodulation =====
    "Speed Source": "速度源",
    "Short Low-Side FETs on Zero Duty": "零占空短路 LS",
    "Overmodulation Factor": "过调制系数",
    "Maximum VD Magnitude": "磁 Vd 最大值",

    # ===== mcconf: PID Controllers =====
    "PID Loop Rate": "PID 循环速率",
    "Speed PID Kp": "速度控制器 Kp",
    "Speed PID Ki": "速度控制器 Ki",
    "Speed PID Kd": "速度控制器 Kd",
    "Speed PID Kd Filter": "速度控制器 Kd 滤波",
    "Allow Braking": "速度控制器允许制动",
    "Ramp eRPMs per second": "速度控制器斜坡 ERPM/s",
    "Speed Tracker Position Source": "速度控制器速度源",

    # ===== mcconf: Position PID =====
    "Position PID Kp": "位置控制器 Kp",
    "Position PID Ki": "位置控制器 Ki",
    "Position PID Kd": "位置控制器 Kd",
    "Position PID Kd Process": "位置控制器 Kd 处理",
    "Position PID Kd Filter": "位置控制器 Kd 滤波",
    "Position Angle Division": "位置控制器角度分频",
    "Gain Decrease Angle": "位置控制器增益衰减角度",
    "Position PID Offset Angle": "位置控制器偏移角度",

    # ===== mcconf: Current Control =====
    "Startup boost": "启动增强占空",
    "Minimum Current": "最小电流",
    "Current Controller Gain": "电流控制器增益",
    "Current Control Ramp Step Max": "电流控制器最大斜坡步长",

    # ===== mcconf: Faults =====
    "Fault Stop Time": "故障停止时间",
    "Additional Faults": "附加故障",

    # ===== mcconf: DRV8301 =====
    "DRV8301 OC Mode": "DRV8301 过流模式",
    "DRV8301 OC Adjustment": "DRV8301 过流调整",

    # ===== mcconf: Auxiliary Output =====
    "Auxiliary Output Mode": "辅助输出模式",

    # ===== mcconf: Sin/Cos Encoder =====
    "Sine Amplitude": "正余弦编码器 Sin 幅度",
    "Cosine Amplitude": "正余弦编码器 Cos 幅度",
    "Sine Offset": "正余弦编码器 Sin 偏移",
    "Cosine Offset": "正余弦编码器 Cos 偏移",
    "Sin/Cos Filter Constant": "正余弦编码器滤波常数",
    "Sin/Cos Phase Correction": "正余弦编码器相位校正",

    # ===== mcconf: BMS Temperature / SOC / VCell =====
    "Temperature Limit Start": "温度限制起点",
    "Temperature Limit End": "温度限制终点",
    "SOC Limit Start": "SOC 限制起点",
    "SOC Limit End": "SOC 限制终点",
    "VCell Min Limit Start": "电芯最低电压限制起点",
    "VCell Min Limit End": "电芯最低电压限制终点",
    "VCell Max Limit Start": "电芯最高电压限制起点",
    "VCell Max Limit End": "电芯最高电压限制终点",
    "Forward CAN to Local": "转发 CAN 到本地",

    # ===== mcconf: Additional Info (Setup) =====
    "Motor Poles": "电机极数",
    "Gear Ratio": "齿轮比",
    "Wheel Diameter": "轮径",
    "Battery Type": "电池类型",
    "Battery Cells Series": "电池串数",
    "Battery Capacity": "电池容量",
    "Motor No Load Current": "电机空载电流",

    # ===== mcconf: Additional Info (General) =====
    "Motor Brand": "电机品牌",
    "Motor Model": "电机型号",
    "Motor Weight": "电机重量",
    "Position Sensor": "电机传感器类型",

    # ===== mcconf: Additional Info (Quality) =====
    "Bearing Quality": "电机轴承质量",
    "Magnet Quality": "电机磁铁质量",
    "Construction Quality": "电机结构质量",
    "Motor Description": "电机描述",
    "Quality Description": "质量描述",

    # ==================================================================
    # ===== appconf: General =====
    # ==================================================================
    "VESC ID": "VESC ID",
    "none": "无",
    "Timeout": "超时时间",
    "Timeout Brake Current": "超时刹车电流",
    "Safe Start": "安全启动",
    "Shutdown Mode": "关闭模式",
    "Send ACK": "发送 ACK",
    "Enable Permanent UART": "启用永久 UART",
    "Kill Switch Mode": "急停开关模式",
    "Enable Servo Output": "启用舵机输出",
    "APP to Use": "使用的应用",
    "Control Type": "控制类型",
    "Input Deadband": "输入死区",

    # ===== appconf: CAN =====
    "CAN Mode": "CAN 模式",
    "CAN Baud Rate": "CAN 波特率",
    "Can Status Rate 1": "CAN 状态速率 1",
    "Can Status Rate 2": "CAN 状态速率 2",
    "Can Messages Rate 1": "CAN 消息速率 1",
    "Can Messages Rate 2": "CAN 消息速率 2",
    "Multiple VESCs Over CAN": "CAN 多 VESC",
    "Pairing Done": "配对完成",

    # ===== appconf: UAVCAN =====
    "UAVCAN ESC Index": "UAVCAN ESC 索引",
    "UAVCAN Raw Throttle Mode": "UAVCAN 原始油门模式",
    "UAVCAN Raw RPM Max": "UAVCAN 原始 RPM 上限",
    "UAVCAN Status Current Mode": "UAVCAN 状态电流模式",

    # ===== appconf: PPM / ADC / NRF =====
    "Pulselength Start": "脉宽起始",
    "Pulselength Center": "脉宽中点",
    "Pulselength End": "脉宽终止",
    "ADC1 Start Voltage": "ADC1 起始电压",
    "ADC1 End Voltage": "ADC1 终止电压",
    "ADC1 Center Voltage": "ADC1 中点电压",
    "ADC2 Start Voltage": "ADC2 起始电压",
    "ADC2 End Voltage": "ADC2 终止电压",
    "ADC1 Abs Min Voltage": "ADC1 绝对最小电压",
    "ADC1 Abs Max Voltage": "ADC1 绝对最大电压",
    "Invert ADC1 Voltage": "反转 ADC1 电压",
    "Invert ADC2 Voltage": "反转 ADC2 电压",
    "Radio Channel": "无线频道",
    "Address 0": "地址 0",
    "Address 1": "地址 1",
    "Address 2": "地址 2",
    "Baudrate": "波特率",
    "TX Power": "发射功率",
    "Retries": "重试次数",
    "Retry Delay": "重试延迟",
    "Speed": "速度",
    "CRC": "CRC",
    "Sample Rate": "采样速率",
    "Update Rate": "更新速率",
    "Median Filter": "中值滤波",
    "Use Filter": "使用滤波",
    "Button Inputs": "按钮输入",

    # ===== appconf: Throttle Curve =====
    "Throttle Expo": "油门曲线指数",
    "Throttle Expo Brake": "刹车曲线指数",
    "Throttle Expo Mode": "曲线模式",

    # ===== appconf: Ramping =====
    "Positive Ramping Time": "正向斜坡时间",
    "Negative Ramping Time": "负向斜坡时间",

    # ===== appconf: PAS (Pedal Assist) =====
    "Sensor Type": "传感器类型",
    "Sensor Magnets": "传感器磁铁数",
    "Invert Pedal Direction": "反转踏板方向",
    "PAS Max Current": "PAS 最大电流",
    "Pedal RPM Start": "踏板 RPM 起点",
    "Pedal RPM End": "踏板 RPM 终点",

    # ===== appconf: Smart Reverse / Cruise =====
    "Use Smart Reverse": "使用智能反转",
    "Smart Reverse Max Duty Cycle": "智能反转最大占空比",
    "Smart Reverse Ramp Time": "智能反转斜坡时间",
    "Max ERPM for direction switch": "方向切换最大 ERPM",
    "ERPM Per Second Cruise Control": "巡航控制 ERPM/s",

    # ===== appconf: Traction Control =====
    "Traction Control": "牵引控制",
    "TC Max ERPM Difference": "TC 最大 ERPM 差",

    # ===== appconf: Coasting Brake =====
    "Coasting Brake Level": "滑行刹车等级",
    "Coasting Brake Ramp Time": "滑行刹车斜坡时间",

    # ===== appconf: PID Speed =====
    "PID Max ERPM": "PID 最大 ERPM",

    # ===== appconf: IMU =====
    "IMU Type": "IMU 类型",
    "IMU AHRS Mode": "IMU AHRS 模式",
    "Madgwick Beta": "Madgwick Beta",
    "Mahony KP": "Mahony KP",
    "Mahony KI": "Mahony KI",
    "Accel/Gyro Filter": "加速度/陀螺仪滤波",
    "Use magnetometer": "使用磁力计",
    "Accelerometer Confidence Decay": "加速度计置信度衰减",
    "Accel Offset X": "加速度 X 偏移",
    "Accel Offset Y": "加速度 Y 偏移",
    "Accel Offset Z": "加速度 Z 偏移",
    "Gyro Offset X": "陀螺仪 X 偏移",
    "Gyro Offset Y": "陀螺仪 Y 偏移",
    "Gyro Offset Z": "陀螺仪 Z 偏移",
    "Accel lowpass filter X": "加速度低通滤波 X",
    "Accel lowpass filter Y": "加速度低通滤波 Y",
    "Accel lowpass filter Z": "加速度低通滤波 Z",
    "Gyro lowpass filter": "陀螺仪低通滤波",
    "Imu Rotation Roll": "IMU 旋转 Roll",
    "Imu Rotation Pitch": "IMU 旋转 Pitch",
    "Imu Rotation Yaw": "IMU 旋转 Yaw",
}


def process_file(filepath):
    """Translate longName elements in a single XML file. Returns count of translations."""
    if not os.path.exists(filepath):
        return 0

    tree = ET.parse(filepath)
    root = tree.getroot()
    count = 0

    for elem in root.iter():
        tag = elem.tag.lower() if "}" not in elem.tag else elem.tag.split("}", 1)[1]

        if tag == "longname" and elem.text:
            stripped = elem.text.strip()
            if stripped in LONGNAME_TRANSLATIONS:
                new_text = LONGNAME_TRANSLATIONS[stripped]
                if stripped != new_text:
                    leading = elem.text[: len(elem.text) - len(elem.text.lstrip())]
                    trailing = elem.text[len(elem.text.rstrip()):]
                    elem.text = leading + new_text + trailing
                    count += 1

    if count > 0:
        tree.write(filepath, encoding="utf-8", xml_declaration=True)

    return count


def main():
    if not os.path.isdir(BASE):
        print(f"ERROR: Directory not found: {BASE}")
        sys.exit(1)

    versions = sorted([
        d for d in os.listdir(BASE)
        if os.path.isdir(os.path.join(BASE, d))
    ])

    total_longname = 0
    files_modified = 0

    for ver in versions:
        mcc = os.path.join(BASE, ver, "parameters_mcconf.xml")
        apc = os.path.join(BASE, ver, "parameters_appconf.xml")

        for fp in (mcc, apc):
            n = process_file(fp)
            if n > 0:
                total_longname += n
                files_modified += 1
                rel = os.path.relpath(fp, os.path.dirname(BASE))
                print(f"  {rel}: {n} translations")

    print()
    print(f"=== Summary ===")
    print(f"   longName translations: {total_longname}")
    print(f"   Files modified:        {files_modified}")
    print(f"   Versions processed:    {len(versions)}")

    # Verify key files are valid XML
    print()
    print("Verifying output...")
    verify = os.path.join(BASE, "7.00", "parameters_mcconf.xml")
    try:
        ET.parse(verify)
        print(f"  {os.path.relpath(verify)}: OK")
    except ET.ParseError as e:
        print(f"  {os.path.relpath(verify)}: BROKEN - {e}")

    verify = os.path.join(BASE, "7.00", "parameters_appconf.xml")
    try:
        ET.parse(verify)
        print(f"  {os.path.relpath(verify)}: OK")
    except ET.ParseError as e:
        print(f"  {os.path.relpath(verify)}: BROKEN - {e}")


if __name__ == "__main__":
    main()
