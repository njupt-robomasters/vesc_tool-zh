/*
    Copyright 2016 - 2017 Benjamin Vedder	benjamin@vedder.se

    This file is part of VESC Tool.

    VESC Tool is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    VESC Tool is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    */

#include "setupwizardmotor.h"
#include <QVBoxLayout>
#include <QMessageBox>
#include "utility.h"

SetupWizardMotor::SetupWizardMotor(VescInterface *vesc, QWidget *parent)
    : QWizard(parent)
{
    setPage(Page_Intro, new IntroPage(vesc));
    setPage(Page_Connection, new ConnectionPage(vesc));
    setPage(Page_Firmware, new FirmwarePage(vesc));
    setPage(Page_MotorType, new MotorTypePage(vesc));
    setPage(Page_Currents, new CurrentsPage(vesc));
    setPage(Page_Voltages, new VoltagesPage(vesc));
    setPage(Page_Sensors, new SensorsPage(vesc));
    setPage(Page_Bldc, new BldcPage(vesc));
    setPage(Page_Foc, new FocPage(vesc));
    setPage(Page_FocEncoder, new FocEncoderPage(vesc));
    setPage(Page_FocHall, new FocHallPage(vesc));
    setPage(Page_Conclusion, new ConclusionPage(vesc));

    setStartId(Page_Intro);
    setWizardStyle(ModernStyle);
    QPixmap icon_logo = QIcon(":/res/icon.svg").pixmap(QSize(this->devicePixelRatioF() * 48, this->devicePixelRatioF() * 48));
    icon_logo.setDevicePixelRatio(this->devicePixelRatioF());
    setPixmap(QWizard::LogoPixmap, icon_logo);
    resize(800, 450);

    setWindowTitle(tr("电机设置向导"));

    mSideLabel = new AspectImgLabel(Qt::Vertical);
    mSideLabel->setPixmap(QPixmap("://res/logo_vertical.png"));
    mSideLabel->setScaledContents(true);
    setSideWidget(mSideLabel);

    connect(this, SIGNAL(currentIdChanged(int)),
            this, SLOT(idChanged(int)));
}

void SetupWizardMotor::idChanged(int id)
{
    if (id == Page_Intro || id == Page_Conclusion) {
        setSideWidget(mSideLabel);
        mSideLabel->setVisible(true);
    } else {
        setSideWidget(0);
    }
}

IntroPage::IntroPage(VescInterface *vesc, QWidget *parent)
    : QWizardPage(parent)
{
    mVesc = vesc;
    setTitle(tr("VESC® 电机设置向导"));

    mLabel = new QLabel(tr("此向导将逐步引导您完成 VESC® 的电机设置。请注意，仅显示使电机运行所需的选项。要调整高级设置，需要在完成此向导后进入配置页面。<br><br>要获取向导中参数和工具的更多信息，请点击旁边的问号。<br><br>完成电机设置后，您可以使用输入设置向导来配置 VESC 的应用程序输入。"));
    mLabel->setWordWrap(true);

    QVBoxLayout *layout = new QVBoxLayout;
    layout->addWidget(mLabel);
    setLayout(layout);
}

int IntroPage::nextId() const
{
    if (mVesc->isPortConnected()) {
        if (mVesc->commands()->isLimitedMode()) {
            return SetupWizardMotor::Page_Firmware;
        } else {
            return SetupWizardMotor::Page_MotorType;
        }
    } else {
        return SetupWizardMotor::Page_Connection;
    }
}

bool IntroPage::validatePage()
{
    bool res = false;

    if (!mVesc->isPortConnected()) {
        QMessageBox::StandardButton reply;
        reply = QMessageBox::information(this,
                                         tr("连接"),
                                         tr("您未连接到 VESC。是否尝试自动连接？<br><br><i>请注意，USB 线必须插入且 VESC 必须通电才能建立连接。</i>"),
                                         QMessageBox::Yes | QMessageBox::No, QMessageBox::Yes);

        if (reply == QMessageBox::Yes) {
            Utility::autoconnectBlockingWithProgress(mVesc, this);
            res = true;
        }
    }

    return !res;
}

