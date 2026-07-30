#include "boardsetupwindow.h"
#include "ui_boardsetupwindow.h"
#include <QMessageBox>
#include <QDebug>
#include <QThread>
#include <QFileDialog>
#include <QListWidgetItem>
#include <QScrollBar>
#include <cmath>
#include <QEventLoop>
#include <QDirIterator>
#include <QDesktopServices>
#include <QProgressDialog>
#include "parametereditor.h"
#include "startupwizard.h"
#include "widgets/helpdialog.h"
#include "utility.h"
#include "widgets/paramdialog.h"
#include "widgets/detectallfocdialog.h"

BoardSetupWindow::BoardSetupWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::BoardSetupWindow)
{
    ui->setupUi(this);

    mVersion = QString::number(VT_VERSION, 'f', 2);
    mVesc = new VescInterface(this);

    mStatusInfoTime = 0;
    mStatusLabel = new QLabel(this);
    ui->statusBar->addPermanentWidget(mStatusLabel);
    mTimer = new QTimer(this);
    mKeyLeft = false;
    mKeyRight = false;


    connect(mTimer, SIGNAL(timeout()),
            this, SLOT(timerSlot()));
    connect(mVesc, SIGNAL(statusMessage(QString,bool)),
            this, SLOT(showStatusInfo(QString,bool)));
    connect(mVesc, SIGNAL(messageDialog(QString,QString,bool,bool)),
            this, SLOT(showMessageDialog(QString,QString,bool,bool)));
    connect(mVesc->commands(), SIGNAL(pingCanRx(QVector<int>,bool)),
            this, SLOT(pingCanRx(QVector<int>,bool)));
    connect(mVesc, SIGNAL(fwUploadStatus(QString,double,bool)),
            this, SLOT(fwUploadStatus(QString,double,bool)));
    connect(mVesc->commands(), SIGNAL(valuesReceived(MC_VALUES,unsigned int)),
            this, SLOT(valuesReceived(MC_VALUES,unsigned int)));

    mTimer->start(20);

    // Restore size and position
    if (mSettings.contains("boardsetupwindow/size")) {
        resize(mSettings.value("boardsetupwindow/size").toSize());
    }

    if (mSettings.contains("boardsetupwindow/position")) {
        move(mSettings.value("boardsetupwindow/position").toPoint());
    }

    if (mSettings.contains("boardsetupwindow/maximized")) {
        bool maximized = mSettings.value("boardsetupwindow/maximized").toBool();
        if (maximized) {
            showMaximized();
        }
    }

    mVesc->fwConfig()->loadParamsXml(Utility::configPath("fw.xml"));
    Utility::configLoadLatest(mVesc);

    mMcConfig_Target = new ConfigParams(this);
    mAppConfig_Target = new ConfigParams(this);
    QPair<int, int> latestSupported = Utility::configLatestSupported();
    QString FW_Ver =  QString::number(latestSupported.first) + "." + QStringLiteral("%1").arg(latestSupported.second, 2, 10, QLatin1Char('0'));
    mMcConfig_Target->loadParamsXml(Utility::configPath(FW_Ver + "/parameters_mcconf.xml"));
    mAppConfig_Target->loadParamsXml(Utility::configPath(FW_Ver + "/parameters_appconf.xml"));


    QDirIterator dir(QDir::currentPath(),QStringList() << "app_settings*.xml", QDir::NoFilter ,QDirIterator::Subdirectories);
    if(dir.hasNext()){
        loadAppConfXML(dir.next());
    }
    QDirIterator dir2(QDir::currentPath(),QStringList() << "motor_settings*.xml", QDir::NoFilter ,QDirIterator::Subdirectories);
    if(dir2.hasNext()){
        loadMotorConfXML(dir2.next());
    }
    on_serialRefreshButton_clicked();
}

BoardSetupWindow::~BoardSetupWindow()
{

    // Save settings
    mSettings.setValue("version", mVersion);
    mSettings.setValue("introVersion", VT_INTRO_VERSION);
    mSettings.setValue("boardsetupwindow/position", pos());
    mSettings.setValue("boardsetupwindow/maximized", isMaximized());

    if (!isMaximized()) {
        mSettings.setValue("boardsetupwindow/size", size());
    }

    delete ui;
}

void BoardSetupWindow::timerSlot()
{
    // Update status label
    if (mStatusInfoTime) {
        mStatusInfoTime--;
        if (!mStatusInfoTime) {
            mStatusLabel->setStyleSheet(qApp->styleSheet());
        }
    } else {
        QString str = mVesc->getConnectedPortName();
        if (str != mStatusLabel->text()) {
            mStatusLabel->setText(mVesc->getConnectedPortName());
            static QString statusLast = "";
            if (str != statusLast) {
                // mPageDebugPrint->printConsole("Status: " + str + "<br>");
                statusLast = str;
            }
        }
    }


    // RT data
    bool getRtData = false;
    bool sendAlive = false;
    if ( getRtData) {
        mVesc->commands()->getValues();
        if (mVesc->isRtLogOpen()) {
            mVesc->commands()->getValuesSetup();
        }
    }

    // APP RT data
    if (getRtData) {
        mVesc->commands()->getDecodedAdc();
        mVesc->commands()->getDecodedChuk();
        mVesc->commands()->getDecodedPpm();
    }

    // IMU Data
    if (getRtData) {
        mVesc->commands()->getImuData(0xFFFF);
    }

    // Send alive command once every 10 iterations
    if (sendAlive) {
        static int alive_cnt = 0;
        alive_cnt++;
        if (alive_cnt >= 10) {
            alive_cnt = 0;
            mVesc->commands()->sendAlive();
        }
    }

    // Read configurations if they haven't been read since starting VESC Tool



    // Disable all data streaming when uploading firmware
    if (mVesc->getFwUploadProgress() > 0.1) {
        //       ui->actionSendAlive->setChecked(false);
        //        ui->actionRtData->setChecked(false);
        //        ui->actionRtDataApp->setChecked(false);
        //        ui->actionIMU->setChecked(false);
        //       ui->actionKeyboardControl->setChecked(false);
    }


    // Run startup checks
    static bool has_run_start_checks = false;
    if (!has_run_start_checks) {

        // put code when opening tool here

        has_run_start_checks = true;
        Utility::checkVersion(mVesc);
    }
}

