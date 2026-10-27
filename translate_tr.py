import re, glob

D = r'''
Append Imports|追加导入
Line: %1: Invalid import tag.|第 %1 行：导入标签无效。
Tag %1 not found in package %2. %3|在软件包 %2 中未找到标签 %1。%3
Line: %1: Imported file cannot be opened.|第 %1 行：无法打开导入的文件。
Line: %1: Imported file not found: %2. %3|第 %1 行：未找到导入的文件：%2。%3
Imports|导入
%1 imports found. Do you want to save them as files?|发现 %1 个导入。是否将其保存为文件？
Choose Directory|选择目录
Replace File|替换文件
File %1 exists. Do you want to replace it?|文件 %1 已存在。是否替换？
Save Import|保存导入
Unpack VESC Package|解包 VESC 软件包
Could not open package file for reading.|无法打开软件包文件进行读取。
Invalid package file.|软件包文件无效。
Write Package|写入软件包
Package is not valid.|软件包无效。
Spaces are not allowed in the name.|名称中不允许包含空格。
Name is empty.|名称为空。
Parameter updated: %1|参数已更新：%1
New parameter added: %1|已添加新参数：%1
Choose parameter file to load|选择要加载的参数文件
Could not load parameters:<BR>%1|无法加载参数：<BR>%1
Configuration Loaded|配置已加载
Choose where to save the parameter XML file|选择参数 XML 文件的保存位置
Could not save parameters:<BR>%1|无法保存参数：<BR>%1
Configuration Saved|配置已保存
Are you sure that you want to delete all data?|确定要删除所有数据吗？
Configuration Deleted|配置已删除
Choose where to save the configuration header file|选择配置头文件的保存位置
h files (*.h)|h 头文件 (*.h)
Save header|保存头文件
Spaces are not allowed in the filename.|文件名中不允许包含空格。
Could not save header|无法保存头文件
%1 Bytes|%1 字节
Choose where to save the parser C source and header file|选择解析器 C 源文件和头文件的保存位置
C Source/Header files (*.c *.h)|C 源文件/头文件 (*.c *.h)
Choose where to save the config C source and header file|选择配置 C 源文件和头文件的保存位置
Choose the XML file or one of the C files. All files will be created with default names and/or overwritten if they already exist in the directory.|选择 XML 文件或其中一个 C 文件。所有文件将使用默认名称创建，若目录中已存在同名文件则会被覆盖。
C Source/Header files (*.c *.h *.xml)|C 源文件/头文件 (*.c *.h *.xml)
The firmware you are trying to upload is too large for the bootloader even after compression.|您尝试上传的固件即使经过压缩，对于引导程序来说仍然过大。
The firmware you are trying to upload is unreasonably large, most likely it is an invalid file|您尝试上传的固件大得不合理，很可能是无效文件
Reconnect|重新连接
No ports found|未找到端口
Please specify the connection manually the first time you are connecting.|首次连接时请手动指定连接方式。
Connected (CAN bus) to %1|已连接（CAN 总线）到 %1
Connected (TCP) to %1:%2|已连接（TCP）到 %1:%2
Connected (UDP) to %1:%2|已连接（UDP）到 %1:%2
Connected (BLE) to %1|已连接（BLE）到 %1
, limited mode|，受限模式
Serial port is not writable|串口不可写
Connect serial|连接串口
Serial port support is not enabled in this build of VESC Tool.|此版本的 VESC Tool 未启用串口支持。
Error creating device '%1' using backend '%2', reason: '%3'|使用后端“%2”创建设备“%1”时出错，原因：“%3”
Connection error: %1|连接错误：%1
CAN bus support is not enabled in this build of VESC Tool.|此版本的 VESC Tool 未启用 CAN 总线支持。
TCP Error|TCP 错误
UDP Error|UDP 错误
No firmware read response|读取固件无响应
Read Firmware Version|读取固件版本
Could not read firmware version. Make sure that the selected port really belongs to the VESC. If you are using UART, make sure that the port is enabled, connected correctly (rx to tx and tx to rx) and uses the correct baudrate|无法读取固件版本。请确认所选端口确实属于 VESC。如果使用 UART，请确认该端口已启用、接线正确（rx 接 tx，tx 接 rx）且波特率正确
This version of VESC Tool does not seem to have any supported firmwares. Something is probably wrong with the motor configuration file.|此版本的 VESC Tool 似乎没有任何受支持的固件。电机配置文件可能有问题。
Error|错误
The firmware on the connected device is too old. Please update it using a programmer.|已连接设备的固件过旧。请使用编程器更新。
Warning|警告
The connected device has newer firmware than this version of VESC Tool supports. It is recommended that you update VESC Tool to the latest version. Alternatively, the firmware on the connected device can be downgraded in the firmware page. Until then, limited communication mode will be used.|已连接设备的固件比此版本 VESC Tool 支持的更新。建议将 VESC Tool 更新到最新版本；也可以在固件页面降级已连接设备的固件。在此之前将使用受限通信模式。
The connected VESC-based ESC has too old firmware. Since the connected VESC has firmware with bootloader support, it can be updated from the Firmware page. Until then, limited communication mode will be used.|已连接的 VESC 电调固件过旧。由于其固件支持引导程序，可在固件页面更新。在此之前将使用受限通信模式。
The connected device has compatible, but old firmware. It is recommended that you update it.|已连接设备的固件兼容但较旧。建议更新。
%1 updated|%1 已更新
Update CAN Baudrate|更新 CAN 波特率
This is going to update the CAN-bus baudrate on all connected VESC-based devices. This is only supported in firmware 6.06 or later. If the update fails the CAN-bus might become unusable until it is reconfigured manually. Do you want to continue?|此操作将更新所有已连接的 VESC 设备的 CAN 总线波特率，仅支持固件 6.06 或更高版本。如果更新失败，CAN 总线可能无法使用，直到手动重新配置。是否继续？
Applying Pulselengths Failed|应用脉宽失败
Please activate RT app data and measure the ADC voltages first.|请先激活实时应用数据并测量 ADC 电压。
Please activate RT app data and measure the pulselengths first.|请先激活实时应用数据并测量脉宽。
Medium Outrunner (~750 g)|中型外转子 (~750 g)
Large Outrunner (~2000 g)|大型外转子 (~2000 g)
Small Inrunner (~200 g)|小型内转子 (~200 g)
Medium Inrunner (~750 g)|中型内转子 (~750 g)
Large Inrunner (~2000 g)|大型内转子 (~2000 g)
E-Bike DD hub motor (~6 kg)|电动自行车直驱轮毂电机 (~6 kg)
EDF Inrunner Small (~200 g)|涵道风扇内转子（小型）(~200 g)
<font color="red">Warning: </font>This is going to spin up all motors connected on the CAN-bus. Make sure that nothing is in the way.|<font color="red">警告：</font>此操作将使 CAN 总线上连接的所有电机旋转。请确保周围没有障碍物。
Measure Error|测量错误
<font color="red">Warning: </font>This is going to spin up the motor. Make sure that nothing is in the way.|<font color="red">警告：</font>此操作将使电机旋转。请确保周围没有障碍物。
As the current is 0 this is going to perform passive flux linkage measurement. Make sure that the motor is driven externally.|由于电流为 0，将执行被动磁链测量。请确保电机由外部驱动。
Apply Error|应用错误
L is 0. Please measure it first.|L 为 0。请先测量 L。
Temp comp base temp applied|温度补偿基准温度已应用
Apply Parameters Failed|应用参数失败
Calculate Error|计算错误
Calculate|计算
This is going to calculate KP, KI and the observer gain from the old settings and the time constant, and apply them. This is useful for manually entering parameters, of for changing time constant without running detection. Do you want to proceed?|此操作将根据旧设置和时间常数计算 KP、KI 和观测器增益并应用。适用于手动输入参数，或在不运行检测的情况下更改时间常数。是否继续？
Apply Encoder Error|应用编码器错误
Please run flux linkage (FW 6.06+) or encoder detection first.|请先运行磁链检测（固件 6.06+）或编码器检测。
Xml files (*.xml)|XML 文件 (*.xml)
PNG Files (*.png)|PNG 文件 (*.png)
PDF Files (*.pdf)|PDF 文件 (*.pdf)
Csv files (*.csv)|CSV 文件 (*.csv)
Save %1|保存 %1
No file is open.|没有打开的文件。
'''
T = {}
for l in D.split('\n'):
    if '|' in l:
        k, v = l.split('|', 1)
        T[k] = v

