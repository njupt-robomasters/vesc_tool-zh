#include "enumtranslations.h"
#include <QHash>
#include <QStringList>

namespace {
const char *kTable = R"TBL(
CAN_BAUD_10K|CAN 10K 波特率
CAN_BAUD_20K|CAN 20K 波特率
CAN_BAUD_50K|CAN 50K 波特率
CAN_BAUD_75K|CAN 75K 波特率
CAN_BAUD_100K|CAN 100K 波特率
CAN_BAUD_125K|CAN 125K 波特率
CAN_BAUD_250K|CAN 250K 波特率
CAN_BAUD_500K|CAN 500K 波特率
CAN_BAUD_1M|CAN 1M 波特率
ALWAYS_OFF|常关
ALWAYS_ON|常开
TOGGLE_BUTTON_ONLY|仅按钮切换
OFF_AFTER_10S|10 秒后关闭
OFF_AFTER_1M|1 分钟后关闭
OFF_AFTER_5M|5 分钟后关闭
OFF_AFTER_10M|10 分钟后关闭
OFF_AFTER_30M|30 分钟后关闭
OFF_AFTER_1H|1 小时后关闭
OFF_AFTER_5H|5 小时后关闭
Comm Bridge|通信桥
UAVCAN and VESC|UAVCAN 与 VESC
Current Control|电流控制
Current No Reverse Brake|电流控制(无反转,带刹车)
Duty Cycle Control|占空比控制
RPM Control|转速控制
Motor Current|电机电流
Input Current|输入电流
Disabled|禁用
PPM Low|PPM 低电平
PPM High|PPM 高电平
ADC2 Low|ADC2 低电平
ADC2 High|ADC2 高电平
ADC3 Low|ADC3 低电平
ADC3 High|ADC3 高电平
SWDIO Low|SWDIO 低电平
SWDIO High|SWDIO 高电平
SWCLK Low|SWCLK 低电平
SWCLK High|SWCLK 高电平
No App|无应用
PPM and UART|PPM 与 UART
ADC and UART|ADC 与 UART
Custom User App|自定义用户应用
ADC and PAS|ADC 与 PAS
Off|关闭
OFF|关闭
Current|电流
Current No Reverse|电流(无反转)
Current No Reverse With Brake|电流(无反转,带刹车)
Duty Cycle|占空比
Duty Cycle No Reverse|占空比(无反转)
PID Speed Control|PID 速度控制
PID Speed Control No Reverse|PID 速度控制(无反转)
Current Hyst Reverse With Brake|电流(迟滞反转,带刹车)
Current Smart Reverse|电流(智能反转)
PID Position Control: 180°|PID 位置控制:180°
PID Position Control: 360°|PID 位置控制:360°
Regular|常规
No Fault|无故障
Exponential|指数
Natural|自然
Polynomial|多项式
Current Reverse Center|电流(中点反转)
Current Reverse Button|电流(按钮反转)
Current Reverse ADC2 Brake Button|电流(按钮反转,ADC2 刹车)
Current Reverse Button Brake Center|电流(按钮反转,中点刹车)
Current No Reverse Brake Center|电流(无反转,中点刹车)
Current No Reverse Brake Button|电流(无反转,按钮刹车)
Current No Reverse Brake ADC2|电流(无反转,ADC2 刹车)
Duty Cycle Reverse Center|占空比(中点反转)
Duty Cycle Reverse Button|占空比(按钮反转)
PID Speed|PID 速度
PID Speed Reverse Center|PID 速度(中点反转)
PID Speed Reverse Button|PID 速度(按钮反转)
Enable Cruise Control|启用巡航
Invert CC Button|反转巡航按钮
Invert Reverse Button|反转倒车按钮
Brake Priority|刹车优先
Current Bidirectional|双向电流
Cadence|踏频
Constant Torque|恒扭矩
Quadrature|正交
IMU_TYPE_OFF|关闭
IMU_TYPE_INTERNAL|内置 IMU
IMU_TYPE_EXTERNAL_MPU9X50|外置 MPU9X50
IMU_TYPE_EXTERNAL_ICM20948|外置 ICM20948
IMU_TYPE_EXTERNAL_BMI160|外置 BMI160
IMU_TYPE_EXTERNAL_LSM6DS3|外置 LSM6DS3
IMU_TYPE_EXTERNAL_LSM6DSV32X|外置 LSM6DSV32X
AHRS_MODE_MADGWICK|Madgwick 算法
AHRS_MODE_MAHONY|Mahony 算法
AHRS_MODE_MADGWICK_FUSION|Madgwick Fusion 算法
IMU_FILTER_LOW|低滤波
IMU_FILTER_MEDIUM|中滤波
IMU_FILTER_HIGH|高滤波
Nonsynchronous HISW|非同步(仅高侧开关)
Synchronous|同步
Bipolar|双极
Integrate|积分
Delay|延时
Sensorless|无感
Sensored|有感
Hybrid|混合
Encoder Slip|编码器打滑
Overspeed|超速
Underspeed|欠速
Absolute Overspeed|绝对超速
Encoder|编码器
Hall Sensors|霍尔传感器
45 Deg V0V7 HFI (Silent)|45° V0V7 HFI(静音)
45 Deg V0 HFI|45° V0 HFI
Coupled V0V7 HFI (Silent)|耦合 V0V7 HFI(静音)
Coupled V0 HFI|耦合 V0 HFI
AB Encoder (No Index Pulse)|AB 编码器(无索引脉冲)
V0 Only|仅 V0
V0 and V7|V0 与 V7
V0 and V7 Interpolation|V0 与 V7 插值
Longest Zero Time|最长零时间
All Sensors Combined|所有传感器组合
High Current|大电流
Factor|系数
Lambda and Factor|Lambda 与系数
FOC_CC_DECOUPLING_DISABLED|电流环解耦:禁用
FOC_CC_DECOUPLING_CROSS|电流环解耦:交叉
FOC_CC_DECOUPLING_BEMF|电流环解耦:反电动势
FOC_CC_DECOUPLING_CROSS_BEMF|电流环解耦:交叉+反电动势
FOC_OBSERVER_ORTEGA_ORIGINAL|Ortega 原版观测器
FOC_OBSERVER_MXLEMMING|MXLemming 观测器
FOC_OBSERVER_ORTEGA_LAMBDA_COMP|Ortega 观测器(Lambda 补偿)
FOC_OBSERVER_MXLEMMING_LAMBDA_COMP|MXLemming 观测器(Lambda 补偿)
FOC_OBSERVER_MXV|MXV 观测器
FOC_OBSERVER_MXV_LAMBDA_COMP|MXV 观测器(Lambda 补偿)
FOC_OBSERVER_MXV_LAMBDA_COMP_LIN|MXV 观测器(Lambda 线性补偿)
Six Vectors|六矢量
Id Single Pulse|Id 单脉冲
Id Double Pulse|Id 双脉冲
Calibrate on Boot|启动时校准
Write Enabled|允许写入
Auto Calibrate|自动校准
IQ Target|Iq 目标值
IQ Measured|Iq 实测值
Corrected Position|校正位置
Observer|观测器
Fast Estimator|快速估算器
Faster Estimator|更快估算器
ABI Encoder|ABI 编码器
AS5047 Encoder|AS5047 编码器
AD2S1205 Resolver|AD2S1205 旋变
Sin/Cos Encoder|正余弦编码器
Custom Encoder|自定义编码器
Current Limit|电流限制
OC Latch Shutdown|过流锁存关断
Report Only|仅报告
On after 2 seconds|2 秒后开启
On after 5 seconds|5 秒后开启
On after 10 seconds|10 秒后开启
On when running|运行时开启
On when not running|未运行时开启
Temp motor > 50 C|电机温度 > 50 °C
Temp mosfet > 50 C|MOSFET 温度 > 50 °C
Temp motor > 70 C|电机温度 > 70 °C
Temp mosfet > 70 C|MOSFET 温度 > 70 °C
Temp motor or mosfet > 50 C|电机或 MOSFET 温度 > 50 °C
Temp motor or mosfet > 70 C|电机或 MOSFET 温度 > 70 °C
NTC Custom|自定义 NTC
PTC Custom|自定义 PTC
BATTERY_TYPE_LIION_3_0__4_2|锂离子电池(3.0-4.2V)
BATTERY_TYPE_LIIRON_2_6__3_6|磷酸铁锂电池(2.6-3.6V)
BATTERY_TYPE_LEAD_ACID|铅酸电池
No sensor|无传感器
Other Sensor|其他传感器
None|无
Overtemp|过温
SOC|电量 SOC
VCell Min|最低单体电压
VCell Max|最高单体电压
USB Only|仅 USB
Any Interface|任意接口
)TBL";

const QHash<QString, QString> &table()
{
    static QHash<QString, QString> t;
    if (t.isEmpty()) {
        const QStringList lines = QString::fromUtf8(kTable).split('\n', QString::SkipEmptyParts);
        for (const QString &l : lines) {
            int i = l.indexOf('|');
            if (i > 0) {
                t.insert(l.left(i).trimmed(), l.mid(i + 1).trimmed());
            }
        }
    }
    return t;
}
}

QString EnumTranslations::display(const QString &name)
{
    auto it = table().constFind(name);
    if (it == table().constEnd()) {
        return name;
    }
    return name + " (" + it.value() + ")";
}