void BoardSetupWindow::on_startButton_clicked()
{
    ui->appConfigButton->setEnabled(false);
    ui->motorConfigButton->setEnabled(false);
    ui->appConfigEdit->setEnabled(false);
    ui->motorConfigEdit->setEnabled(false);
    ui->motorTolSlider->setEnabled(false);
    ui->startButton->setEnabled(false);
    ui->serialRefreshButton->setEnabled(false);
    ui->serialPortBox->setEnabled(false);
    ui->bleFirmwareButton->setEnabled(false);
    ui->bleFirmwareEdit->setEnabled(false);
    ui->bootloaderCheckBox->setEnabled(false);
    ui->bleCheckBox->setEnabled(false);
    ui->appCheckBox->setEnabled(false);
    ui->motorDetectionCheckBox->setEnabled(false);


    if(ui->motorDetectionCheckBox->isChecked()){
        QMessageBox::StandardButton reply;
        reply = QMessageBox::information(this,
                                         tr("电路板设置已启动"),
                                         tr("您已开始电路板设置流程，已启用电机校准。") +
                                         tr("请在按确定之前确保电机和轮子可以自由旋转而不受") +
                                         tr("干扰。"),
                                         QMessageBox::Ok|QMessageBox::Cancel);
        if(reply!=QMessageBox::Ok){
            return;
        }
    }
    ui->startButton->setEnabled(false);
    bool res;
    res = trySerialConnect();
    if(!res){
        resetRoutine();
        return;
    }
    res = tryCANScan();
    if(!res){
        return;
    }
    if(ui->bootloaderCheckBox->isChecked()){
        res = tryBootloaderUpload();
        if(!res){
            resetRoutine();
            return;
        }
        res = tryFirmwareUpload();
        if(!res){
            resetRoutine();
            return;
        }
        res = tryCANScan();
        if(!res){
            return;
        }
    }

    if(ui->bleCheckBox->isChecked()){
        res = tryBleFirmwareUpload();
        if(!res){
            resetRoutine();
            return;
        }

    }

    if(ui->motorDetectionCheckBox->isChecked()){
        res = tryFOCCalibration();
        if(!res){
            resetRoutine();
            return;
        }
        res = tryMotorDirection();
        if(!res){
            resetRoutine();
            return;
        }

        res = tryTestMotorParameters();
        if(!res){
            resetRoutine();
            return;
        }
    }

    if(ui->appCheckBox->isChecked()){
        if(num_VESCs>1){
            res = tryApplySlaveAppSettings();
            if(!res){
                resetRoutine();
                return;
            }
        }
        res = tryApplyMasterAppSettings();
        if(!res){
            resetRoutine();
            return;
        }
        res = tryRemoteTest();
        if(!res){
            resetRoutine();
            return;
        }
    }
    res = tryFinalDiagnostics();
    if(!res){
        resetRoutine();
        return;
    }
    testResultMsg = "设置已成功完成。您的开发板现在应该可以正常使用了。";
    testResult = true;
    resetRoutine();
}

void BoardSetupWindow::resetRoutine(){
    //showMessageDialog(tr("测试结果"),
    //                  tr(testResultMsg.toUtf8()),
    //                 testResult, false);
    QMessageBox::StandardButton reply;
    reply = QMessageBox::information(this,
                                     tr("测试结果："),
                                     tr(testResultMsg.toUtf8()),
                                     QMessageBox::Ok);
    mVesc->disconnectPort();
    ui->startButton->setEnabled(true);
    ui->usbConnectLabel->setStyleSheet("");

    is_Dual = false;
    num_VESCs = 0;
    HW_Name = "";

    ui->appConfigButton->setEnabled(true);
    ui->motorConfigButton->setEnabled(true);
    ui->motorTolSlider->setEnabled(true);
    ui->appConfigEdit->setEnabled(true);
    ui->motorConfigEdit->setEnabled(true);
    ui->startButton->setEnabled(true);
    ui->serialRefreshButton->setEnabled(true);
    ui->serialPortBox->setEnabled(true);
    ui->bleFirmwareButton->setEnabled(true);
    ui->bleFirmwareEdit->setEnabled(true);
    ui->bootloaderCheckBox->setEnabled(true);
    ui->bleCheckBox->setEnabled(true);
    ui->appCheckBox->setEnabled(true);
    ui->motorDetectionCheckBox->setEnabled(true);

    ui->CANScanLabel->setStyleSheet("");
    ui->bootloaderLabel->setStyleSheet("");
    ui->firmwareLabel->setStyleSheet("");
    ui->bleFirmwareLabel->setStyleSheet("");
    ui->motorDetectionLabel->setStyleSheet("");
    ui->motorDirectionLabel->setStyleSheet("");
    ui->motorTestLabel->setStyleSheet("");
    ui->appSetupLabel->setStyleSheet("");
    ui->remoteTestLabel->setStyleSheet("");

    ui->usbConnectLabel->setText("连接 USB 端口");
    ui->CANScanLabel->setText("CAN 总线扫描");
    ui->bootloaderLabel->setText("引导加载程序上传");
    ui->firmwareLabel->setText("固件上传");
    ui->bleFirmwareLabel->setText("BLE 固件上传");
    ui->motorDetectionLabel->setText("电机 FOC 检测");
    ui->motorDirectionLabel->setText("电机方向校准");
    ui->motorTestLabel->setText("电机测试");
    ui->appSetupLabel->setText("应用设置");
    ui->remoteTestLabel->setText("应用测试");

}

