/*
    Copyright 2016 - 2019 Benjamin Vedder	benjamin@vedder.se

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

#include "setupwizardapp.h"
#include <QVBoxLayout>
#include <QMessageBox>
#include <QProgressDialog>
#include "utility.h"
#include "setupwizardapp.h"

SetupWizardApp::SetupWizardApp(VescInterface *vesc, QWidget *parent)
    : QWizard(parent)
{
    mVesc = vesc;
    mVesc->commands()->setSendCan(false);

    setPage(Page_Intro, new AppIntroPage(vesc));
    setPage(Page_Connection, new AppConnectionPage(vesc));
    setPage(Page_Firmware, new AppFirmwarePage(vesc));
    setPage(Page_Multi, new AppMultiPage(vesc));
    setPage(Page_General, new AppGeneralPage(vesc));
    setPage(Page_Nunchuk, new AppNunchukPage(vesc));
    setPage(Page_Ppm_Map, new AppPpmMapPage(vesc));
    setPage(Page_Ppm, new AppPpmPage(vesc));
    setPage(Page_Adc_Map, new AppAdcMapPage(vesc));
    setPage(Page_Adc, new AppAdcPage(vesc));
    setPage(Page_Conclusion, new AppConclusionPage(vesc));

    setStartId(Page_Intro);
    setWizardStyle(ModernStyle);
    QPixmap icon_logo = QIcon(Utility::getIcon(":/res/icon.svg")).pixmap(QSize(this->devicePixelRatioF() * 48, this->devicePixelRatioF() * 48));
    icon_logo.setDevicePixelRatio(this->devicePixelRatioF());
    setPixmap(QWizard::LogoPixmap, icon_logo);
    resize(800, 450);

    setWindowTitle(tr("应用设置向导"));

    mSideLabel = new AspectImgLabel(Qt::Vertical);
    mSideLabel->setPixmap(Utility::getIcon("logo_vertical.png"));
    mSideLabel->setScaledContents(true);
    setSideWidget(mSideLabel);

    connect(this, SIGNAL(currentIdChanged(int)),
            this, SLOT(idChanged(int)));
    connect(this, SIGNAL(rejected()), this, SLOT(ended()));
    connect(this, SIGNAL(accepted()), this, SLOT(ended()));
}

void SetupWizardApp::idChanged(int id)
{
    if (id == Page_Intro || id == Page_Conclusion) {
        setSideWidget(mSideLabel);
        mSideLabel->setVisible(true);
    } else {
        setSideWidget(nullptr);
    }
}

void SetupWizardApp::ended()
{
    mVesc->commands()->getAppConf();
}

AppIntroPage::AppIntroPage(VescInterface *vesc, QWidget *parent)
    : QWizardPage(parent)
{
    mVesc = vesc;
    setTitle(tr("VESC® 输入设置向导"));

    mLabel = new QLabel(tr("此向导将帮助您选择 VESC® 使用的输入类型，并根据您的输入设置应用程序。"
                           "<br><br>"
                           "要获取向导中参数和工具的更多信息，请点击旁边的问号。"));

    mLabel->setWordWrap(true);

    QVBoxLayout *layout = new QVBoxLayout;
    layout->addWidget(mLabel);
    setLayout(layout);
}

int AppIntroPage::nextId() const
{
    if (mVesc->isPortConnected()) {
        if ((mVesc->commands()->isLimitedMode() &&
             !mVesc->commands()->getLimitedCompatibilityCommands().contains(int(COMM_GET_APPCONF))) ||
                !mResetInputOk) {
            return SetupWizardApp::Page_Firmware;
        } else {
            if (mVesc->getCanDevsLast().size() == 0) {
                return SetupWizardApp::Page_General;
            } else {
                return SetupWizardApp::Page_Multi;
            }
        }
    } else {
        return SetupWizardApp::Page_Connection;
    }
}

bool AppIntroPage::validatePage()
{
    bool res = false;

    if (!mVesc->isPortConnected()) {
        QMessageBox::StandardButton reply;
        reply = QMessageBox::information(this,
                                         tr("连接"),
                                         tr("您未连接到 VESC。是否尝试自动连接？"
                                            "<br><br>"
                                            ""
                                            "<i>请注意，USB 线必须插入且 VESC 必须通电才能建立连接。</i>"),
                                         QMessageBox::Yes | QMessageBox::No, QMessageBox::Yes);

        if (reply == QMessageBox::Yes) {
            Utility::autoconnectBlockingWithProgress(mVesc, this);
            res = true;
        }
    } else {
        mVesc->commands()->getAppConf();

        QProgressDialog dialog("Scanning CAN-Bus...", QString(), 0, 0, this);
        dialog.setWindowFlags(Qt::Dialog | Qt::WindowTitleHint | Qt::CustomizeWindowHint);
        dialog.setWindowModality(Qt::WindowModal);
        dialog.setAttribute(Qt::WA_DeleteOnClose);
        dialog.show();

        setEnabled(false);
        auto devs = mVesc->scanCan();
        mResetInputOk = Utility::resetInputCan(mVesc, devs);
        setEnabled(true);
    }

    return !res;
}

AppConnectionPage::AppConnectionPage(VescInterface *vesc, QWidget *parent)
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

int AppConnectionPage::nextId() const
{
    if (mVesc->commands()->isLimitedMode() &&
            !mVesc->commands()->getLimitedCompatibilityCommands().contains(int(COMM_GET_APPCONF))) {
        return SetupWizardApp::Page_Firmware;
    } else {
        return SetupWizardApp::Page_Multi;
    }
}

bool AppConnectionPage::isComplete() const
{
    return mVesc->fwRx();
}

AppFirmwarePage::AppFirmwarePage(VescInterface *vesc, QWidget *parent)
    : QWizardPage(parent)
{
    mVesc = vesc;

    setTitle(tr("更新固件"));
    setSubTitle(tr("您需要更新 VESC 上的固件才能与此版本的 VESC Tool 一起使用。"));

    mLabel = new QLabel(tr("您的 VESC（或 CAN 总线上的某个 VESC）固件版本过旧，需要更新。之后必须重新进行电机配置。"));

    mLabel->setWordWrap(true);

    QVBoxLayout *layout = new QVBoxLayout;
    layout->addWidget(mLabel);
    setLayout(layout);
}

int AppFirmwarePage::nextId() const
{
    return -1;
}

AppMultiPage::AppMultiPage(VescInterface *vesc, QWidget *parent)
    : QWizardPage(parent)
{
    mVesc = vesc;

    setTitle(tr("多个 VESC"));
    setSubTitle(tr("在 CAN 总线上发现多个 VESC，请选择输入连接到哪一个。"));

    mCanFwdList = new QListWidget;
    mCanFwdList->setIconSize(QSize(50, 50));
    mCanFwdList->setWordWrap(true);
    mCanFwdList->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);

    registerField("CanFwd", this, "canFwd", SIGNAL(canFwdChanged));
    connect(mCanFwdList, SIGNAL(currentRowChanged(int)),
            this, SIGNAL(canFwdChanged()));

    QVBoxLayout *layout = new QVBoxLayout;
    layout->addWidget(mCanFwdList);
    setLayout(layout);
}

void AppMultiPage::initializePage()
{
    mCanFwdList->clear();

    FW_RX_PARAMS params;
    Utility::getFwVersionBlocking(mVesc, &params);

    if (params.hwType == HW_TYPE_VESC) {
        QListWidgetItem *item = new QListWidgetItem;
        item->setText(tr("此 VESC（ID：%1）").
                      arg(mVesc->appConfig()->getParamInt("controller_id")));
        item->setIcon(Utility::getIcon("icons/Connected-96.png"));
        item->setData(Qt::UserRole, -1);
        mCanFwdList->addItem(item);
    }

    bool canLastFwd = mVesc->commands()->getSendCan();
    int canLastId = mVesc->commands()->getCanSendId();
    mVesc->ignoreCanChange(true);

    for (int dev: mVesc->getCanDevsLast()) {
        mVesc->commands()->setSendCan(true, dev);
        FW_RX_PARAMS params;
        Utility::getFwVersionBlocking(mVesc, &params);
        if (params.hwType != HW_TYPE_VESC) {
            continue;
        }

        QListWidgetItem *item = new QListWidgetItem;
        item->setText(tr("ID 为 %1 的 VESC").arg(dev));
        item->setIcon(Utility::getIcon("icons/can_off.png"));
        item->setData(Qt::UserRole, dev);
        mCanFwdList->addItem(item);
    }

    mCanFwdList->setCurrentItem(nullptr);

    mVesc->commands()->setSendCan(canLastFwd, canLastId);
    mVesc->ignoreCanChange(false);
}

int AppMultiPage::nextId() const
{
    return SetupWizardApp::Page_General;
}

bool AppMultiPage::validatePage()
{
    if (field("CanFwd").toInt() >= 0) {
        mVesc->commands()->setSendCan(true, field("CanFwd").toInt());
    } else {
        mVesc->commands()->setSendCan(false);
    }

    mVesc->commands()->getAppConf();
    Utility::waitSignal(mVesc->appConfig(), SIGNAL(updated()), 2000);

    return true;
}

void AppMultiPage::cleanupPage()
{
    // Do nothing here, but override so that fields are not reset.
}

int AppMultiPage::getCanFwd()
{
    QListWidgetItem *item = mCanFwdList->currentItem();
    int canFwd = 0;
    if (item) {
        canFwd = item->data(Qt::UserRole).toInt();
    }
    return canFwd;
}

AppGeneralPage::AppGeneralPage(VescInterface *vesc, QWidget *parent)
    : QWizardPage(parent)
{
    mVesc = vesc;

    setTitle(tr("选择应用"));
    setSubTitle(tr("选择用于控制此 VESC 的输入类型。"));

    mInputList = new QListWidget;
    QListWidgetItem *item = new QListWidgetItem;
    item->setText(tr("PPM 输入，如传统遥控接收机。"));
    item->setIcon(QIcon("://res/images/rc_rx.jpg"));
    item->setData(Qt::UserRole, SetupWizardApp::Input_Ppm);
    mInputList->addItem(item);

    item = new QListWidgetItem;
    item->setText(tr("NRF 控制器。"));
    item->setIcon(QIcon("://res/images/vedder_nunchuk.jpg"));
    item->setData(Qt::UserRole, SetupWizardApp::Input_NunchukNrf);
    mInputList->addItem(item);

    item = new QListWidgetItem;
    item->setText(tr("ADC 输入，如传统电动车油门。"));
    item->setIcon(QIcon("://res/images/ebike_throttle.jpg"));
    item->setData(Qt::UserRole, SetupWizardApp::Input_Adc);
    mInputList->addItem(item);

    item = new QListWidgetItem;
    item->setText(tr("无线 Nyko Kama Nunchuk。"));
    item->setIcon(QIcon("://res/images/nunchuk.jpg"));
    item->setData(Qt::UserRole, SetupWizardApp::Input_Nunchuk);
    mInputList->addItem(item);

    mInputList->setIconSize(QSize(60, 60));
    mInputList->setCurrentItem(nullptr);

    registerField("Input", this, "inputType", SIGNAL(inputTypeChanged));
    connect(mInputList, SIGNAL(currentRowChanged(int)),
            this, SIGNAL(inputTypeChanged()));

    QVBoxLayout *layout = new QVBoxLayout;
    layout->addWidget(mInputList);
    setLayout(layout);
}

int AppGeneralPage::nextId() const
{
    switch (field("Input").toInt()) {
    case SetupWizardApp::Input_Nunchuk:
    case SetupWizardApp::Input_NunchukNrf:
        return SetupWizardApp::Page_Nunchuk;

    case SetupWizardApp::Input_Ppm:
        return SetupWizardApp::Page_Ppm_Map;

    case SetupWizardApp::Input_Adc:
        return SetupWizardApp::Page_Adc_Map;

    default:
        break;
    }

    return SetupWizardApp::Page_Conclusion;
}

bool AppGeneralPage::validatePage()
{
    return true;
}

void AppGeneralPage::cleanupPage()
{
    // Do nothing here, but override so that fields are not reset.
}

int AppGeneralPage::getInputType()
{
    QListWidgetItem *item = mInputList->currentItem();
    int input = 0;
    if (item) {
        input = item->data(Qt::UserRole).toInt();
    }
    return input;
}

AppNunchukPage::AppNunchukPage(VescInterface *vesc, QWidget *parent)
    : QWizardPage(parent)
{
    mVesc = vesc;
    setTitle(tr("Nunchuk 配置"));

    mParamTab = new ParamTable;
    mNrfPair = new NrfPair;
    mTimer = new QTimer(this);
    mWriteButton = new QPushButton(tr(" | 将配置写入 VESC"));
    mWriteButton->setIcon(Utility::getIcon("icons/app_down.png"));
    mWriteButton->setIconSize(QSize(24, 24));

    mNrfPair->setVesc(mVesc);

    mDisplay = new DisplayPercentage;
    mDisplay->setMinimumHeight(30);
    mDisplay->setDual(true);

    QVBoxLayout *layout = new QVBoxLayout;
    layout->addWidget(mParamTab);
    layout->addWidget(mWriteButton);
    layout->addWidget(mDisplay);
    layout->addWidget(mNrfPair);
    setLayout(layout);

    connect(mVesc->commands(), SIGNAL(decodedChukReceived(double)),
            this, SLOT(decodedChukReceived(double)));
    connect(mTimer, SIGNAL(timeout()), this, SLOT(timerSlot()));
    connect(mWriteButton, SIGNAL(clicked(bool)),
            mVesc->commands(), SLOT(setAppConf()));
}

int AppNunchukPage::nextId() const
{
    return SetupWizardApp::Page_Conclusion;
}

bool AppNunchukPage::validatePage()
{
    mVesc->commands()->setAppConf();
    return true;
}

void AppNunchukPage::initializePage()
{
    mParamTab->setRowCount(0);

    mParamTab->addParamRow(mVesc->appConfig(), "app_chuk_conf.ctrl_type");
    mParamTab->addParamRow(mVesc->appConfig(), "app_chuk_conf.ramp_time_pos");
    mParamTab->addParamRow(mVesc->appConfig(), "app_chuk_conf.ramp_time_neg");
    mParamTab->addParamRow(mVesc->appConfig(), "app_chuk_conf.stick_erpm_per_s_in_cc");
    mParamTab->addParamRow(mVesc->appConfig(), "app_chuk_conf.hyst");
    mParamTab->addParamRow(mVesc->appConfig(), "app_chuk_conf.use_smart_rev");
    mParamTab->addParamRow(mVesc->appConfig(), "app_chuk_conf.smart_rev_max_duty");
    mParamTab->addParamRow(mVesc->appConfig(), "app_chuk_conf.smart_rev_ramp_time");

    mParamTab->addRowSeparator(tr("CAN 总线上的多个 VESC"));
    mParamTab->addParamRow(mVesc->appConfig(), "app_chuk_conf.tc");
    mParamTab->addParamRow(mVesc->appConfig(), "app_chuk_conf.tc_max_diff");
    mVesc->appConfig()->updateParamBool("app_chuk_conf.multi_esc", true);

    if (field("Input").toInt() == SetupWizardApp::Input_Nunchuk) {
        setSubTitle(tr("配置您的 Nyko Kama Nunchuk。"));
        mNrfPair->setVisible(false);        
        mVesc->appConfig()->updateParamEnum("app_to_use", 6);
        mVesc->commands()->setAppConf();
        Utility::waitSignal(mVesc->commands(), SIGNAL(ackReceived(QString)), 2000);
        // TODO: Figure out why setting the conf twice is required...
        mVesc->commands()->setAppConf();
        Utility::waitSignal(mVesc->commands(), SIGNAL(ackReceived(QString)), 2000);
    } else {
        setSubTitle(tr("配对并配置您的 NRF Nunchuk。"));
        mNrfPair->setVisible(true);
//        mVesc->appConfig()->updateParamEnum("app_to_use", 7);
        mVesc->appConfig()->updateParamEnum("app_to_use", 3); // Assume permanent NRF or NRF51 on UART
        mVesc->commands()->setAppConf();
        Utility::waitSignal(mVesc->commands(), SIGNAL(ackReceived(QString)), 2000);
        // TODO: Figure out why setting the conf twice is required...
        mVesc->commands()->setAppConf();
        Utility::waitSignal(mVesc->commands(), SIGNAL(ackReceived(QString)), 2000);

        QMessageBox::information(this,
                                 tr("NRF 配对"),
                                 tr("您即将开始配对 NRF Nunchuk。点击确定后，您可以使用 Nunchuk 上的任意按钮完成配对过程。请注意，Nunchuk 必须处于关闭状态才能成功配对。配对完成后，您可能需要再次使用 Nunchuk 按钮将其打开才能使用。"
                                    "<br><br>"
                                    "<font color=\"red\">警告：</font>"
                                    "配对完成后 Nunchuk 将被激活，如果您移动摇杆，电机将开始转动。请确保周围没有任何障碍物。"));

        mNrfPair->startPairing();
    }

    mTimer->start(40);
}

void AppNunchukPage::decodedChukReceived(double value)
{
    double p = value * 100.0;
    mDisplay->setValue(p);
    mDisplay->setText(tr("%1 %").
                      arg(p, 0, 'f', 1));
}

void AppNunchukPage::timerSlot()
{
    mVesc->commands()->getDecodedChuk();
}

AppPpmMapPage::AppPpmMapPage(VescInterface *vesc, QWidget *parent)
    : QWizardPage(parent)
{
    mVesc = vesc;

    setTitle(tr("PPM 映射"));
    setSubTitle(tr("映射您的 PPM 接收机。"));

    mParamTab = new ParamTable;
    mPpmMap = new PpmMap;
    mTimer = new QTimer(this);

    mPpmMap->setVesc(mVesc);

    QVBoxLayout *layout = new QVBoxLayout;
    layout->addWidget(mParamTab);
    layout->addWidget(mPpmMap);
    setLayout(layout);

    connect(mTimer, SIGNAL(timeout()), this, SLOT(timerSlot()));
    connect(mVesc->appConfig(), SIGNAL(paramChangedDouble(QObject*,QString,double)),
            this, SLOT(paramChangedDouble(QObject*,QString,double)));
}

int AppPpmMapPage::nextId() const
{
    return SetupWizardApp::Page_Ppm;
}

bool AppPpmMapPage::validatePage()
{
    mVesc->commands()->setAppConf();
    return true;
}

void AppPpmMapPage::initializePage()
{
    mParamTab->setRowCount(0);

    mParamTab->addParamRow(mVesc->appConfig(), "app_ppm_conf.pulse_start");
    mParamTab->addParamRow(mVesc->appConfig(), "app_ppm_conf.pulse_end");
    mParamTab->addParamRow(mVesc->appConfig(), "app_ppm_conf.pulse_center");
    mParamTab->addParamRow(mVesc->appConfig(), "app_ppm_conf.hyst");

    mVesc->appConfig()->updateParamEnum("app_ppm_conf.ctrl_type", 0);
    mVesc->appConfig()->updateParamEnum("app_to_use", 4);
    mVesc->commands()->setAppConf();
    Utility::waitSignal(mVesc->commands(), SIGNAL(ackReceived(QString)), 2000);
    // TODO: Figure out why setting the conf twice is required...
    mVesc->commands()->setAppConf();
    Utility::waitSignal(mVesc->commands(), SIGNAL(ackReceived(QString)), 2000);
    mTimer->start(40);
}

void AppPpmMapPage::paramChangedDouble(QObject *src, QString name, double newParam)
{
    (void)src;
    (void)newParam;

    if (name == "app_ppm_conf.pulse_start" ||
            name == "app_ppm_conf.pulse_end" ||
            name == "app_ppm_conf.pulse_center" ||
            name == "app_ppm_conf.hyst") {
        mVesc->commands()->setAppConf();
    }
}

void AppPpmMapPage::timerSlot()
{
    mVesc->commands()->getDecodedPpm();
}

AppPpmPage::AppPpmPage(VescInterface *vesc, QWidget *parent)
    : QWizardPage(parent)
{
    mVesc = vesc;

    setTitle(tr("PPM 配置"));
    setSubTitle(tr("配置您的 PPM 接收机。"));

    mParamTab = new ParamTable;
    mWriteButton = new QPushButton(tr(" | 将配置写入 VESC"));
    mWriteButton->setIcon(Utility::getIcon("icons/app_down.png"));
    mWriteButton->setIconSize(QSize(24, 24));

    QVBoxLayout *layout = new QVBoxLayout;
    layout->addWidget(mParamTab);
    layout->addWidget(mWriteButton);
    setLayout(layout);

    connect(mWriteButton, SIGNAL(clicked(bool)),
            mVesc->commands(), SLOT(setAppConf()));
}

int AppPpmPage::nextId() const
{
    return SetupWizardApp::Page_Conclusion;
}

bool AppPpmPage::validatePage()
{
    mVesc->commands()->setAppConf();
    return true;
}

void AppPpmPage::initializePage()
{
    mParamTab->setRowCount(0);

    mParamTab->addRowSeparator(tr("通用"));
    mParamTab->addParamRow(mVesc->appConfig(), "app_ppm_conf.ctrl_type");
    mParamTab->addParamRow(mVesc->appConfig(), "app_ppm_conf.median_filter");
    mParamTab->addParamRow(mVesc->appConfig(), "app_ppm_conf.safe_start");
    mParamTab->addParamRow(mVesc->appConfig(), "app_ppm_conf.ramp_time_pos");
    mParamTab->addParamRow(mVesc->appConfig(), "app_ppm_conf.ramp_time_neg");
    mParamTab->addParamRow(mVesc->appConfig(), "app_ppm_conf.pid_max_erpm");
    mParamTab->addParamRow(mVesc->appConfig(), "app_ppm_conf.max_erpm_for_dir");
    mParamTab->addParamRow(mVesc->appConfig(), "app_ppm_conf.smart_rev_max_duty");
    mParamTab->addParamRow(mVesc->appConfig(), "app_ppm_conf.smart_rev_ramp_time");

    mParamTab->addRowSeparator(tr("CAN 总线上的多个 VESC"));
    mParamTab->addParamRow(mVesc->appConfig(), "app_ppm_conf.tc");
    mParamTab->addParamRow(mVesc->appConfig(), "app_ppm_conf.tc_max_diff");
    mVesc->appConfig()->updateParamBool("app_ppm_conf.multi_esc", true);

    mVesc->appConfig()->updateParamEnum("app_ppm_conf.ctrl_type", 3);
    mVesc->commands()->setAppConf();
}

AppAdcMapPage::AppAdcMapPage(VescInterface *vesc, QWidget *parent)
    : QWizardPage(parent)
{
    mVesc = vesc;

    setTitle(tr("ADC 映射"));
    setSubTitle(tr("映射您的模拟油门。"));

    mParamTab = new ParamTable;
    mAdcMap = new AdcMap;
    mTimer = new QTimer(this);

    mAdcMap->setVesc(mVesc);

    QVBoxLayout *layout = new QVBoxLayout;
    layout->addWidget(mParamTab);
    layout->addWidget(mAdcMap);
    setLayout(layout);

    connect(mTimer, SIGNAL(timeout()), this, SLOT(timerSlot()));
    connect(mVesc->appConfig(), SIGNAL(paramChangedDouble(QObject*,QString,double)),
            this, SLOT(paramChangedDouble(QObject*,QString,double)));
    connect(mVesc->appConfig(), SIGNAL(paramChangedBool(QObject*,QString,bool)),
            this, SLOT(paramChangedBool(QObject*,QString,bool)));
}

int AppAdcMapPage::nextId() const
{
    return SetupWizardApp::Page_Adc;
}

bool AppAdcMapPage::validatePage()
{
    mVesc->commands()->setAppConf();
    return true;
}

void AppAdcMapPage::initializePage()
{
    mParamTab->setRowCount(0);

    mParamTab->addParamRow(mVesc->appConfig(), "app_adc_conf.voltage_start");
    mParamTab->addParamRow(mVesc->appConfig(), "app_adc_conf.voltage_end");
    mParamTab->addParamRow(mVesc->appConfig(), "app_adc_conf.voltage_center");
    mParamTab->addParamRow(mVesc->appConfig(), "app_adc_conf.voltage_inverted");
    mParamTab->addParamRow(mVesc->appConfig(), "app_adc_conf.voltage2_start");
    mParamTab->addParamRow(mVesc->appConfig(), "app_adc_conf.voltage2_end");
    mParamTab->addParamRow(mVesc->appConfig(), "app_adc_conf.voltage2_inverted");
    mParamTab->addParamRow(mVesc->appConfig(), "app_adc_conf.hyst");

    mVesc->appConfig()->updateParamEnum("app_to_use", 5);
    mVesc->appConfig()->updateParamEnum("app_adc_conf.ctrl_type", 0);
    mVesc->commands()->setAppConf();
    Utility::waitSignal(mVesc->commands(), SIGNAL(ackReceived(QString)), 2000);
    // TODO: Figure out why setting the conf twice is required...
    mVesc->commands()->setAppConf();
    Utility::waitSignal(mVesc->commands(), SIGNAL(ackReceived(QString)), 2000);
    mTimer->start(40);
}

void AppAdcMapPage::paramChangedDouble(QObject *src, QString name, double newParam)
{
    (void)src;
    (void)newParam;

    if (name == "app_adc_conf.voltage_start" ||
            name == "app_adc_conf.voltage_end" ||
            name == "app_adc_conf.voltage_center" ||
            name == "app_adc_conf.voltage2_start" ||
            name == "app_adc_conf.voltage2_end" ||
            name == "app_adc_conf.hyst") {
        mVesc->commands()->setAppConf();
    }
}

void AppAdcMapPage::paramChangedBool(QObject *src, QString name, bool newParam)
{
    (void)src;
    (void)newParam;

    if (name == "app_adc_conf.voltage_inverted" ||
            name == "app_adc_conf.voltage2_inverted") {
        mVesc->commands()->setAppConf();
    }
}

void AppAdcMapPage::timerSlot()
{
    mVesc->commands()->getDecodedAdc();
}

AppAdcPage::AppAdcPage(VescInterface *vesc, QWidget *parent)
    : QWizardPage(parent)
{
    mVesc = vesc;

    setTitle(tr("ADC 配置"));
    setSubTitle(tr("配置您的模拟油门。"));

    mParamTab = new ParamTable;
    mWriteButton = new QPushButton(tr(" | 将配置写入 VESC"));
    mWriteButton->setIcon(Utility::getIcon("icons/app_down.png"));
    mWriteButton->setIconSize(QSize(24, 24));

    QVBoxLayout *layout = new QVBoxLayout;
    layout->addWidget(mParamTab);
    layout->addWidget(mWriteButton);
    setLayout(layout);

    connect(mWriteButton, SIGNAL(clicked(bool)),
            mVesc->commands(), SLOT(setAppConf()));
}

int AppAdcPage::nextId() const
{
    return SetupWizardApp::Page_Conclusion;
}

bool AppAdcPage::validatePage()
{
    mVesc->commands()->setAppConf();
    return true;
}

void AppAdcPage::initializePage()
{
    mParamTab->setRowCount(0);

    mParamTab->addRowSeparator(tr("通用"));
    mParamTab->addParamRow(mVesc->appConfig(), "app_adc_conf.ctrl_type");
    mParamTab->addParamRow(mVesc->appConfig(), "app_adc_conf.use_filter");
    mParamTab->addParamRow(mVesc->appConfig(), "app_adc_conf.safe_start");
    mParamTab->addParamRow(mVesc->appConfig(), "app_adc_conf.cc_button_inverted");
    mParamTab->addParamRow(mVesc->appConfig(), "app_adc_conf.rev_button_inverted");
    mParamTab->addParamRow(mVesc->appConfig(), "app_adc_conf.ramp_time_pos");
    mParamTab->addParamRow(mVesc->appConfig(), "app_adc_conf.ramp_time_neg");

    mParamTab->addRowSeparator(tr("CAN 总线上的多个 VESC"));
    mParamTab->addParamRow(mVesc->appConfig(), "app_adc_conf.tc");
    mParamTab->addParamRow(mVesc->appConfig(), "app_adc_conf.tc_max_diff");
    mVesc->appConfig()->updateParamBool("app_adc_conf.multi_esc", true);

    mVesc->appConfig()->updateParamEnum("app_adc_conf.ctrl_type", 1);
    mVesc->commands()->setAppConf();
}

AppConclusionPage::AppConclusionPage(VescInterface *vesc, QWidget *parent)
    : QWizardPage(parent)
{
    mVesc = vesc;
    setTitle(tr("完成"));

    mLabel = new QLabel;
    mLabel->setWordWrap(true);

    QVBoxLayout *layout = new QVBoxLayout;
    layout->addWidget(mLabel);
    setLayout(layout);
}

int AppConclusionPage::nextId() const
{
    return -1;
}

void AppConclusionPage::initializePage()
{
    mLabel->setText(tr("您已完成应用设置。此时一切应已准备就绪，可以运行。"));
}