ConnectionPage::ConnectionPage(VescInterface *vesc, QWidget *parent)
    : QWizardPage(parent)
{
    mVesc = vesc;

    setTitle(tr("连接 VESC"));
    setSubTitle(tr("VESC 必须连接才能使用此向导。请使用可用的接口之一进行连接。"));

    mPageConnection = new PageConnection;
    mPageConnection->setVesc(mVesc);

    connect(mVesc, SIGNAL(fwRxChanged(bool,bool)),
            this, SIGNAL(completeChanged()));

    QVBoxLayout *layout = new QVBoxLayout;
    layout->addWidget(mPageConnection);
    setLayout(layout);
}

int ConnectionPage::nextId() const
{
    if (mVesc->commands()->isLimitedMode()) {
        return SetupWizardMotor::Page_Firmware;
    } else {
        return SetupWizardMotor::Page_MotorType;
    }
}

bool ConnectionPage::isComplete() const
{
    return mVesc->fwRx();
}

FirmwarePage::FirmwarePage(VescInterface *vesc, QWidget *parent)
    : QWizardPage(parent)
{
    mVesc = vesc;

    setTitle(tr("更新固件"));
    setSubTitle(tr("您需要更新 VESC 上的固件才能与此版本的 VESC Tool 一起使用。"));

    mPageFirmware = new PageFirmware;
    mPageFirmware->setVesc(mVesc);

    connect(mVesc, SIGNAL(portConnectedChanged()),
            this, SIGNAL(completeChanged()));

    QVBoxLayout *layout = new QVBoxLayout;
    layout->addWidget(mPageFirmware);
    setLayout(layout);
}

int FirmwarePage::nextId() const
{
    // Going to a previous page here does not seem to work,
    // so this is done in the validatePage function.
    return SetupWizardMotor::Page_MotorType;
}

bool FirmwarePage::isComplete() const
{
    return !mVesc->isPortConnected();
}

bool FirmwarePage::validatePage()
{
    wizard()->back();
    return false;
}

void FirmwarePage::initializePage()
{
    mVesc->commands()->getFwVersion();
}

MotorTypePage::MotorTypePage(VescInterface *vesc, QWidget *parent)
    : QWizardPage(parent)
{
    mVesc = vesc;
    mLoadDefaultAsked = false;

    setTitle(tr("选择电机类型"));
    setSubTitle(tr("此选择将帮助向导显示相关的配置页面。"));

    mParamTab = new ParamTable;
    mParamTab->addParamRow(mVesc->mcConfig(), "motor_type");

    QVBoxLayout *layout = new QVBoxLayout;
    layout->addWidget(mParamTab);
    setLayout(layout);
}

int MotorTypePage::nextId() const
{
    return SetupWizardMotor::Page_Currents;
}

bool MotorTypePage::validatePage()
{
    mVesc->commands()->setMcconf();
    return true;
}

void MotorTypePage::showEvent(QShowEvent *event)
{
    if (!mLoadDefaultAsked) {
        mLoadDefaultAsked = true;

        QMessageBox::StandardButton reply;
        reply = QMessageBox::information(this,
                                         tr("加载默认配置"),
                                         tr("是否在继续设置之前从连接的 VESC 加载默认配置？"),
                                         QMessageBox::Yes | QMessageBox::No, QMessageBox::Yes);

        if (reply == QMessageBox::Yes) {
            mVesc->commands()->getMcconfDefault();
        }
    }

    QWidget::showEvent(event);
}

CurrentsPage::CurrentsPage(VescInterface *vesc, QWidget *parent)
    : QWizardPage(parent)
{
    mVesc = vesc;
    mWarningShown = false;

    setTitle(tr("设置电流限制"));
    setSubTitle(tr("设置正确的电流限制非常重要，既能确保参数检测的准确性，也能保证安全运行。"));

    mParamTab = new ParamTable;
    mParamTab->addRowSeparator(tr("电机"));
    mParamTab->addParamRow(mVesc->mcConfig(), "l_current_max");
    mParamTab->addParamRow(mVesc->mcConfig(), "l_current_min");
    mParamTab->addRowSeparator(tr("电池"));
    mParamTab->addParamRow(mVesc->mcConfig(), "l_in_current_max");
    mParamTab->addParamRow(mVesc->mcConfig(), "l_in_current_min");
    mConfigureBatteryCutoff = true;

    mLabel = new QLabel(tr("<font color=\"red\">警告：</font>使用过高的电流设置可能会损坏电机、VESC 和/或电池。如果不确定如何配置电流限制，请务必阅读系统规格说明。"));
    mLabel->setWordWrap(true);

    QVBoxLayout *layout = new QVBoxLayout;
    layout->addWidget(mParamTab);
    layout->addWidget(mLabel);
    setLayout(layout);
}