bool BoardSetupWindow::trySerialConnect(){
    bool res;
    mVesc->commands()->setSendCan(false);
    res = mVesc->connectSerial(ui->serialPortBox->currentData().toString(), 115200);
    if(res){
        Utility::waitSignal(mVesc, SIGNAL(fwRxChanged(bool, bool)), 5000);
    }
    if(mVesc->isPortConnected()){
        ui->usbConnectLabel->setStyleSheet("QLabel { background-color : lightGreen; color : black; }");
    }else{
        ui->usbConnectLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
        testResultMsg = "无法连接 USB。请确保设备已通电、已连接到计算机，并且选择了正确的串口。";
        testResult = false;
    }
    return mVesc->isPortConnected();
}

bool BoardSetupWindow::tryCANScan(){
    bool res = false;
    if(mVesc->isPortConnected()){
        mVesc->commands()->pingCan();
        Utility::waitSignal(mVesc->commands(), SIGNAL(pingCanRx(QVector<int>, bool)), 10000);
    }
    if(CAN_Timeout){
        res = false;
        ui->CANScanLabel->setStyleSheet("QLabel { background-color : lightGreen; color : black; }");
        testResultMsg = "无法连接 USB。请确保设备已通电、已连接到计算机，并且选择了正确的串口。";
        testResult = false;
    }else{
        res = true;
        mVesc->commands()->setSendCan(false);
        mVesc->commands()->getAppConf();
        if(!Utility::waitSignal(mVesc->appConfig(), SIGNAL(updated()), 5000)){
            ui->CANScanLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
            testResultMsg = "CAN 扫描期间无法读取应用配置。";
            return false;
        }
        int this_ID = mVesc->appConfig()->getParamInt("controller_id");
        QString canTxt("CAN IDs: " + QString::number(this_ID));
        for(int i = 0; i < CAN_IDs.size(); i++){
            canTxt = canTxt + ", " + QString::number(CAN_IDs.at(i));
        }
        canTxt = canTxt + " (" + QString::number(CAN_IDs.size() + 1) + " motors total)";
        ui->CANScanLabel->setText(canTxt);
        ui->CANScanLabel->setStyleSheet("QLabel { background-color : lightGreen; color : black; }");
    }
    HW_Name = mVesc->getFirmwareNow().split("Hw: ").last();
    HW_Name = HW_Name.split("\n").first();
    if(HW_Name.contains("STORMCORE")|| HW_Name.contains("UNITY")){
        is_Dual = true;
        num_VESCs = (CAN_IDs.size() + 1)/2;
        qDebug() << "num vescs" << num_VESCs;
    }else{
        is_Dual = false;
        num_VESCs = CAN_IDs.size() + 1;
    }
    return res;
}

bool BoardSetupWindow::tryBootloaderUpload(){   
    QString FW_Path;
    QFile file;
    file.setFileName("://res/bootloaders/generic.bin");
    is_Bootloader = true;
    if (!file.open(QIODevice::ReadOnly)) {
        QMessageBox::critical(this,
                              tr("上传错误"),
                              tr("无法打开文件。请确保路径有效。"));
        testResultMsg = "此软件中包含的引导加载程序文件有问题。";
        testResult = false;
        return false;
    }
    if (file.size() > 400000) {
        QMessageBox::critical(this,
                              tr("上传错误"),
                              tr("所选文件太大，不是有效的固件。"));
        testResultMsg = "包含的引导加载程序文件太大。";
        testResult = false;
        return false;
    }
    QByteArray data = file.readAll();

    bool fwRes = mVesc->fwUpload(data, is_Bootloader, num_VESCs > 1);
    if(fwRes){
        ui->bootloaderLabel->setStyleSheet("QLabel { background-color : lightGreen; color : black; }");
    }else{
        ui->bootloaderLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
        testResultMsg = "引导加载程序上传超时。请重试该流程，您可能需要先在 VESC Tool 之外单独更新固件。";
        testResult = false;
    }
    return fwRes;
}

bool BoardSetupWindow::tryFirmwareUpload(){
    QString FW_Path;
    QDirIterator it("://res/firmwares");
    while (it.hasNext()) {
        QFileInfo fi(it.next());
        QStringList names = fi.fileName().split("_o_");
        if (fi.isDir() && (HW_Name.isEmpty() || names.contains(HW_Name, Qt::CaseInsensitive))) {
            FW_Path = fi.absoluteFilePath() +  "/VESC_default.bin";
        }
    }
    bool fwRes = false;
    is_Bootloader = false;
    QFile file;
    if(!FW_Path.isEmpty()){
        file.setFileName(FW_Path);
        if (!file.open(QIODevice::ReadOnly)) {
            QMessageBox::critical(this,
                                  tr("上传错误"),
                                  tr("无法打开文件。请确保路径有效。"));
            testResultMsg = "此软件中包含用于您硬件的固件文件有问题。";
            testResult = false;
            return false;
        }

        QByteArray data = file.readAll();

        fwRes = mVesc->fwUpload(data, is_Bootloader, num_VESCs > 1);
        if(!fwRes){
            ui->firmwareLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
            testResultMsg = "固件上传超时。请重试该流程，您可能需要先在 VESC Tool 之外单独更新固件。";
            return false;
        }
    }else{
        // Didn't find any supported default firmwares
        ui->bootloaderLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
        testResultMsg = "固件文件路径不存在。";
        return false;
    }
    for(int j = 25; j >= 0; j--){
        ui->firmwareLabel->setText("等待重启: " + QString::number(j)  + " s");
        Utility::sleepWithEventLoop(1000);

        if (j < 20 && mVesc->lastPortAvailable()) {
            Utility::sleepWithEventLoop(1000);
            break;
        }
    }
    bool reconnected = trySerialConnect();
    if(reconnected){
        ui->firmwareLabel->setText("固件上传成功并已重新连接");
        ui->firmwareLabel->setStyleSheet("QLabel { background-color : lightGreen; color : black; }");
    }else{
        ui->firmwareLabel->setText("固件上传后设备未重新连接。");
        ui->firmwareLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
        testResult = false;
    }
    return reconnected;
}