LIT = re.compile(r'"((?:[^"\\]|\\.)*)"')
SEQ = re.compile(r'(?:\s*"(?:[^"\\]|\\.)*")+')
SKIP = ('vesc_tool-master', 'build', 'QCodeEditor', 'maddy', 'android', 'ios', 'lzokay', 'heatshrink', 'minimp3', 'qmarkdowntextedit')
miss = {}
replaced = 0
changed = 0
for f in glob.glob('**/*.cpp', recursive=True) + glob.glob('**/*.h', recursive=True):
    if f.startswith(SKIP):
        continue
    s = open(f, encoding='utf-8', newline='').read()
    edits = []
    for m in re.finditer(r'\btr\(\s*', s):
        r = SEQ.match(s, m.end())
        if not r:
            continue
        t = ''.join(LIT.findall(r.group(0)))
        if t in T:
            edits.append((m.end(), r.end(), T[t]))
        elif re.search('[a-z]{3}', t) and not re.search('[一-鿿]', t):
            miss[t] = f
    if edits:
        for a, b, v in reversed(edits):
            s = s[:a] + '"' + v + '"' + s[b:]
        open(f, 'w', encoding='utf-8', newline='').write(s)
        changed += 1
        replaced += len(edits)
print('files changed:', changed, 'tr replacements:', replaced)
print('remaining english:', len(miss))
for t, f in miss.items():
    print(f, '|', t[:1200])