int CurrentsPage::nextId() const
{
    if (mConfigureBatteryCutoff) {
        return SetupWizardMotor::Page_Voltages;
    } else {
        return SetupWizardMotor::Page_Sensors;
    }
}

bool CurrentsPage::validatePage()
{
    mVesc->commands()->setMcconf();

    mConfigureBatteryCutoff = QMessageBox::information(this,
                                     tr("配置电池截止"),
                                     tr("是否配置软电池截止电压以防止电池过度放电？<br><br>如果您使用的是电源而非电池，可以跳过此步骤。"),
                                     QMessageBox::Yes | QMessageBox::No, QMessageBox::Yes)
            == QMessageBox::Yes;

    return true;
}

void CurrentsPage::showEvent(QShowEvent *event)
{
    if (!mWarningShown) {
        mWarningShown = true;

        QMessageBox::warning(this,
                             tr("重要提示"),
                             tr("您即将配置电流限制。请注意，使用过高的电流设置可能会损坏电机、VESC 和/或电池。如果不确定如何配置电流限制，请务必阅读系统规格说明。"));

    }

    QWidget::showEvent(event);
}

VoltagesPage::VoltagesPage(VescInterface *vesc, QWidget *parent)
    : QWizardPage(parent)
{
    mVesc = vesc;

    setTitle(tr("设置电压限制"));
    setSubTitle(tr("设置软电压限制以防止电池过度放电。"));

    mParamTab = new ParamTable;
    mParamTab->addParamRow(mVesc->mcConfig(), "l_battery_cut_start");
    mParamTab->addParamRow(mVesc->mcConfig(), "l_battery_cut_end");

    mCalc = new BatteryCalculator(this);
    mCalc->setVesc(vesc);

    QVBoxLayout *layout = new QVBoxLayout;
    layout->addWidget(mParamTab);
    layout->addWidget(mCalc);
    setLayout(layout);
}

int VoltagesPage::nextId() const
{
    return SetupWizardMotor::Page_Sensors;
}

bool VoltagesPage::validatePage()
{
    mVesc->commands()->setMcconf();
    return true;
}

SensorsPage::SensorsPage(VescInterface *vesc, QWidget *parent)
    : QWizardPage(parent)
{
    mVesc = vesc;

    setTitle(tr("选择传感器模式"));
    setSubTitle(tr("选择电机的传感器类型（如有）。"));

    mSensorMode = new QComboBox;
    mSensorMode->addItem("No Sensor (Sensorless)", SetupWizardMotor::Sensor_Sensorless);
    mParamTab = new ParamTable;
    mTypeBefore = -1;

    mParamTab->addParamRow(mVesc->mcConfig(), "m_encoder_counts");
    registerField("SensorMode", mSensorMode, "currentData");

    QVBoxLayout *layout = new QVBoxLayout;
    layout->addWidget(mSensorMode);
    layout->addWidget(mParamTab);
    setLayout(layout);

    connect(mSensorMode, SIGNAL(currentIndexChanged(int)),
            this, SLOT(indexChanged(int)));

    indexChanged(0);
}

int SensorsPage::nextId() const
{
    int retval = SetupWizardMotor::Page_Conclusion;

    switch (mVesc->mcConfig()->getParamEnum("motor_type")) {
    case 0: // BLDC
        retval = SetupWizardMotor::Page_Bldc;
        break;

    case 1: // DC
        retval = SetupWizardMotor::Page_Conclusion;
        break;

    case 2: // FOC
        retval = SetupWizardMotor::Page_Foc;
        break;

    default:
        break;
    }

    return retval;
}