bool BoardSetupWindow::tryBleFirmwareUpload(){
    return true;
}


bool BoardSetupWindow::tryFOCCalibration(){    
    mVesc->commands()->setSendCan(false);
    mVesc->ignoreCanChange(true);
    mVesc->commands()->getAppConf();
    if(!Utility::waitSignal(mVesc->appConfig(), SIGNAL(updated()), 5000)){
        ui->motorDetectionLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
        testResultMsg = "电机设置过程中无法读取应用配置。";
        return false;
    }
    app_enum_old = mVesc->appConfig()->getParamEnum("app_to_use");
    mVesc->appConfig()->updateParamEnum("app_to_use",0); // set to use no app
    Utility::sleepWithEventLoop(100);
    mVesc->commands()->setAppConf();
    if(!Utility::waitSignal(mVesc->commands(), SIGNAL(ackReceived(QString)), 2000)){
        ui->appSetupLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
        testResultMsg = "电机设置过程中无法写入应用配置。";
        return false;
    }





    bool xml_res = mVesc->mcConfig()->loadXml(mcXmlPath, "MCConfiguration");
    if(!xml_res){
        ui->motorDetectionLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
        testResultMsg = "FOC 校准期间电机 XML 读取失败";
        return false;
    }
    mVesc->ignoreCanChange(true);
    ui->motorDetectionLabel->setText("正在写入默认配置");
    mVesc->commands()->setSendCan(false);
    mVesc->commands()->setMcconf(false);
    Utility::waitSignal(mVesc->commands(), SIGNAL(ackReceived(QString)), 2000);

    for(int i = 0; i < CAN_IDs.size(); i++){
        mVesc->commands()->setSendCan(true, CAN_IDs.at(i));
        mVesc->commands()->setMcconf();
        Utility::waitSignal(mVesc->commands(), SIGNAL(ackReceived(QString)), 2000);
    }
    mVesc->ignoreCanChange(false);
    mVesc->commands()->setSendCan(false);

    Utility::sleepWithEventLoop(1000);
    ui->motorDetectionLabel->setText("正在运行 FOC 检测");
    double max_loss = pow(mMcConfig_Target->getParamDouble("l_current_max"),2.0) * mMcConfig_Target->getParamDouble("foc_motor_r");
    qDebug() << "max loss" << max_loss;
    mVesc->mcConfig();
    QString res = Utility::detectAllFoc(mVesc, true,
                                        max_loss,
                                        mMcConfig_Target->getParamDouble("l_in_current_min"),
                                        mMcConfig_Target->getParamDouble("l_in_current_max"),
                                        mMcConfig_Target->getParamDouble("foc_openloop_rpm"),
                                        mMcConfig_Target->getParamDouble("foc_sl_erpm"));
    if(!res.startsWith("Success!")){
        ui->motorDetectionLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
        return false;
    }
    ui->motorDetectionLabel->setText("正在检查检测值的准确性");
    mVesc->ignoreCanChange(true);
    float tolerance = (float) ui->motorTolSlider->value();
    if(ui->motorTolSlider->value() < 100){
        tolerance /= 100.0;
    }else{
        tolerance *= 100.0;
    }

    for(int i = -1; i < CAN_IDs.size(); i++){
        QString canid;
        if(i == -1){
            canid = "Master";
            mVesc->commands()->setSendCan(false);
        }  else{
            canid = QString::number(CAN_IDs.at(i));
            mVesc->commands()->setSendCan(true, CAN_IDs.at(i));
        }
        mVesc->commands()->getMcconf();
        Utility::waitSignal(mVesc->mcConfig(), SIGNAL(updated()), 5000);

        if(mcConfigOutsideParamBounds("foc_motor_r",tolerance )){
            ui->motorDetectionLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
            testResultMsg = "CAN ID " + canid + " 的电机电阻超出了目标值的容差范围。" +
                    " 请检查您的电机和绕组连接。测量电阻为 " +
                    QString::number(mVesc->mcConfig()->getParamDouble("foc_motor_r")*1.0e3)+" mOhm";
            return false;
        }

        if(mcConfigOutsideParamBounds("foc_motor_l",tolerance )){
            ui->motorDetectionLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
            testResultMsg = "CAN ID " + canid + " 的电机电感超出了目标值的容差范围。" +
                    " 请检查您的电机和绕组连接。测量电感为 " +
                    QString::number(mVesc->mcConfig()->getParamDouble("foc_motor_l")*1.0e6)+" uH";
            return false;
        }

        if(mcConfigOutsideParamBounds("foc_motor_flux_linkage",tolerance)){
            ui->motorDetectionLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
            testResultMsg = "CAN ID " + canid + " 的电机磁链超出了目标值的容差范围。" +
                    " 请检查您的电机和绕组连接，确保电机可以自由旋转。测量磁链为 " +
                    QString::number(mVesc->mcConfig()->getParamDouble("foc_motor_flux_linkage")*1.0e3)+" mWb";
            return false;
        }
        if(mVesc->mcConfig()->getParamEnum("foc_sensor_mode") != mMcConfig_Target->getParamEnum("foc_sensor_mode")){
            ui->motorDetectionLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
            testResultMsg = "CAN ID " + canid + " 的电机传感器与目标设置不匹配。" +
                    " 请确保传感器已正确插入和接线。";
            return false;
        }
    }
    mVesc->ignoreCanChange(false);
    mVesc->commands()->setSendCan(false);
    ui->motorDetectionLabel->setText("检测成功完成");
    ui->motorDetectionLabel->setStyleSheet("QLabel { background-color : lightGreen; color : black; }");
    return true;
}

