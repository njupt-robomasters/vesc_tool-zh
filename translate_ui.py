import re, glob

D = '''
 Deg| 度
%v Degrees|%v 度
(USB-)Serial|(USB-)串口
3D Plot|3D 图
ADC Voltage Mapping|ADC 电压映射
About Libraries Used|关于所用的库
About Qt|关于 Qt
About VESC Tool|关于 VESC Tool
Accel|加速度计
Accel/Gyro/Mag|加速度计/陀螺仪/磁力计
Acceptable motor power loss to derive current limits from.|用于推导电流限制的可接受电机功率损耗。
Activate IMU Sampling|启用 IMU 采样
Add|添加
Add Setup|添加配置
Add UUID|添加 UUID
Add group|添加分组
Add new|新增
Add the connected VESC without pairing it.|添加已连接的 VESC，无需配对。
Address|地址
Advanced|高级
Advanced search / replace text|高级查找/替换文本
After Stream: Load on top|流式传输后：在顶部加载
After Stream: Reload Flash &amp; Load|流式传输后：重新加载 Flash 并加载
After Stream: Reset &amp; Load|流式传输后：重置并加载
Ah Charge Total|累计充电 Ah
Ah Counter|Ah 计数
Ah Discharge Total|累计放电 Ah
Align Center|居中对齐
Align Justify|两端对齐
Align Left|左对齐
Align Right|右对齐
All|全部
All Data|全部数据
Anti Alias (2bpp)|抗锯齿 (2bpp)
Antialias|抗锯齿
Antialias when loading|加载时抗锯齿
App Config XML:|应用配置 XML：
App Data Poll Rate|应用数据轮询频率
App Setup|应用设置
App Target Settings|应用目标设置
App Test|应用测试
Application|应用
Applications|应用程序
Apply|应用
Apply Encoder|应用编码器
Apply calculated limits|应用计算出的限制
Apply detection result|应用检测结果
Apply detection results|应用检测结果
Apply font and settings|应用字体和设置
Apply min and max to configuration|将最小值和最大值应用到配置
Apply min, max and center to VESC Tool configuration|将最小值、最大值和中心值应用到 VESC Tool 配置
Archive|归档
Ask before loading QML UI|加载 QML 界面前询问
Auto-Scale Plot when samples are received|收到采样时自动缩放图表
AutoConnect|自动连接
AutoRun|自动运行
AutoZoom|自动缩放
Autoconnect|自动连接
Automatically connect to the VESC using the USB connection.|通过 USB 连接自动连接 VESC。
Automatically run program on upload|上传后自动运行程序
Autoscale plots after updates.|更新后自动缩放图表。
Autoscale plots with incoming samples|随新采样自动缩放图表
Autoscroll|自动滚动
Axis|轴
Axis 1|轴 1
Axis 2|轴 2
Axis 3|轴 3
Axis 4|轴 4
Axis Monitoring and Configuration|轴监控与配置
BEMF|反电动势
BLE Device|BLE 设备
BLE Firmware Upload|BLE 固件上传
BLE Firmware: |BLE 固件：
BMS Data Poll Rate|BMS 数据轮询频率
Backup Configuration|备份配置
Backup Configuration (no CAN)|备份配置（不含 CAN）
Backup Configurations (Including CAN)|备份配置（含 CAN）
Bal Off|均衡关
Bal On|均衡开
Base Torque|基础扭矩
Battery|电池
Battery Cutoff Calculator|电池截止电压计算器
Baud: |波特率：
Baudrate|波特率
Bidirectional|双向
Binding|绑定
Binding Plot|绑定图表
Bit rate: |比特率：
Bitfield|位域
Bluetooth LE|低功耗蓝牙
Board Setup|主板设置
Bold|粗体
Bold (CTRL+B)|粗体 (CTRL+B)
Bool|布尔
Bootloader|引导程序
Bootloader Upload|引导程序上传
Border|边框
Brake current|刹车电流
Browse directory of last log file.|浏览最近日志文件所在目录。
Browse...|浏览...
Bullet list (CTRL+-)|项目符号列表 (CTRL+-)
C Define|C 宏定义
CAN Bus Scan|CAN 总线扫描
CAN Forward|CAN 转发
CAN bus|CAN 总线
CAN bus interfaces detected|检测到的 CAN 总线接口
CAN-Devices|CAN 设备
Cal Zero Current|电流零点校准
Calc Apply Old|按旧方式计算并应用
Calculate Compressed C Array Size|计算压缩 C 数组大小
Calculate KP and KI (requires R and L)|计算 KP 和 KI（需要 R 和 L）
Calculate Observer Gain (requires λ)|计算观测器增益（需要 λ）
Calculate Packet Size|计算数据包大小
Calculate Size|计算大小
Calculate and apply all parameters|计算并应用所有参数
Calculate compressed QML size|计算压缩后的 QML 大小
Cancel|取消
Cancel Search|取消搜索
Cancel upload|取消上传
Case Sensitive|区分大小写
Cell Diff|单体压差
Cell Max|单体最高
Cell Min|单体最低
Cells|串数
Center|中心
Center: |中心：
Charge Input Voltage|充电输入电压
Chg Dis|充电禁用
Chg En|充电使能
Choose file...|选择文件...
Choose output directory|选择输出目录
Clear|清除
Clear Configuration Backups|清除配置备份
Clear Filter Text|清除过滤文本
Clear Layer 2|清除第 2 层
Clear Screen|清屏
Clear Terminal|清除终端
Clear all text from console|清除控制台所有文本
Clear data from plots|清除图表数据
Clear recent file list (nothing will be deleted from file system)|清除最近文件列表（不会删除文件系统中的文件）
Clear terminal|清除终端
Clear text below|清除下方文本
Client|客户端
Close|关闭
Close comparison graphs|关闭对比图
Close search|关闭搜索
Color|颜色
Color index on image to count as transparent.|图像上视为透明的颜色索引。
Compare|对比
Compensate for filter delay|补偿滤波器延迟
Configuration is OK (check this box manually when done)|配置正常（完成后手动勾选）
Configure|配置
Connect|连接
Connect Internal|连接内部
Connect USB Port|连接 USB 端口
Connect to a VESC node|连接到 VESC 节点
Connect to external MCU over SWD.|通过 SWD 连接外部 MCU。
Connect to internal NRF5x MCU|连接内部 NRF5x MCU
Connect to see relevant firmwares|连接后可查看相关固件
Connected Device|已连接设备
Connected VESC|已连接的 VESC
Connection|连接
Console|控制台
Console/REPL|控制台/REPL
Controls|控制
Copy (CTRL+C)|复制 (CTRL+C)
Create Package|创建软件包
Crop Size|裁剪尺寸
Crop Start|裁剪起点
Current|电流
Current Control|电流控制
Current Control Brake|电流控制刹车
Current In Max: |最大输入电流：
Current In Min: |最小输入电流：
Current Sweep|电流扫描
Current VESC output. Will be updated after writing the app configuration.|当前 VESC 输出。写入应用配置后更新。
Current control KI|电流环 KI
Current control KP|电流环 KP
Current for starting|启动电流
Current to use for spinning up the motor|用于带动电机旋转的电流
Current:|电流：
Custom|自定义
Custom File|自定义文件
Cut (CTRL+X)|剪切 (CTRL+X)
DRV Reset Latched Faults|DRV 复位锁存故障
Dark Mode|夜间模式
Data|数据
Data Polling|数据轮询
Data polling disabled|数据轮询已禁用
Dec: |抽取：
Decimation (skip samples to fit more data)|抽取（跳过部分采样以容纳更多数据）
Decrease indentation (CTRL+,)|减少缩进 (CTRL+,)
Default Value|默认值
Delay Comp|延迟补偿
Delete|删除
Delete All Data|删除所有数据
Description|描述
Detect BLDC Parameters|检测 BLDC 参数
Detect Encoder|检测编码器
Detect FOC Parameters on all VESCs|检测所有 VESC 的 FOC 参数
Detect Hall Sensors|检测霍尔传感器
Detect and Calculate Parameters|检测并计算参数
Detected Devices|已检测到的设备
Developer|开发者
Direct Drive|直驱
Directions|方向
Disconnect|断开连接
Discover VESC nodes in the CAN bus|发现 CAN 总线上的 VESC 节点
Discovered VESC nodes in the bus|总线上已发现的 VESC 节点
Display|显示
Dither when loading|加载时抖动
Double|双精度
Download Archive|下载归档
Download Latest|下载最新版
Draw Font|绘制字体
Draw Overlay|绘制叠加层
Draw border around characters to see their bounding box|在字符周围绘制边框以查看其边界框
Drop old samples when the plot grows larger than this|图表超过此大小时丢弃旧采样
Duty Control|占空比控制
Duty Sweep|占空比扫描
Duty cycle|占空比
Duty cycle to measure BEMF coupling at|测量反电动势耦合时使用的占空比
Duty cycle to sample at|采样时使用的占空比
ERPM Sweep|ERPM 扫描
EXT Monitor|外部监视
Edit|编辑
Edit as Percentage|以百分比编辑
Editor Decimals|编辑器小数位数
Editor Scale|编辑器缩放
Editor Step|编辑器步进
Emergency Stop Time|急停时间
Enable Horizontal Zoom|启用水平缩放
Enable TCP Server|启用 TCP 服务器
Enable UDP Server|启用 UDP 服务器
Enable Vertical Zoom|启用垂直缩放
Enable horizontal zoom|启用水平缩放
Enable vertical zoom|启用垂直缩放
Encoder|编码器
Encoder offset|编码器偏移
Encoder ratio|编码器比率
End RPM|结束 RPM
End: |结束：
Enum|枚举
Erase|擦除
Erase &amp;&amp; Upload|擦除并上传
Erase LispBM|擦除 LispBM
Erase Only|仅擦除
Erase QML|擦除 QML
Examples|示例
Exit|退出
Exp|指数
Experiment Plot|实验图表
Export|导出
Export Array App|导出应用数组
Export Array HW|导出硬件数组
Export Bin|导出 Bin
Export C Array|导出 C 数组
Export Compressed C Array|导出压缩 C 数组
Export Configuration Parser|导出配置解析器
Export Font|导出字体
Export Height|导出高度
Export Scale|导出缩放
Export Width|导出宽度
Export only numbers to save space|仅导出数字以节省空间
Ext|扩展
Extended|扩展帧
FFT Plot|FFT 图
FIR Filter|FIR 滤波器
FIR filter stop frequency|FIR 滤波器截止频率
FIR filter taps|FIR 滤波器阶数
FW: |固件：
False|假
Fast Start|快速启动
Field Weakening|弱磁
Field Weakening Current|弱磁电流
File|文件
Filesystem|文件系统
Filter|过滤
Filter Data|过滤数据
Filter Outliers|过滤异常值
Filter Plot|滤波图
Filters|滤波器
Find in text|在文本中查找
Find:|查找：
Finish|完成
Firmware|固件
Firmware Changelog|固件更新日志
Firmware Upload|固件上传
Firmware Version|固件版本
Flash|烧录
Flash using Bootloader|通过引导程序烧录
Flash using USB|通过 USB 烧录
Follow|跟随
Follow log position on map|在地图上跟随日志位置
Font|字体
Font Editor|字体编辑器
Font size|字号
Format|格式
Forward communication over CAN-bus|通过 CAN 总线转发通信
From: |从：
Full brake|全刹车
Fullscreen|全屏
Gamepad|游戏手柄
Gamepad Control|游戏手柄控制
Gear Eff: |齿轮效率：
Gear Ratio|齿轮比
Gearing: |传动比：
General|通用
Generic|通用
Get gearing from config|从配置获取传动比
Go up one directory|返回上一级目录
Graph Title|图表标题
Grid|网格
Grouping|分组
Gyro|陀螺仪
HB |手刹
Hall Sensors|霍尔传感器
Hamming|汉明窗
Handbrake current|手刹电流
Hardware Version|硬件版本
Heap|堆
Heavy Inertial Load|大惯量负载
Help|帮助
History: |历史：
Humidity|湿度
IB |制动电流
IMU Data Poll Rate|IMU 数据轮询频率
Ignore|忽略
Image|图像
Image rotation in degrees|图像旋转角度（度）
Image scale|图像缩放
Img Center|图像中心
Import|导入
Import Bin|导入 Bin
Import Font|导入字体
Include negative RPM and Torque in tests.|测试中包含负转速和负扭矩。
Included|内置
Included Files|内置文件
Included Firmwares|内置固件
Increase indentation (CTRL+.)|增加缩进 (CTRL+.)
Indexed 16|索引 16
Indexed 2|索引 2
Indexed 4|索引 4
Inductance|电感
Info|信息
Input Current|输入电流
Input Current BMS IC|BMS IC 输入电流
Input Setup Wizard|输入设置向导
Insert image...|插入图片...
Install|安装
Install New Firmware|安装新固件
Int|整数
Interface|接口
Interpretation|解释方式
Invert Motor Directions|反转电机方向
Inverted|反向
Italic (CTRL+I)|斜体 (CTRL+I)
KBits/sec|Kbit/s
Keep End Speed|保持结束速度
Len|长度
Libraries|库
License|许可证
Limited Warranty Statement|有限保修声明
Link (CTRL+L)|链接 (CTRL+L)
LispBM Editor|LispBM 编辑器
Lithium Ion (full at 4.2V/cell)|锂离子（单体满电 4.2V）
Live Update|实时更新
Load App Configuration XML|加载应用配置 XML
Load Color Scale: |加载颜色缩放：
Load Custom|加载自定义
Load Firmware Configs|加载固件配置
Load Hardware Qml UI on Connect|连接时加载硬件 QML 界面
Load Image|加载图像
Load Motor Configuration XML|加载电机配置 XML
Load Package|加载软件包
Load XML|加载 XML
Load samples from CSV-file|从 CSV 文件加载采样
Load selected motor configuration in VESC Tool|在 VESC Tool 中加载所选电机配置
Load/Save|加载/保存
Local|本地
Local Logs|本地日志
Login Details|登录信息
Logs created from LispBM and sent to local VESC Tool.|由 LispBM 创建并发送到本地 VESC Tool 的日志。
Logscale|对数刻度
Long Name|长名称
MC total|电机总计
Manual|手动
Mapping|映射
Match case sensitive|区分大小写
Max|最大
Max Length|最大长度
Max Power Loss: |最大功率损耗：
Max RPM: |最大 RPM：
Max: |最大：
Maximum Value|最大值
Maximum distance from origin|距原点的最大距离
Maximum motor shaft RPM|电机轴最大转速
Mean Filter|均值滤波
Measure Offsets|测量偏移
Measure flux linkage|测量磁链
Measure resistance and inductance|测量电阻和电感
Measured maximum pulselength|测得的最大脉宽
Measured maximum voltage|测得的最大电压
Measured minimum pulselength|测得的最小脉宽
Measured minimum voltage|测得的最小电压
Mem|内存
Menu|菜单
Min|最小
Min ERPM setting for delay commutation mode to use|延迟换相模式使用的最小 ERPM 设置
Min: |最小：
Minimum Value|最小值
Misc|杂项
Mode:|模式：
Motor|电机
Motor A|电机 A
Motor B|电机 B
Motor Config XML: |电机配置 XML：
Motor Configuration|电机配置
Motor Detection|电机检测
Motor Direction Calibration|电机方向校准
Motor General|电机通用
Motor Openloop Load Test|电机开环负载测试
Motor Parameter Tolerance:|电机参数容差：
Motor Pulley: |电机皮带轮：
Motor Setup Wizard|电机设置向导
Motor Target Settings|电机目标设置
Motor flux linkage|电机磁链
Motor inductance|电机电感
Motor resistance|电机电阻
Motors: |电机数：
Move down|下移
Move up|上移
Multi Settings|多项设置
My Application|我的应用
NRF Pairing|NRF 配对
NRF Quick Pair|NRF 快速配对
Name|名称
Negative|负向
Next|下一步
No Filter|无滤波
No log opened|未打开日志
Not Inverted|未反向
NumOnly|仅数字
Number of motors in parallel|并联电机数量
Numbers Only|仅数字
Obs vs Enc|观测器与编码器
Obs vs Hall|观测器与霍尔
Observer|观测器
Observer gain|观测器增益
Offset|偏移
Offset: |偏移：
Offsets|偏移量
Open|打开
Open CSV file...|打开 CSV 文件...
Open Qmlui App|打开 QML 应用界面
Open Qmlui HW|打开 QML 硬件界面
Open Selected|打开所选
Open current|打开当前
Open file...|打开文件...
Open in editor|在编辑器中打开
Open log from RT data page|从实时数据页打开日志
Open loop current to turn the motor with|用于转动电机的开环电流
Open selected recent file|打开所选的最近文件
Openloop ERPM: |开环 ERPM：
Openloop Presets|开环预设
Ordered list (CTRL+=)|有序列表 (CTRL+=)
Output|输出
Overlay|叠加层
Overlay Editor|叠加层编辑器
PID Error|PID 误差
PID Pos|PID 位置
PPM Pulselength Mapping|PPM 脉宽映射
Package Name|软件包名称
Package Store|软件包商店
Pair|配对
Pair the connected VESC|配对已连接的 VESC
Paragraph formatting|段落格式
Parameter|参数
Parameter Editor Appconf|参数编辑器（应用配置）
Parameter Editor Custom Conf 0|参数编辑器（自定义配置 0）
Parameter Editor FW|参数编辑器（固件）
Parameter Editor Info|参数编辑器（信息）
Parameter Editor Mcconf|参数编辑器（电机配置）
Partition Table|分区表
Password|密码
Paste (CTRL+V)|粘贴 (CTRL+V)
Paths|路径
Phase|相位
Plain text|纯文本
Play log in real time|实时回放日志
Plot|图表
Plot Line Width|图表线宽
Plot Points: |绘图点数：
Plot Scale|图表缩放
Plot the PID controller position|绘制 PID 控制器位置
Plot the PID controller position error|绘制 PID 控制器位置误差
Plot the encoder position|绘制编码器位置
Plot the rotor position seen by the observer (FOC only)|绘制观测器得到的转子位置（仅 FOC）
Poll All|全部轮询
Poll GNSS|轮询 GNSS
Poll Off|关闭轮询
Poll Rate|轮询频率
Poll VT|轮询 VT
Poll all variables|轮询所有变量
Poll realtime GNSS-data from the connected device.|从已连接设备轮询实时 GNSS 数据。
Poll variables starting with vt only|仅轮询以 vt 开头的变量
Port|端口
Port: |端口：
Pos Now: |当前位置：
Position|位置
Position Control|位置控制
Position Offset Calculator|位置偏移计算器
Position to draw image|绘制图像的位置
Power|功率
Preferences|偏好设置
Pressure|气压
Preview|预览
Preview Scale: |预览缩放：
Previous|上一步
Print Faults|打印故障
Print Threads|打印线程
Print available commands|打印可用命令
Propeller|螺旋桨
Properties|属性
QML Upload|QML 上传
Quality|质量
Quick Configuration|快速配置
REPL Max Line Count|REPL 最大行数
RPM exponent|RPM 指数
RPM/Power|RPM/功率
RT Data Log|实时数据日志
RT Data Poll Rate|实时数据轮询频率
Ratio: |比率：
Raw|原始
Re-run tests any time settings are changed.|设置更改时自动重新运行测试。
Read|读取
Read All|全部读取
Read Default|读取默认值
Read LispBM code from connected VESC|从已连接的 VESC 读取 LispBM 代码
Read app configuration|读取应用配置
Read current setting|读取当前设置
Read default app configuration|读取默认应用配置
Read default motor configuration|读取默认电机配置
Read default setting|读取默认设置
Read firmware version|读取固件版本
Read last samples|读取最近的采样
Read motor Configuration|读取电机配置
Realtime|实时
Reboot|重启
Reboot via CPU reset|通过 CPU 复位重启
Recent|最近
Reconnect Last CAN UUID|重连上次的 CAN UUID
Reconnect last connection|重新连接上次的连接
Redo|重做
Reduce Code on Upload|上传时精简代码
Refresh|刷新
Refresh serial port list|刷新串口列表
Regular expression|正则表达式
Reload|重新加载
Reload &amp;&amp; Run|重新加载并运行
Remove|移除
Remove Downloaded Configs|移除已下载的配置
Remove Setup|移除配置
Replace|替换
Replace All|全部替换
Replace all|全部替换
Replace all text occurrences|替换所有匹配文本
Replace one text occurrence|替换一处匹配文本
Replace with|替换为
Replace:|替换：
Rescale plots to fit|重新缩放图表以适应
Reset|复位
Reset Ah|重置 Ah
Reset Configuration|重置配置
Reset Wh|重置 Wh
Reset editor|重置编辑器
Reset min and max|重置最小值和最大值
Restart + Launch Board Configurator|重启并启动主板配置器
Restart + Launch Mobile Tool|重启并启动移动端工具
Restart LispBM|重启 LispBM
Restore Configuration|恢复配置
Restore Configurations (Including CAN)|恢复配置（含 CAN）
Restore Defaults|恢复默认值
Restore default|恢复默认
Roll/Pitch/Yaw|横滚/俯仰/偏航
Rot Center|旋转中心
Rotation|旋转
Rotation will be done around this pixel on the image|将围绕图像上的此像素进行旋转
Rotor Position|转子位置
Run|运行
Run Detection (no CAN)|运行检测（不含 CAN）
Run in Window|在窗口中运行
Run in panel.|在面板中运行。
Run or re-run evaluator|运行或重新运行求值器
Run uploaded UI in fullscreen mode.|以全屏模式运行已上传的界面。
Safety Information|安全信息
Samp: |采样：
Sample Interval: |采样间隔：
Sample now|立即采样
Sample when the motor starts|电机启动时采样
Sampling frequency to calculate FFT time axis at|计算 FFT 时间轴所用的采样频率
Save App Configuration C Header (ifdef wrapped) as...|另存应用配置 C 头文件（含 ifdef）为...
Save App Configuration C Header as...|另存应用配置 C 头文件为...
Save App Configuration XML as...|另存应用配置 XML 为...
Save Configuration C Header (ifdef wrapped) as|另存配置 C 头文件（含 ifdef）为
Save Configuration C Header (ifdef wrapped) as...|另存配置 C 头文件（含 ifdef）为...
Save Configuration C Header as...|另存配置 C 头文件为...
Save Motor Configuration C Header (ifdef wrapped) as...|另存电机配置 C 头文件（含 ifdef）为...
Save Motor Configuration C Header as...|另存电机配置 C 头文件为...
Save Motor Configuration XML as...|另存电机配置 XML 为...
Save PNG|保存 PNG
Save Package|保存软件包
Save XML|保存 XML
Save XML and export config, parser and compressed C array|保存 XML 并导出配置、解析器和压缩 C 数组
Save XML as...|另存 XML 为...
Save all data as CSV-file...|将所有数据保存为 CSV 文件...
Save as...|另存为...
Save file|保存文件
Save file as...|文件另存为...
Save image, as seen above, to PNG file.|将上方图像保存为 PNG 文件。
Save map as PDF image|将地图保存为 PDF 图像
Save map as Png image|将地图保存为 PNG 图像
Save plot as PDF image|将图表保存为 PDF 图像
Save plot as PNG image|将图表保存为 PNG 图像
Save samples to CSV file...|将采样保存到 CSV 文件...
Save to Layer 2|保存到第 2 层
Scale|缩放
Scale: |缩放：
Scan|扫描
Scan CAN|扫描 CAN
Scan for CAN devices|扫描 CAN 设备
ScatterPlot|散点图
Scatterplot|散点图
Script Input Files|脚本输入文件
Script Output Files|脚本输出文件
Scripting|脚本
Search backward|向后搜索
Search forward|向前搜索
Select what to plot|选择要绘制的内容
Send|发送
Send Alive Commands|发送保活命令
Send Frame|发送帧
Send alive packets periodically to prevent timeout|定期发送保活包以防止超时
Send command|发送命令
Send help command to VESC|向 VESC 发送 help 命令
Sensorless|无感
Sensorless ERPM: |无感 ERPM：
Sensors|传感器
Serial port|串口
Series|数据系列
Server|服务器
Servo Output|舵机输出
Set|设置
Set Device Name|设置设备名称
Settings|设置
Setup|设置
Setup Bluetooth Module|设置蓝牙模块
Setup IMU|设置 IMU
Setup Input|设置输入
Setup Motors FOC|设置电机 FOC
Setup Motors FOC (old)|设置电机 FOC（旧版）
Setup Other Motors|设置其他电机
Show Display|显示屏幕
Show FOC motor phase|显示 FOC 电机相位
Show Help|显示帮助
Show Instructions|显示指令
Show Layer 2|显示第 2 层
Show Legend|显示图例
Show MOSFET temperature|显示 MOSFET 温度
Show duty cycle|显示占空比
Show firmware changelog|显示固件更新日志
Show firmware update message|显示固件更新提示
Show firmwares with non-default compilation options|显示使用非默认编译选项的固件
Show help|显示帮助
Show individual MOSFET temperatures|显示各 MOSFET 温度
Show input current|显示输入电流
Show input voltage|显示输入电压
Show motor current|显示电机电流
Show motor temperature|显示电机温度
Show non-default firmwares|显示非默认固件
Show power|显示功率
Show this graph|显示此图表
Shutdown|关机
Shutdown (for controllers with auto-shutdown support only)|关机（仅适用于支持自动关机的控制器）
Simple|简易
Simple FOC setup for all VESCs on CAN-bus|CAN 总线上所有 VESC 的简易 FOC 设置
Size|大小
Size of cropped area|裁剪区域大小
Source|来源
Speed|速度
Speed Control|速度控制
Start Board Setup|开始主板设置
Start Pairing|开始配对
Start RPM|起始 RPM
Start Update|开始更新
Start detection|开始检测
Start inductance based signal injection detection (BLDC only)|开始基于电感的信号注入检测（仅 BLDC）
Start the App Setup Wizard|启动应用设置向导
Start the Motor Setup Wizard|启动电机设置向导
Stat|状态
State of Charge (SoC)|荷电状态 (SoC)
State of Health (SoH)|健康状态 (SoH)
Stats|统计
Status|状态
Stay in pairing mode for this amount of time|保持配对模式的时长
Step: |步进：
Stop|停止
Stop evaluator|停止求值器
Stop sampling|停止采样
Stop sending position samples|停止发送位置采样
Stream|流式传输
Stream BMS realtime data|流式传输 BMS 实时数据
Stream Mode|流式传输模式
Stream realtime app data|流式传输应用实时数据
Stream realtime data|流式传输实时数据
String|字符串
Suffix|后缀
Supported Firmwares Loaded|已加载支持的固件
Sweep from 0 to the end RPM at the set torque.|在设定扭矩下，从 0 扫描到结束 RPM。
Sweep from 0 to the set torque at the set RPM.|在设定 RPM 下，从 0 扫描到设定扭矩。
Sweep from the start RPM to the end RPM at the set Power.|在设定功率下，从起始 RPM 扫描到结束 RPM。
Switch off|关闭
TCP Client|TCP 客户端
TCP Hub|TCP 集线器
TCP Port: |TCP 端口：
TCP Server|TCP 服务器
TS: |时间步：
TX  Scale|发送缩放
TX Type|发送类型
Target:|目标：
Temp Cell Max|电芯最高温度
Temp Increase: |温升：
Temp PCB Max|PCB 最高温度
Temp Plot|温度图
Temperature|温度
Temperatures|温度
Terminal|终端
Text background color|文本背景色
Text color|文本颜色
This file has been changed on the filesystem.|此文件已在文件系统中被修改。
Throttle Curve|油门曲线
Time Plot|时间图
Time constant for calculating KP and KI|计算 KP 和 KI 所用的时间常数
Time to disable all motor commands after using the stop button or the ESC key.|使用停止按钮或 ESC 键后禁用所有电机命令的时长。
Time: |时间：
To: |到：
Toggle fullscreen in running window.|切换运行窗口的全屏。
Tools|工具
Torque|扭矩
Torque sweep while keeping the bus voltage constant.|保持母线电压恒定的扭矩扫描。
Total Voltage|总电压
Transmittable|可传输
Transparent|透明
Triggered sampling at fault codes|故障码触发采样
Triggered sampling at fault codes without sending the samples automatically|故障码触发采样，不自动发送采样数据
Triggered sampling when the motor starts|电机启动时触发采样
True|真
Truncate|截断
Truncate conducting phases|截断导通相
Try to automatically connect using the USB connection|尝试通过 USB 连接自动连接
Type|类型
UDP Client|UDP 客户端
UDP Port: |UDP 端口：
UDP Server|UDP 服务器
UI Scale Factor (restart required)|界面缩放系数（需重启）
USB Target:|USB 目标：
Undefined|未定义
Underline (CTRL+U)|下划线 (CTRL+U)
Undo (CTRL+Z)|撤销 (CTRL+Z)
Uninstall Current|卸载当前
Unpair|取消配对
Unused|未使用
Up|上
Update|更新
Update Archive|更新归档
Update CAN Baudrate|更新 CAN 波特率
Update RT|更新实时数据
Update firmware on the connected VESC|更新已连接 VESC 的固件
Update plots while receiving data|接收数据时更新图表
Upload|上传
Upload Bootloader|上传引导程序
Upload bootloader before uploading firmware|上传固件前先上传引导程序
Upload code to flash. This is persistent and starts the code on every boot.|将代码上传到 Flash。此方式持久保存，并在每次启动时运行。
Upload/Stream/Run|上传/流式传输/运行
Use|使用
Use Axis 1|使用轴 1
Use Axis 2|使用轴 2
Use Axis 3|使用轴 3
Use Axis 4|使用轴 4
Use Centered Control|使用中心控制
Use Editor Content|使用编辑器内容
Use File Content|使用文件内容
Use Gamepad Control|使用游戏手柄控制
Use Hamming window|使用汉明窗
Use Imperial Units|使用英制单位
Use Scatterplot|使用散点图
Use Yaw (will drift)|使用偏航角（会漂移）
Use editor content when uploading/streaming/running code.|上传/流式传输/运行代码时使用编辑器内容。
Use mcconf from connected VESC|使用已连接 VESC 的电机配置
Use raw ADC values instead of scaled voltages and currents.|使用原始 ADC 值，而非换算后的电压和电流。
VESC Devices|VESC 设备
VESC Discord|VESC Discord 社区
VESC Firmware|VESC 固件
VESC Firmware, Hardware and UUID|VESC 固件、硬件和 UUID
VESC Parameter Editor|VESC 参数编辑器
VESC Project Forums|VESC 项目论坛
VESC Tool Changelog|VESC Tool 更新日志
VESC Tool preview with the current settings.|使用当前设置的 VESC Tool 预览。
Value|值
Value: |值：
Verify flash while programming|编程时校验 Flash
Virtual Ground|虚拟地
Voltage|电压
Voltage:|电压：
Voltages|电压
Wattage|功率
Wh Charge Total|累计充电 Wh
Wh Counter|Wh 计数
Wh Discharge Total|累计放电 Wh
Wheel Diameter|轮径
Wheel Pulley: |车轮皮带轮：
Whole words|全字匹配
Window|窗口
Wizards|向导
Worst horizontal accuracy for points|各点最差水平精度
Write|写入
Write All|全部写入
Write app configuration|写入应用配置
Write motor configuration|写入电机配置
Zoom in on trace|放大轨迹
Zoom in on trajectory when zooming in on data.|放大数据时同时放大轨迹。
does not update BLE FW if left empty|留空则不更新 BLE 固件
'''
T = dict(l.split('|', 1) for l in D.splitlines() if '|' in l)
for i in range(8):
    T['Hall table %d position (0 - 200, 255 = not used)' % i] = '霍尔表 %d 位置 (0 - 200，255 = 未使用)' % i

PROP = re.compile(r'(<(?:property|attribute) name=.(?:text|toolTip|title|windowTitle|suffix|prefix|placeholderText|statusTip|whatsThis|format).>[^<]*<string>)([^<]*)(</string>)')

files = [f for f in glob.glob('**/*.ui', recursive=True) if not f.startswith(('vesc_tool-master', 'build', 'application'))]
miss = {}
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
        if re.search('[A-Za-z]{2}', k):
            miss.setdefault(k, set()).add(f)
        return m.group(0)
    n = PROP.sub(rep, s)
    if n != s:
        open(f, 'w', encoding='utf-8', newline='').write(n)
        changed += 1

print('files changed:', changed, 'replacements:', replaced)
html = [k for k in miss if k.startswith('&lt;')]
rest = sorted(k for k in miss if not k.startswith('&lt;'))
print('untranslated html:', len(html), 'untranslated plain:', len(rest))
for k in rest:
    print(repr(k[:110]), '|', sorted(miss[k])[0])
