import re, glob

D = '''
最大 ERPM: |最大 ERPM：
最小 ERPM: |最小 ERPM：
ConfBackup|配置备份
HiRes|高分辨率
← Calc|← 计算
← For λ|← 用于 λ
← Param|← 参数
Same as FW &lt; 5.02|与固件 &lt; 5.02 相同
Show the Qt library's About box|显示 Qt 库的“关于”对话框
Manuallt add UUID to this instance of VESC Tool|手动将 UUID 添加到此 VESC Tool 实例
Use tiles from https://www.fau.de/|使用来自 https://www.fau.de/ 的地图瓦片
Use tiles from https://www.openstreetmap.org|使用来自 https://www.openstreetmap.org 的地图瓦片
Calculate KP, KI and Observer Gain from the entered settings and the time constant, and apply them.|根据输入的设置和时间常数计算 KP、KI 和观测器增益，并应用。
Corner to start crop. The image will not be drawn outside of the crop area. Cropping the drawing greatly improves performance.|裁剪起始角。图像不会绘制在裁剪区域之外。裁剪绘制区域可大幅提升性能。
Erase LispBM application from VESC. This will also prevent it from starting on next boot (as expected).|从 VESC 擦除 LispBM 应用。这也会阻止其在下次启动时运行（符合预期）。
Flash using the bootloader. Requires that the vesc-firmware alredy is present.|通过引导程序烧录。要求 VESC 固件已存在。
Maximum number of lines to show in REPL. Reducing this number improves performance when printing things fast.|REPL 中显示的最大行数。减小此数值可在快速打印时提升性能。
Number of samples total, or number of samples before trigger in triggered modes|采样总数；在触发模式下为触发前的采样数
Plot the difference between the observer and encoder position (FOC only)|绘制观测器与编码器位置之差（仅 FOC）
Plot the difference between the observer and hall sensor position (FOC only)|绘制观测器与霍尔传感器位置之差（仅 FOC）
Populate box without scanning, in case there are problems with scanning or the firmware does not support it.|不扫描直接填充列表，适用于扫描出现问题或固件不支持扫描的情况。
Refresh editor with file content. Warning: This will replace unsaved changes in the editor.|用文件内容刷新编辑器。警告：这将覆盖编辑器中未保存的更改。
Reload file from filesystem and run in panel. Warning: This will replace the editor content if it is unsaved.|从文件系统重新加载文件并在面板中运行。警告：若编辑器内容未保存，将被覆盖。
Remove comments, spaces and imports on upload. This saves space, but makes the code less readable when reading it back.|上传时移除注释、空格和导入。可节省空间，但回读时代码可读性会降低。
Remove selected recent file from list (file will not be deleted from file system)|从列表中移除所选的最近文件（不会删除文件系统中的文件）
Save overlay to layer 2 on image. Layer 2 can be enabled and disabled independently.|将叠加层保存到图像的第 2 层。第 2 层可独立启用或禁用。
Scale colors when loading image. Useful if the loaded image becomes too dark or too bright.|加载图像时缩放颜色。当加载的图像过暗或过亮时很有用。
Select which VESCs have inverted motor direction. Press the FWD or REV button to try.|选择哪些 VESC 的电机方向需要反向。按下 FWD 或 REV 按钮进行尝试。
Show centered graph, which is how the centered control modes interpret the throttle.|显示居中图，即居中控制模式解释油门的方式。
Stream code. This is faster and not persistent, but does not work with imports.|流式传输代码。速度更快但不会持久保存，且不支持导入。
This configuration is not supported by the socketcan backend. However it is possible to set the rate when configuring the CAN network interface using the ip link command.|socketcan 后端不支持此配置。不过，可以在使用 ip link 命令配置 CAN 网络接口时设置速率。
This pixel on the image will correspond to the position above|图像上的此像素将对应上方的位置
Triggered sampling when the motor starts without sending the samples automatically|电机启动时触发采样，不自动发送采样数据
Uninstall current package and install the selected package to the connected VESC|卸载当前软件包，并将所选软件包安装到已连接的 VESC
Unpair this VESC, and make it possible to connect to it from any VESC Tool instance.|取消此 VESC 的配对，使其可从任意 VESC Tool 实例连接。
Use file content when uploading/streaming/running code. If the content is not saved and a file path does not exist the editor content will be used instead.|上传/流式传输/运行代码时使用文件内容。若内容未保存且文件路径不存在，则改用编辑器内容。
'''
T = dict(l.split('|', 1) for l in D.splitlines() if '|' in l)

PROP = re.compile(r'(<(?:property|attribute) name=.(?:text|toolTip|title|windowTitle|suffix|prefix|placeholderText|statusTip|whatsThis|format).>[^<]*<string>)([^<]*)(</string>)')

files = [f for f in glob.glob('**/*.ui', recursive=True) if not f.startswith(('vesc_tool-master', 'build', 'application'))]
changed = 0
replaced = 0
for f in files:
    s = open(f, encoding='utf-8', newline='').read()
    def rep(m):
        global replaced
        k = m.group(2)
        if k in T:
            replaced += 1
            return m.group(1) + T[k] + m.group(3)
        return m.group(0)
    n = PROP.sub(rep, s)
    if n != s:
        open(f, 'w', encoding='utf-8', newline='').write(n)
        changed += 1

print('files changed:', changed, 'replacements:', replaced)