bool BoardSetupWindow::tryMotorDirection(){
    int tach_start[16];
    int tach_end[16];
    QString directionStatus;
        directionStatus = tr("请正向旋转每个电机以继续。\n");
    mVesc->ignoreCanChange(true);
    QVector<int> CAN_IDs_VESC;
    FW_RX_PARAMS params;
    for(int i = -1; i < CAN_IDs.size(); i++){
        if(i<0){
            mVesc->commands()->setSendCan(false);
        }else{
            mVesc->commands()->setSendCan(true, CAN_IDs.at(i));
        }
        bool res = Utility::getFwVersionBlocking(mVesc, &params);
        if(i > 0 &&res && params.hwType == HW_TYPE_VESC){
            CAN_IDs_VESC.append(CAN_IDs.at(i));
        }
    }
    for(int i = -1; i < CAN_IDs_VESC.size(); i++){
        if(i<0){
            mVesc->commands()->setSendCan(false);
        }else{
            mVesc->commands()->setSendCan(true, CAN_IDs_VESC.at(i));
        }

        mVesc->commands()->getValues();
        if(!Utility::waitSignal(mVesc->commands(), SIGNAL(valuesReceived(MC_VALUES, unsigned int)), 2000)){
            ui->motorDirectionLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
            testResultMsg = "电机方向校准过程中无法读取转速计值。";
            return false;
        }
        tach_start[i+1] = values_now.tachometer;
        directionStatus += "  0% ";
    }
    bool allHaveTurned = false;

    QMessageBox* msgBox = new QMessageBox( this );
    msgBox->setWindowTitle( tr("旋转电机") );
    msgBox->setText(directionStatus);
    msgBox->addButton(QMessageBox::Cancel);
    msgBox->setModal( true );
    msgBox->open(this, SLOT(msgBoxClosed(QAbstractButton*)));
    mVesc->ignoreCanChange(true);
    while(!allHaveTurned){
    directionStatus = tr("请正向旋转每个电机以继续。\n");
        bool turned = true;
        for(int i = -1; i < CAN_IDs_VESC.size(); i++){

            if(i<0){
                mVesc->commands()->setSendCan(false);
            }else{
                mVesc->commands()->setSendCan(true, CAN_IDs_VESC.at(i));
            }
            Utility::sleepWithEventLoop(10);
            mVesc->commands()->getValues();
            if(Utility::waitSignal(mVesc->commands(), SIGNAL(valuesReceived(MC_VALUES, unsigned int)), 100)){
                tach_end[i+1] = values_now.tachometer;
            }
            int tachDiff = tach_start[i+1] - tach_end[i+1];
            turned &= (abs(tachDiff) >= 50);
            int percent = abs(2*tachDiff);
            percent = percent>100?100:percent;
            QString number = "motor " + QString::number(i+2) + ": " +
                    QStringLiteral("%1").arg(percent, 3, 10, QLatin1Char(' '))+ "% ";
            // number = QString::number(tach_end[i+1]) +" " + QString::number(tach_start[i+1]) + " ";
            directionStatus += number;
        }

        msgBox->setText(directionStatus);
        if(!msgBox->isVisible()){
            ui->motorDirectionLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
            testResultMsg = "方向校准被用户取消。";
            return false;
        }
        if(!mVesc->isPortConnected()){
            ui->motorDirectionLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
            testResultMsg = "方向校准期间连接断开。";
            msgBox->close();
            msgBox->deleteLater();
            return false;
        }
        allHaveTurned = turned;
    }
    mVesc->ignoreCanChange(true);
    msgBox->close();
    msgBox->deleteLater();
    double motor_current_min = mMcConfig_Target->getParamDouble("l_current_min");
    double motor_current_max = mMcConfig_Target->getParamDouble("l_current_max");
    double motor_current_in_min = mMcConfig_Target->getParamDouble("l_in_current_min");
    double motor_current_in_max = mMcConfig_Target->getParamDouble("l_in_current_max");
    for(int i = -1; i < CAN_IDs_VESC.size(); i++){
        if(i<0){
            mVesc->commands()->setSendCan(false);
        }else{
            mVesc->commands()->setSendCan(true, CAN_IDs_VESC.at(i));
        }
        Utility::sleepWithEventLoop(100);
        mVesc->commands()->getMcconf();
        if(!Utility::waitSignal(mVesc->mcConfig(), SIGNAL(updated()), 5000)){
            ui->motorDirectionLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
            testResultMsg = "电机方向校准过程中无法读取配置。";
            return false;
        }

        bool invert_motor = ((tach_start[i+1] - tach_end[i+1]) > 0);
        mVesc->mcConfig()->updateParamBool("m_invert_direction", invert_motor);
        mVesc->mcConfig()->updateParamDouble("l_current_min", motor_current_min);
        mVesc->mcConfig()->updateParamDouble("l_current_max", motor_current_max);
        mVesc->mcConfig()->updateParamDouble("l_in_current_min", motor_current_in_min);
        mVesc->mcConfig()->updateParamDouble("l_in_current_max", motor_current_in_max);
        mVesc->commands()->setMcconf(false);

        if(!Utility::waitSignal(mVesc->commands(), SIGNAL(ackReceived(QString)), 2000)){
            ui->motorDirectionLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
            testResultMsg = "电机方向校准过程中无法写入配置。";
            return false;
        }
    }

    ui->motorDirectionLabel->setStyleSheet("QLabel { background-color : lightGreen; color : black; }");
    ui->motorDirectionLabel->setText("电机方向已设置");


    return true;
}

bool BoardSetupWindow::tryTestMotorParameters(){   



    if(!ui->appCheckBox->isChecked()){
        mVesc->commands()->setSendCan(false);
        mVesc->commands()->getAppConf();
        if(!Utility::waitSignal(mVesc->appConfig(), SIGNAL(updated()), 5000)){
            ui->motorDetectionLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
            testResultMsg = "电机设置完成后无法读取应用配置。";
            return false;
        }
        mVesc->appConfig()->updateParamEnum("app_to_use",app_enum_old); // set to use no app
        mVesc->commands()->setAppConf();
        if(!Utility::waitSignal(mVesc->commands(), SIGNAL(ackReceived(QString)), 2000)){
            ui->appSetupLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
            testResultMsg = "电机设置完成后无法写入应用配置。";
            return false;
        }
    }
    return true;
}

