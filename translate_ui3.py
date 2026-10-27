import re, glob, html

D = '''
Enable keyboard control.|启用键盘控制。
Key functions:|按键功能：
Up and Down Arrow Keys|上、下方向键
Current control using the current value in the lower|使用左下角设定的
left corner.|电流值进行电流控制。
Right and Left Arrow Keys|左、右方向键
Duty cycle control. Slowly ramps up and down the duty|占空比控制。缓慢地增大和减小
cycle. When e.g. starting with right and then also holding|占空比。例如先按住右键，再同时按住
left, the duty cycle is ramped higher.|左键，占空比将被升得更高。
Page Down|Page Down 键
Brake with the current set in the lower left corner.|使用左下角设定的电流进行刹车。
Parameter|参数
Editor|编辑器
This is what the editor of this parameter is going to look like. This preview is updated when a parameter is opened for editing, and when changes are saved.|此处显示该参数编辑器的外观预览。打开参数进行编辑以及保存更改时，预览会随之更新。
Save changes (or make new parameter if this name does not exist)|保存更改（如果该名称不存在，则新建参数）
Serialization Order|序列化顺序
Groups|分组
Subgroups|子分组
Parameters|参数
Scale the user intefrace with this factor. Useful for high resolution monitors. VESC Tool must be restarted for this setting to take effect.|按此系数缩放用户界面，适用于高分辨率显示器。需要重启 VESC Tool 后此设置才会生效。
Line thickness for the graphs in plots.|图表中曲线的线条粗细。
Upload firmware to the connected VESC, as well as to the VESCs connected over CAN-bus. Only available in FW3.45+.|将固件上传到已连接的 VESC，以及通过 CAN 总线连接的所有 VESC。仅适用于固件 3.45 及以上版本。
WARNING|警告
: This function should |：此功能应
only|仅
 be used if all VESCs on the CAN-bus have the same hardware version. Otherwise, the firmware has to be updated on them individually.|在 CAN 总线上所有 VESC 的硬件版本相同时使用。否则，必须逐个更新各 VESC 的固件。
Show this data series on the second Y axis to the right|将此数据系列显示在右侧的第二条 Y 轴上
Y axes will be autoscaled independently|各 Y 轴将独立自动缩放
Torque-sweep at fixed RPM and limited bus voltage. Uses field weakening according to the current in the FW-box.|在固定 RPM 和受限母线电压下进行扭矩扫描。弱磁电流按 FW 输入框中的值使用。
Torque + RPM Exponential mode. Sweep from 0 to end RPM and use the base torque + exponent on the RPM to derive the power requirement. The test will be scaled such that the specified power is at the full RPM. The power for the base torque will be required in addition to that.|扭矩 + RPM 指数模式。从 0 扫描到结束 RPM，并使用基础扭矩加上 RPM 的指数来推导功率需求。测试会按比例缩放，使指定功率出现在满转速处。基础扭矩所需的功率需另行叠加。
Propellers and impellers in air and water usually just have the exponent while traction vehicles have a base torque from the rolling resistance + an exponent from wind resistance.|空气和水中的螺旋桨与叶轮通常只有指数项，而牵引类车辆的基础扭矩来自滚动阻力，指数项则来自风阻。
RPM sweep while limiting the torque by the bus voltage.|在由母线电压限制扭矩的条件下进行 RPM 扫描。
Log Realtime Data to File.|将实时数据记录到文件。
Go to |前往
Settings -> Paths|偏好设置 -> 路径
 to choose the output directory.| 选择输出目录。
Welcome to |欢迎使用
To get started, you can use the |开始使用时，可以通过
Setup Wizards|设置向导
 to configure the motor and app settings respectively. Otherwise, you can connect to your VESC in the |分别配置电机和应用设置。或者，您也可以在
Connection|连接
 page and go through the motor and app configuration pages manually.| 页面连接 VESC，然后手动完成电机和应用配置页面的设置。
Note|注意
: Leave below parameters at 0 for default values|：下方参数保持为 0 即使用默认值
ERPM/sec to ramp up the motor in openloop mode with.|开环模式下使电机升速所用的 ERPM/秒。
'''
T = {}
for l in D.split('\n'):
    if '|' in l:
        k, v = l.split('|', 1)
        T[k] = v

esc = lambda s: html.escape(s, quote=False)
Q = chr(39)
OLD = 'font-family:' + Q + 'Roboto' + Q
NEW = 'font-family:' + Q + 'Microsoft YaHei' + Q
STR = re.compile(r'(<string>)(&lt;[^<]*)(</string>)')
hits = 0

def fix(m):
    global hits
    body = m.group(2)
    for k, v in T.items():
        a = '&gt;' + esc(k) + '&lt;'
        if a in body:
            hits += 1
            body = body.replace(a, '&gt;' + esc(v) + '&lt;')
    body = body.replace(OLD, NEW)
    return m.group(1) + body + m.group(3)

files = [f for f in glob.glob('**/*.ui', recursive=True) if not f.startswith(('vesc_tool-master', 'build', 'application'))]
changed = 0
for f in files:
    s = open(f, encoding='utf-8', newline='').read()
    n = STR.sub(fix, s)
    if n != s:
        open(f, 'w', encoding='utf-8', newline='').write(n)
        changed += 1
print('files changed:', changed, 'node replacements:', hits)