bool SensorsPage::validatePage()
{
    switch (mSensorMode->currentData().toInt()) {
    case SetupWizardMotor::Sensor_Sensorless:
        mVesc->mcConfig()->updateParamEnum("m_sensor_port_mode", 0);
        mVesc->mcConfig()->updateParamEnum("sensor_mode", 0);
        mVesc->mcConfig()->updateParamEnum("foc_sensor_mode", 0);
        break;

    case SetupWizardMotor::Sensor_Hall:
        mVesc->mcConfig()->updateParamEnum("m_sensor_port_mode", 0);
        mVesc->mcConfig()->updateParamEnum("sensor_mode", 2);
        mVesc->mcConfig()->updateParamEnum("foc_sensor_mode", 2);
        break;

    case SetupWizardMotor::Sensor_EncoderAbi:
        mVesc->mcConfig()->updateParamEnum("m_sensor_port_mode", 1);
        mVesc->mcConfig()->updateParamEnum("sensor_mode", 0);
        mVesc->mcConfig()->updateParamEnum("foc_sensor_mode", 1);
        break;

    case SetupWizardMotor::Sensor_EncoderAs:
        mVesc->mcConfig()->updateParamEnum("m_sensor_port_mode", 2);
        mVesc->mcConfig()->updateParamEnum("sensor_mode", 0);
        mVesc->mcConfig()->updateParamEnum("foc_sensor_mode", 1);
        break;

    case SetupWizardMotor::Sensor_Resolver_AD2S1205:
        mVesc->mcConfig()->updateParamEnum("m_sensor_port_mode", 3);
        mVesc->mcConfig()->updateParamEnum("sensor_mode", 0);
        mVesc->mcConfig()->updateParamEnum("foc_sensor_mode", 1);
        break;

    case SetupWizardMotor::Sensor_Encoder_SinCos:
        mVesc->mcConfig()->updateParamEnum("m_sensor_port_mode", 4);
        mVesc->mcConfig()->updateParamEnum("sensor_mode", 0);
        mVesc->mcConfig()->updateParamEnum("foc_sensor_mode", 1);
        break;

    case SetupWizardMotor::Sensor_EncoderAs5x47u:
        mVesc->mcConfig()->updateParamEnum("m_sensor_port_mode", 8);
        mVesc->mcConfig()->updateParamEnum("sensor_mode", 0);
        mVesc->mcConfig()->updateParamEnum("foc_sensor_mode", 1);
        break;

    default:
        break;
    }

    mVesc->commands()->setMcconf();
    return true;
}

void SensorsPage::initializePage()
{
    int typeNow = mVesc->mcConfig()->getParamEnum("motor_type");

    if (mTypeBefore != typeNow) {
        while (mSensorMode->count() > 1) {
            mSensorMode->removeItem(1);
        }

        switch (typeNow) {
        case 0: // BLDC
            mSensorMode->addItem("Hall Sensors", SetupWizardMotor::Sensor_Hall);
            break;

        case 1: // DC
            mSensorMode->addItem("ABI Encoder", SetupWizardMotor::Sensor_EncoderAbi);
            mSensorMode->addItem("AS5047 Encoder", SetupWizardMotor::Sensor_EncoderAs);
            mSensorMode->addItem("AS5X47U Encoder", SetupWizardMotor::Sensor_EncoderAs5x47u);
            break;

        case 2: // FOC
            mSensorMode->addItem("Hall Sensors", SetupWizardMotor::Sensor_Hall);
            mSensorMode->addItem("ABI Encoder", SetupWizardMotor::Sensor_EncoderAbi);
            mSensorMode->addItem("AS5047 Encoder", SetupWizardMotor::Sensor_EncoderAs);
            mSensorMode->addItem("AS5X47U Encoder", SetupWizardMotor::Sensor_EncoderAs5x47u);
            mSensorMode->addItem("Resolver", SetupWizardMotor::Sensor_Resolver_AD2S1205);
            mSensorMode->addItem("Sin/Cos Encoder", SetupWizardMotor::Sensor_Encoder_SinCos);
            mSensorMode->addItem("BiSS Encoder", SetupWizardMotor::Sensor_EncoderBiSS);
            break;

        default:
            break;
        }
    }

    mTypeBefore = typeNow;
}

void SensorsPage::cleanupPage()
{
    // Do nothing here, but override so that fields are not reset.
}