bool BoardSetupWindow::tryApplySlaveAppSettings(){

    // I wrote this little bit to determine if it was the second or motor or not for dual drivers and then
    // realized it didn't really matter since it's ok to double write app config.
    //
    int master_ID = 0;
    mVesc->commands()->setSendCan(false);
    mVesc->commands()->getAppConf();
    if(!Utility::waitSignal(mVesc->appConfig(), SIGNAL(updated()), 5000)){
        ui->appSetupLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
        testResultMsg = "Failed to read app config during slave setup routine.";
        return false;
    }
    master_ID = mVesc->appConfig()->getParamInt("controller_id");   
    mVesc->appConfig()->updateParamEnum("app_to_use",0); // set to use uart
    mVesc->commands()->setAppConf();
    if(!Utility::waitSignal(mVesc->commands(), SIGNAL(ackReceived(QString)), 5000)){
        ui->appSetupLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
        testResultMsg = "从机应用设置过程中无法写入主配置。";
        return false;
    }

    bool xml_res = mVesc->appConfig()->loadXml(appXmlPath, "APPConfiguration");
    if(!xml_res){
        ui->appSetupLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
        testResultMsg = "app XML read failed during App Setup";
        return false;
    }


    mVesc->appConfig()->updateParamEnum("app_to_use",3); // set to use uart
    mVesc->appConfig()->updateParamEnum("can_mode",0); // set to use vesc CAN
    mVesc->appConfig()->updateParamEnum("can_baud_rate",2); // 500K baud
    mVesc->appConfig()->updateParamEnum("send_can_status",5); // send all CAN status'
    mVesc->appConfig()->updateParamInt("send_can_status_rate_hz",50); // 50 Hz
    mVesc->appConfig()->updateParamEnum("shutdown_mode",1); // set slaves to always on so they don't time out seperatley and master controls shutdown


    //    for(int i = 0; i < CAN_IDs.size(); i = i + 1){
    //
    //        is_second_motor_id |= ((master_ID + 1) == CAN_IDs.at(i));
    //        if(i>0){
    //            is_second_motor_id |= ((CAN_IDs.at(i) - CAN_IDs.at(i - 1) + 256) % 256 == 1);
    //        }
    //        is_second_motor_id &= is_Dual;
    //        is_second_motor_id = false;
    //        if(!is_second_motor_id){
    //        }

    mVesc->ignoreCanChange(true);
    for(int i = 0; i < CAN_IDs.size(); i = i + 1){
        bool is_second_master_id = is_Dual && ((master_ID + 1) == CAN_IDs.at(i));
        if(!is_second_master_id)
        {
            mVesc->commands()->setSendCan(true, CAN_IDs.at(i));
            mVesc->appConfig()->updateParamInt("controller_id", CAN_IDs.at(i));
            Utility::sleepWithEventLoop(100);
            mVesc->commands()->setAppConf();
            if(!Utility::waitSignal(mVesc->commands(), SIGNAL(ackReceived(QString)), 2000)){
                ui->appSetupLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
                testResultMsg = "从机应用设置过程中无法写入配置。";
                return false;
            }
        }
    }
    mVesc->commands()->setSendCan(false);
    mVesc->ignoreCanChange(false);
    return true;
}

bool BoardSetupWindow::tryApplyMasterAppSettings(){
    int master_ID = 0;
    mVesc->commands()->setSendCan(false);
    mVesc->commands()->getAppConf();
    if(!Utility::waitSignal(mVesc->appConfig(), SIGNAL(updated()), 5000)){
        ui->appSetupLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
        testResultMsg = "从机设置过程中无法读取应用配置。";
        return false;
    }
    master_ID = mVesc->appConfig()->getParamInt("controller_id");

    bool xml_res = mVesc->appConfig()->loadXml(appXmlPath, "APPConfiguration");
    if(!xml_res){
        ui->appSetupLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
        testResultMsg = "应用设置期间应用程序 XML 读取失败";
        return false;
    }
    mVesc->appConfig()->updateParamEnum("send_can_status",0); // don't send CAN status on master
    mVesc->appConfig()->updateParamInt("controller_id",master_ID); // don't send CAN status on master

    QString success_msg = "";

    switch(mAppConfig_Target->getParamEnum("app_to_use")){
    case 4: //ppm and uart

    case 1: //ppm
        mVesc->appConfig()->updateParamBool("app_ppm_conf.multi_esc",true);
        success_msg = "PPM Remote Config Applied";
        break;
    case 3: //uart
        // if uart only on master assume a uart based chuk remote
        mVesc->appConfig()->updateParamBool("app_chuk_conf.multi_esc",true);
        success_msg = "UART Remote Config Applied";
        break;
    case 2: //adc
        mVesc->appConfig()->updateParamBool("app_adc_conf.multi_esc",true);
        success_msg = "ADC Config Applied";
        break;
    default:
        ui->appSetupLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
        testResultMsg = "您的应用类型目前与此设置工具不兼容。";
        return false;
    }

    mVesc->commands()->setSendCan(false);
    mVesc->commands()->setAppConf();
    if(!Utility::waitSignal(mVesc->commands(), SIGNAL(ackReceived(QString)), 2000)){
        ui->appSetupLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
        testResultMsg = "主应用设置过程中无法写入配置。";
        return false;
    }

    ui->appSetupLabel->setStyleSheet("QLabel { background-color : lightGreen; color : black; }");
    ui->appSetupLabel->setText(success_msg);
    return true;
}

bool BoardSetupWindow::tryRemoteTest(){

    return true;
}

bool BoardSetupWindow::tryFinalDiagnostics(){
    return true;
}

bool BoardSetupWindow::mcConfigOutsideParamBounds(QString paramName, double tolerance) {
    qDebug() << "tolerance" << tolerance;
    double detectedParam = mVesc->mcConfig()->getParamDouble(paramName);
    double targetParam = mMcConfig_Target->getParamDouble(paramName);
    return abs(detectedParam - targetParam) > tolerance*targetParam;
}