void SensorsPage::indexChanged(int ind)
{
    (void)ind;
    if (mSensorMode->currentData() == SetupWizardMotor::Sensor_EncoderAbi) {
        mParamTab->setVisible(true);
    } else {
        mParamTab->setVisible(false);
    }
}

BldcPage::BldcPage(VescInterface *vesc, QWidget *parent)
    : QWizardPage(parent)
{
    mVesc = vesc;

    setTitle(tr("BLDC 设置"));
    setSubTitle(tr("运行检测并获取 BLDC 换向所需的参数。"));

    mParamTab = new ParamTable;
    mDetect = new DetectBldc(this);
    mDetect->setVesc(vesc);

    QVBoxLayout *layout = new QVBoxLayout;
    layout->addWidget(mParamTab);
    layout->addWidget(mDetect);
    layout->setStretch(0, 1);
    setLayout(layout);
}

int BldcPage::nextId() const
{
    return SetupWizardMotor::Page_Conclusion;
}

bool BldcPage::validatePage()
{
    mVesc->commands()->setMcconf();
    return true;
}

void BldcPage::initializePage()
{
    mParamTab->setRowCount(0);
    mParamTab->addParamRow(mVesc->mcConfig(), "sl_cycle_int_limit");
    mParamTab->addParamRow(mVesc->mcConfig(), "sl_bemf_coupling_k");
    mParamTab->addRowSeparator(tr("霍尔传感器设置"));

    if (field("SensorMode").toInt() == SetupWizardMotor::Sensor_Hall) {
        mParamTab->addParamRow(mVesc->mcConfig(), "hall_sl_erpm");
        for (int i = 0;i < 8;i++) {
            mParamTab->addParamRow(mVesc->mcConfig(), QString("hall_table_%1").arg(i));
        }
    }
}

FocPage::FocPage(VescInterface *vesc, QWidget *parent)
    : QWizardPage(parent)
{
    mVesc = vesc;

    setTitle(tr("FOC 设置"));
    setSubTitle(tr("运行检测并获取 FOC 所需的参数。"));

    mParamTab = new ParamTable;
    mDetect = new DetectFoc(this);
    mDetect->setVesc(vesc);

    mParamTab->addParamRow(mVesc->mcConfig(), "foc_motor_r");
    mParamTab->addParamRow(mVesc->mcConfig(), "foc_motor_l");
    mParamTab->addParamRow(mVesc->mcConfig(), "foc_motor_flux_linkage");
    mParamTab->addParamRow(mVesc->mcConfig(), "foc_current_kp");
    mParamTab->addParamRow(mVesc->mcConfig(), "foc_current_ki");
    mParamTab->addParamRow(mVesc->mcConfig(), "foc_observer_gain");

    QVBoxLayout *layout = new QVBoxLayout;
    layout->addWidget(mParamTab);
    layout->addWidget(mDetect);
    setLayout(layout);
}

int FocPage::nextId() const
{
    int retval = SetupWizardMotor::Page_Conclusion;

    switch (field("SensorMode").toInt()) {
    case SetupWizardMotor::Sensor_Sensorless:
        retval = SetupWizardMotor::Page_Conclusion;
        break;

    case SetupWizardMotor::Sensor_Hall:
        retval = SetupWizardMotor::Page_FocHall;
        break;

    case SetupWizardMotor::Sensor_EncoderAbi:
    case SetupWizardMotor::Sensor_EncoderBiSS:
    case SetupWizardMotor::Sensor_Resolver_AD2S1205:
    case SetupWizardMotor::Sensor_Encoder_SinCos:
    case SetupWizardMotor::Sensor_EncoderAs:
    case SetupWizardMotor::Sensor_EncoderAs5x47u:
        retval = SetupWizardMotor::Page_FocEncoder;
        break;

    default:
        break;
    }

    return retval;
}