void BoardSetupWindow::mcConfigCheckResult(QStringList paramsNotSet)
{
    if (!paramsNotSet.isEmpty()) {
        ParamDialog::showParams(tr("参数已截断"),
                                tr("以下参数被截断，因为它们被设置在允许范围之外，"
                                   "或者写入失败。如果写入失败，您可以尝试再次写入。"),
                                mVesc->mcConfig(),
                                paramsNotSet,
                                this);
    }
}



void BoardSetupWindow::on_motorConfigButton_clicked()
{
    QString path;
    path = QFileDialog::getOpenFileName(this,
                                        tr("选择要加载的电机配置文件"),
                                        ".",
                                        tr("XML 文件 (*.xml)"));

    loadMotorConfXML(path);


}

void BoardSetupWindow::on_appConfigButton_clicked()
{
    QString path;
    path = QFileDialog::getOpenFileName(this,
                                        tr("选择要加载的应用配置文件"),
                                        ".",
                                        tr("XML 文件 (*.xml)"));
    loadAppConfXML(path);
}

void BoardSetupWindow::on_bleFirmwareButton_clicked()
{
    QString filename = QFileDialog::getOpenFileName(this,
                                                    tr("选择固件文件"), ".",
                                                    tr("二进制文件 (*.bin)"));

    if (filename.isNull()) {
        return;
    }

    ui->bleFirmwareEdit->setText(filename);

}

void BoardSetupWindow::on_serialRefreshButton_clicked()
{
    if (mVesc) {
        ui->serialPortBox->clear();
        auto ports = mVesc->listSerialPorts();
        foreach(auto &info, ports) {
            auto port = info.value<VSerialInfo_t>();
            ui->serialPortBox->addItem(port.name, port.systemPath);
        }
        ui->serialPortBox->setCurrentIndex(0);
    }
}

void BoardSetupWindow::on_bootloaderCheckBox_stateChanged(){
    ui->bootloaderLabel->setEnabled(ui->bootloaderCheckBox->isChecked());
    ui->firmwareLabel->setEnabled(ui->bootloaderCheckBox->isChecked());
}

void BoardSetupWindow::on_bleCheckBox_stateChanged(){
    ui->bleFirmwareLabel->setEnabled(ui->bleCheckBox->isChecked());
}

void BoardSetupWindow::on_motorDetectionCheckBox_stateChanged(){
    ui->motorTolLabel->setEnabled(ui->motorDetectionCheckBox->isChecked());
    ui->motorTolLabel_2->setEnabled(ui->motorDetectionCheckBox->isChecked());
    ui->motorTolSlider->setEnabled(ui->motorDetectionCheckBox->isChecked());
    ui->motorDetectionLabel->setEnabled(ui->motorDetectionCheckBox->isChecked());
    ui->motorDirectionLabel->setEnabled(ui->motorDetectionCheckBox->isChecked());
    ui->motorTestLabel->setEnabled(ui->motorDetectionCheckBox->isChecked());
}

void BoardSetupWindow::on_appCheckBox_stateChanged(){
    ui->appSetupLabel->setEnabled(ui->appCheckBox->isChecked());
    ui->remoteTestLabel->setEnabled(ui->appCheckBox->isChecked());
}

void BoardSetupWindow::on_motorTolSlider_valueChanged(int value){
    if(value < 100){
        ui->motorTolLabel_2->setText(QString::number(value).rightJustified(3, ' ') + "%");
    }else{
        ui->motorTolLabel_2->setText(" INF ");
    }
}



void BoardSetupWindow::showStatusInfo(QString info, bool isGood)
{
    if (isGood) {
        mStatusLabel->setStyleSheet("QLabel { background-color : lightgreen; color : black; }");
        // mPageDebugPrint->printConsole("Status: " + info + "<br>");
    } else {
        mStatusLabel->setStyleSheet("QLabel { background-color : red; color : black; }");
        // mPageDebugPrint->printConsole("<font color=\"red\">Status: " + info + "</font><br>");
    }

    mStatusInfoTime = 80;
    mStatusLabel->setText(info);
}


void BoardSetupWindow::showMessageDialog(const QString &title, const QString &msg, bool isGood, bool richText)
{
    (void)richText;

    if (isGood) {
        QMessageBox::information(this, title, msg);
    } else {
        QMessageBox::warning(this, title, msg);
    }
}