bool FocPage::validatePage()
{
    bool res = false;

    if (mDetect->lastOkValuesApplied()) {
        res = true;
    } else {
        QString msg;

        if (mDetect->allValuesOk()) {
            msg = tr("您尚未应用检测结果。是否在不使用检测值的情况下继续向导？<br><br><font color=\"red\">警告：</font>使用错误的电机参数很可能会损坏您的 VESC 和/或电机。建议选择<b>否</b>并应用检测结果。");
        } else {
            msg = tr("您尚未完成检测。是否仍要继续向导？<br><br><font color=\"red\">警告：</font>使用错误的电机参数很可能会损坏您的 VESC 和/或电机。建议选择<b>否</b>并完成检测。");
        }

        QMessageBox::StandardButton reply;
        reply = QMessageBox::warning(this,
                                     tr("是否在无检测结果的情况下继续？"),
                                     msg,
                                     QMessageBox::Yes | QMessageBox::No, QMessageBox::No);

        res = reply == QMessageBox::Yes;
    }

    if (res) {
        mVesc->commands()->setMcconf();
    }

    return res;
}

FocEncoderPage::FocEncoderPage(VescInterface *vesc, QWidget *parent)
    : QWizardPage(parent)
{
    mVesc = vesc;

    setTitle(tr("FOC 编码器设置"));
    setSubTitle(tr("检测并设置使用编码器运行 FOC 所需的设置。"));

    mParamTab = new ParamTable;
    mDetect = new DetectFocEncoder(this);
    mDetect->setVesc(vesc);

    mParamTab->addParamRow(mVesc->mcConfig(), "foc_sl_erpm");
    mParamTab->addParamRow(mVesc->mcConfig(), "foc_encoder_offset");
    mParamTab->addParamRow(mVesc->mcConfig(), "foc_encoder_ratio");
    mParamTab->addParamRow(mVesc->mcConfig(), "foc_encoder_inverted");

    QVBoxLayout *layout = new QVBoxLayout;
    layout->addWidget(mParamTab);
    layout->addWidget(mDetect);
    setLayout(layout);
}

int FocEncoderPage::nextId() const
{
    return SetupWizardMotor::Page_Conclusion;
}

bool FocEncoderPage::validatePage()
{
    mVesc->commands()->setMcconf();
    return true;
}

FocHallPage::FocHallPage(VescInterface *vesc, QWidget *parent)
    : QWizardPage(parent)
{
    mVesc = vesc;

    setTitle(tr("FOC 霍尔传感器设置"));
    setSubTitle(tr("检测并设置使用霍尔传感器运行 FOC 所需的设置。"));

    mParamTab = new ParamTable;
    mDetect = new DetectFocHall(this);
    mDetect->setVesc(vesc);

    mParamTab->addParamRow(mVesc->mcConfig(), "foc_sl_erpm");
    mParamTab->addParamRow(mVesc->mcConfig(), "foc_hall_table__0");
    mParamTab->addParamRow(mVesc->mcConfig(), "foc_hall_table__1");
    mParamTab->addParamRow(mVesc->mcConfig(), "foc_hall_table__2");
    mParamTab->addParamRow(mVesc->mcConfig(), "foc_hall_table__3");
    mParamTab->addParamRow(mVesc->mcConfig(), "foc_hall_table__4");
    mParamTab->addParamRow(mVesc->mcConfig(), "foc_hall_table__5");
    mParamTab->addParamRow(mVesc->mcConfig(), "foc_hall_table__6");
    mParamTab->addParamRow(mVesc->mcConfig(), "foc_hall_table__7");

    QVBoxLayout *layout = new QVBoxLayout;
    layout->addWidget(mParamTab);
    layout->addWidget(mDetect);
    setLayout(layout);
}

int FocHallPage::nextId() const
{
    return SetupWizardMotor::Page_Conclusion;
}

bool FocHallPage::validatePage()
{
    mVesc->commands()->setMcconf();
    return true;
}

ConclusionPage::ConclusionPage(VescInterface *vesc, QWidget *parent)
    : QWizardPage(parent)
{
    mVesc = vesc;
    setTitle(tr("完成"));

    mLabel = new QLabel(tr("您已完成 VESC® 的电机设置。下一步是运行应用设置来配置与 VESC 配合使用的接口类型。"));
    mLabel->setWordWrap(true);

    QVBoxLayout *layout = new QVBoxLayout;
    layout->addWidget(mLabel);
    setLayout(layout);
}

int ConclusionPage::nextId() const
{
    return -1;
}