void BoardSetupWindow::loadAppConfXML(QString path){
    if (path.isNull()) {
        return;
    }

    bool res = mAppConfig_Target->loadXml(path, "APPConfiguration");

    if (res) {
        ui->appTab->clearParams();

        switch(mAppConfig_Target->getParamEnum("app_to_use")){
        case 4: //ppm and uart
            ui->appTab->addParamRow(mAppConfig_Target, "app_uart_baudrate");
            [[clang::fallthrough]];
        case 1: //ppm
            ui->appTab->addParamRow(mAppConfig_Target, "app_ppm_conf.ctrl_type");
            ui->appTab->addParamRow(mAppConfig_Target, "app_ppm_conf.pulse_start");
            ui->appTab->addParamRow(mAppConfig_Target, "app_ppm_conf.pulse_center");
            ui->appTab->addParamRow(mAppConfig_Target, "app_ppm_conf.hyst");
            ui->appTab->addParamRow(mAppConfig_Target, "app_ppm_conf.ramp_time_pos");
            ui->appTab->addParamRow(mAppConfig_Target, "app_ppm_conf.ramp_time_neg");
            if(mAppConfig_Target->getParamBool("app_ppm_conf.tc")){
                ui->appTab->addParamRow(mAppConfig_Target, "app_ppm_conf.tc");
                ui->appTab->addParamRow(mAppConfig_Target, "app_ppm_conf.tc_max_diff");
            }
            if(mAppConfig_Target->getParamEnum("app_ppm_conf.ctrl_type") == 9){
                ui->appTab->addParamRow(mAppConfig_Target, "app_ppm_conf.smart_rev_max_duty");
                ui->appTab->addParamRow(mAppConfig_Target, "app_ppm_conf.smart_rev_ramp_time");
            }
            break;
        case 2: //adc
            break;
        case 3: //uart
            ui->appTab->addParamRow(mAppConfig_Target, "app_uart_baudrate");
            ui->appTab->addParamRow(mAppConfig_Target, "app_chuk_conf.ctrl_type");
            ui->appTab->addParamRow(mAppConfig_Target, "app_chuk_conf.hyst");
            ui->appTab->addParamRow(mAppConfig_Target, "app_chuk_conf.ramp_time_pos");
            ui->appTab->addParamRow(mAppConfig_Target, "app_chuk_conf.ramp_time_neg");
            if(mAppConfig_Target->getParamBool("app_chuk_conf.tc")){
                ui->appTab->addParamRow(mAppConfig_Target, "app_chuk_conf.tc");
                ui->appTab->addParamRow(mAppConfig_Target, "app_chuk_conf.tc_max_diff");
            }
            if(mAppConfig_Target->getParamBool("app_chuk_conf.use_smart_rev")){
                ui->appTab->addParamRow(mAppConfig_Target, "app_chuk_conf.smart_rev_max_duty");
                ui->appTab->addParamRow(mAppConfig_Target, "app_chuk_conf.smart_rev_ramp_time");
            }
            break;
        default:
            QMessageBox::StandardButton reply;
            reply = QMessageBox::warning(this,
                                         tr("不支持的应用类型"),
                                         tr("此工具目前仅支持部分应用类型。") +
                                         tr("加载的应用配置类型不同，不兼容。"),
                                         QMessageBox::Ok);
            ui->appCheckBox->setCheckable(false);
            ui->appCheckBox->setCheckState(Qt::Unchecked);
            return;
        }

        appXmlPath = path;
        ui->appConfigEdit->setText(path);
        showStatusInfo("Loaded app configuration", true);
        QString str;

        ui->appTab->addParamRow(mAppConfig_Target, "app_to_use");
        foreach(QObject *p, ui->appTab->children().at(0)->children()){
            p->setProperty("enabled",false);
        }
        ui->appCheckBox->setCheckable(true);
        ui->appCheckBox->setCheckState(Qt::Checked);

    } else {
        showMessageDialog(tr("加载应用配置"),
                          tr("无法加载应用配置：<BR>"
                             "%1").arg(mAppConfig_Target->xmlStatus()),
                          false, false);
    }
}
void BoardSetupWindow::loadMotorConfXML(QString path){


    if (path.isNull()) {
        return;
    }



    bool res = mMcConfig_Target->loadXml(path, "MCConfiguration");

    if (res) {
        ui->motorTab->clearParams();
        if(mMcConfig_Target->getParamEnum("motor_type") != 2){
            QMessageBox::StandardButton reply;
            reply = QMessageBox::warning(this,
                                         tr("不支持的电机类型"),
                                         tr("此工具目前仅支持 FOC 电机校准。") +
                                         tr("加载的配置电机类型不同，不兼容。"),
                                         QMessageBox::Ok);
            ui->motorDetectionCheckBox->setCheckable(false);
            ui->motorDetectionCheckBox->setCheckState(Qt::Unchecked);
            return;
        }
        mcXmlPath = path;
        showStatusInfo("Loaded motor configuration", true);
        QString str;
        ui->motorTab->addParamRow(mMcConfig_Target, "foc_motor_r");
        ui->motorTab->addParamRow(mMcConfig_Target, "foc_motor_l");
        ui->motorTab->addParamRow(mMcConfig_Target, "foc_motor_flux_linkage");
        ui->motorTab->addParamRow(mMcConfig_Target, "foc_sensor_mode");
        ui->motorTab->addParamRow(mMcConfig_Target, "l_current_max");
        ui->motorTab->addParamRow(mMcConfig_Target, "l_current_min");
        ui->motorTab->addParamRow(mMcConfig_Target, "l_in_current_max");
        ui->motorTab->addParamRow(mMcConfig_Target, "l_in_current_min");
        ui->motorTab->addParamRow(mMcConfig_Target, "l_battery_cut_start");
        ui->motorTab->addParamRow(mMcConfig_Target, "l_battery_cut_end");
        ui->motorConfigEdit->setText(path);

        foreach(QObject *p, ui->motorTab->children().at(0)->children()){
            p->setProperty("enabled",false);
        }
        ui->motorDetectionCheckBox->setCheckable(true);
        ui->motorDetectionCheckBox->setCheckState(Qt::Checked);
    } else {
        showMessageDialog(tr("加载电机配置"),
                          tr("无法加载电机配置：<BR>"
                             "%1").arg(mVesc->mcConfig()->xmlStatus()),
                          false, false);
    }

}

void BoardSetupWindow::pingCanRx(QVector<int> devs, bool isTimeout)
{
    CAN_Timeout = isTimeout;
    if(!isTimeout){
        CAN_IDs = devs;
    }
}

void BoardSetupWindow::fwUploadStatus(const QString &status, double progress, bool isOngoing)
{
    if(is_Bootloader){
        if (isOngoing) {
            ui->bootloaderLabel->setText(tr("%1 (%2 %)").
                                         arg(status).
                                         arg(progress * 100, 0, 'f', 1));
        } else {
            ui->bootloaderLabel->setText("引导加载程序 " + status);
        }
    }else{
        if (isOngoing) {
            ui->firmwareLabel->setText(tr("%1 (%2 %)").
                                       arg(status).
                                       arg(progress * 100, 0, 'f', 1));
        } else {
            ui->firmwareLabel->setText("固件 " + status);
        }
    }
}

void BoardSetupWindow::valuesReceived(MC_VALUES values, unsigned int mask)
{
    (void)mask;
    values_now = values;
}

