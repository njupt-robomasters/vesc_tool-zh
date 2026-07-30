/*
    Copyright 2021 Benjamin Vedder	benjamin@vedder.se

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

import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.3
import Vedder.vesc.vescinterface 1.0
import Vedder.vesc.bleuart 1.0
import Vedder.vesc.commands 1.0
import Vedder.vesc.utility 1.0
import Vedder.vesc.udpserversimple 1.0

Item {
    id: rootItem
    property int animationDuration: 500
    property BleUart mBle: VescIf.bleDevice()
    property Commands mCommands: VescIf.commands()
    property bool opened: true
    property bool pingTcpHub: false
    property bool scanning: false
    property bool fullLogo: true
    property var dialogParent: rootItem.parent

    onOpenedChanged: {
        if(opened){
            animationDuration = 500
            y = 0
        } else {
            y = Qt.binding(function() {return parent.height})
        }
    }

    Behavior on y {
        NumberAnimation {
            duration: animationDuration
            easing.type: Easing.InOutSine
        }
    }

    Rectangle {
        color: Utility.getAppHexColor("darkBackground")
        anchors.fill: parent
    }

    // Prevents events from passing to components behind
    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.AllButtons
        onWheel: {wheel.accepted=true}
        hoverEnabled: true
    }

    function startBleScan() {
        if (Utility.hasLocationPermission()) {
            scanning = true
            scanDotTimer.running = true
            bleModel.clear()
            vescsUdp = []
            mBle.startScan()
        } else {
            bleScanStart.open()
        }
    }

    onYChanged: {
        if (y > 1) {
            enableDialog()
        }
        if(!opened & y == height){
            animationDuration = 0
        }
    }

    ColumnLayout {
        id: column
        anchors.fill: parent
        anchors.margins: 10
        anchors.leftMargin: notchLeft
        anchors.rightMargin: notchRight

        Rectangle {
            Layout.preferredHeight: notchTop
            Layout.fillWidth: true
            opacity: 0
        }

        Image {
            id: image
            Layout.preferredWidth: Math.min(column.width, column.height*0.8) * 0.8
            Layout.preferredHeight: (sourceSize.height * Layout.preferredWidth) / sourceSize.width
            Layout.alignment: Qt.AlignHCenter | Qt.AlignBottom
            Layout.topMargin: Math.min(rootItem.width, rootItem.height) * 0.025
            Layout.bottomMargin: 0
            source: fullLogo
                    ? "qrc" + Utility.getThemePath() + "/logo.png"
                    : "qrc" + Utility.getThemePath() + "/symbol_v_wide.png"
            DragHandler {
                id: handler
                target: rootItem
                margin: 0
                xAxis.enabled: false
                yAxis.maximum: rootItem.height
                yAxis.minimum: 0

                onActiveChanged: {
                    if (handler.active) {
                        animationDuration = 3
                    } else {
                        animationDuration = 500
                        if(opened) {
                            if (rootItem.y > (rootItem.height / 4)) {
                                rootItem.opened = false
                            } else {
                                rootItem.y = 0
                            }
                        }
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Button {
                text: qsTr("隐藏")
                Layout.preferredWidth: 120
                flat: true
                onClicked: {
                    rootItem.opened = false
                }
            }

            Text {
                id: text
                Layout.fillWidth: true
                color: Utility.getAppHexColor("lightText")
                text: qsTr("已发现设备")
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
            }

            Button {
                id: scanButton
                text: qsTr("扫描...")
                enabled: true
                flat: true
                Layout.preferredWidth: 120

                onClicked: {
                    scanMenu.open()
                }

                Menu {
                    id: scanMenu

                    MenuItem {
                        text: "扫描 BLE"
                        enabled: !scanning
                        onTriggered: {
                            startBleScan()
                        }
                    }

                    MenuItem {
                        text: "Ping TCP 集线器"
                        onTriggered: {
                            bleModel.clear()
                            pingTcpHub = true
                            mBle.emitScanDone()
                        }
                    }

                    MenuItem {
                        text: "连接 TCP 集线器..."
                        onTriggered: {
                            tcpHubConnDialog.open()
                        }

                        Dialog {
                            id: tcpHubConnDialog
                            standardButtons: Dialog.Ok | Dialog.Cancel
                            modal: true
                            focus: true
                            closePolicy: Popup.CloseOnEscape
                            anchors.centerIn: parent
                            width: parent.width - 20
                            parent: rootItem.parent
                            Overlay.modal: Rectangle {
                                color: "#AA000000"
                            }

                            onAccepted: {
                                hubBox.connectToHub()
                            }

                            title: "连接 TCP 集线器"

                            TcpHubBox {
                                id: hubBox
                                anchors.fill: parent
                                showControls: false
                            }
                        }
                    }

                    MenuItem {
                        text: "清除 TCP 集线器设备"
                        onTriggered: {
                            tcpHubClearDialog.open()
                        }

                        Dialog {
                            id: tcpHubClearDialog
                            standardButtons: Dialog.Ok | Dialog.Cancel
                            modal: true
                            focus: true
                            closePolicy: Popup.CloseOnEscape
                            anchors.centerIn: parent
                            parent: rootItem.parent
                            Overlay.modal: Rectangle {
                                color: "#AA000000"
                            }

                            onAccepted: {
                                VescIf.clearTcpHubDevs()
                            }

                            title: "清除 TCP 集线器设备"

                            Text {
                                color: Utility.getAppHexColor("lightText")
                                verticalAlignment: Text.AlignVCenter
                                anchors.fill: parent
                                wrapMode: Text.WordWrap
                                text:
                                    "这将清除所有之前的 TCP 集线器连接。是否继续？"
                            }
                        }
                    }
                }
            }

            Timer {
                id: scanDotTimer
                interval: 500
                running: false
                repeat: true

                property int dots: 0
                onTriggered: {
                    var text = "正在扫描"
                    for (var i = 0;i < dots;i++) {
                        text = "-" + text + "-"
                    }

                    dots++;
                    if (dots > 3) {
                        dots = 0;
                    }

                    scanButton.text = text
                }
            }
        }

        ListModel {
            id: bleModel
        }

        ListView {
            id: bleList
            Layout.fillWidth: true
            Layout.fillHeight: true
            focus: true
            clip: true
            spacing: 5
            z:2

            Component {
                id: bleDelegate

                Rectangle {
                    width: bleList.width
                    height: 120
                    color: Utility.getAppHexColor("normalBackground")
                    radius: 10

                    RowLayout {
                        anchors.fill: parent
                        spacing: 10

                        Rectangle {
                            Layout.leftMargin: 10
                            Layout.fillWidth: true
                            opacity: 1.0
                            color: preferred ? (Utility.getAppHexColor("vescGreenMedium")) : (Utility.getAppHexColor("vescGreenDark") )
                            height: column.height + 10
                            radius: height / 2

                            ColumnLayout {
                                id: column
                                anchors.centerIn: parent
                                Image {
                                    id: image
                                    fillMode: Image.PreserveAspectFit
                                    Layout.preferredWidth: 40
                                    Layout.preferredHeight: 40
                                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                                    source: "qrc" + Utility.getThemePath() +  ({
                                       0: "icons/bluetooth.png",
                                       1: "icons/USB-96.png",
                                       2: "icons/LAN-96.png",
                                       3: "icons/Globe-96.png"
                                   }[connectionType]) 
                                }

                                Text {
                                    Layout.fillWidth: true
                                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                                    text: name
                                    horizontalAlignment: Text.AlignHCenter
                                    color: Utility.getAppHexColor("lightText")
                                    wrapMode: Text.WordWrap
                                }
                            }
                        }

                        ColumnLayout {
                            visible: connectionType === 0

                            Text {
                                Layout.alignment: Qt.AlignHCenter | Qt.AlignBottom
                                Layout.rightMargin: 5
                                color: Utility.getAppHexColor("lightText")
                                text: "首选"
                                horizontalAlignment: Text.AlignHCenter
                            }

                            Switch {
                                Layout.alignment: Qt.AlignHCenter | Qt.AlignTop
                                enabled: true
                                checked: preferred
                                onToggled: {
                                    VescIf.storeBlePreferred(bleAddr, checked)
                                    bleModel.clear()
                                    mBle.emitScanDone()
                                }
                            }
                        }

                        ColumnLayout {
                            Layout.rightMargin: 10
                            spacing: -5

                            Timer {
                                id: workaroundTimerConnect
                                property string bleAddr: ""
                                interval: 0
                                repeat: false
                                running: false
                                onTriggered: {
                                    VescIf.connectBle(workaroundTimerConnect.bleAddr)
                                }
                            }

                            Button {
                                Layout.alignment: Qt.AlignHCenter | Qt.AlignBottom
                                Layout.preferredHeight: 55
                                Layout.preferredWidth: {
                                    if (connectionType === 0) {
                                        nameButton.width
                                    } else if (connectionType === 3) {
                                        passButton.width
                                    } else {
                                        nameButton.width
                                    }
                                }

                                text: "连接"

                                onClicked: {
                                    if (connectionType === 1) {
                                        if (bleAddr === "") {
                                            VescIf.autoconnect()
                                        } else {
                                            VescIf.connectSerial(bleAddr, 115200)
                                        }
                                    } else if (connectionType === 2) {
                                        VescIf.connectTcp(bleAddr, tcpPort)
                                    } else if (connectionType === 3) {
                                        VescIf.connectTcpHubUuid(hubUuid)
                                    } else {
                                        disableDialog()
                                        workaroundTimerConnect.bleAddr = bleAddr
                                        workaroundTimerConnect.start()
                                    }
                                }
                            }

                            Button {
                                id: passButton
                                Layout.alignment: Qt.AlignHCenter | Qt.AlignBottom
                                Layout.preferredHeight: 55
                                text: "更新密码"
                                visible: connectionType === 3

                                onClicked: {
                                    hubPassDialog.uuid = hubUuid
                                    hubPassDialog.open()
                                }
                            }

                            Button {
                                id: nameButton
                                Layout.alignment: Qt.AlignHCenter | Qt.AlignBottom
                                Layout.preferredHeight: 55
                                text: "设置名称"
                                visible: connectionType === 0

                                onClicked: {
                                    bleNameDialog.addr = bleAddr
                                    stringInput.text = setName
                                    bleNameDialog.open()
                                }
                            }
                        }
                    }
                }
            }

            model: bleModel
            delegate: bleDelegate

            footer: BusyIndicator {
                Layout.alignment: Qt.AlignCenter
                Layout.fillHeight: true
                running: scanning
                width: parent.width
                height: BusyIndicator.implicitHeight*1.5

                Behavior on y {
                    NumberAnimation {
                        duration: 300;
                        easing.type: Easing.InOutSine
                    }
                }

            }
        }
    }

    property var vescsUdp: []

    UdpServerSimple {
        Component.onCompleted: {
            startServerBroadcast(65109)
        }

        onDataRx: {
            var tokens = Utility.arr2str(data).split("::")
            if (tokens.length === 3) {
                var found = false
                
                for (var i = 0; i < vescsUdp.length;i++) {
                    if (vescsUdp[i].ip === tokens[1]) {
                        vescsUdp[i].updateTime = new Date().getTime()
                        found = true
                        break
                    }
                }

                if (!found) {
                    vescsUdp[vescsUdp.length] = {
                        "name" : tokens[0],
                        "ip" : tokens[1],
                        "port" : parseInt(tokens[2]),
                        "updateTime" : new Date().getTime()
                    }
                    mBle.emitScanDone()
                }
            }
        }
    }

    Timer {
        running: true
        repeat: true
        interval: 500

        onTriggered: {
            var removed = false
            for (var i = 0; i < vescsUdp.length;i++) {
                var age = new Date().getTime() - vescsUdp[i].updateTime
                if (age > 5000) {
                    vescsUdp.splice(i, 1)
                    removed = true
                    i--;
                    if (i < 0) {
                        break
                    }
                }
            }

            if (removed) {
                bleModel.clear()
                mBle.emitScanDone()
            }

            // Re-scan serial regularly
            if (Utility.hasSerialport()) {
                mBle.emitScanDone()
            }
        }
    }

    Connections {
        target: mBle
        function formatBleDevice(name, addr){
            var shortAddr = addr
            if(Qt.platform.os == "ios" || Qt.platform.os == "mac") {
                var ids = addr.split('-')
                shortAddr = 
                    ids[0].slice(1,3) + '-' +
                    ids[1].slice(0,2) + '-' +
                    ids[2].slice(0,2) + '-' +
                    ids[3].slice(0,2) + '-' + 
                    ids[4].slice(0,2)
            }
            
            var bleName = VescIf.getBleName(addr)
            var displayName
            if (bleName.length > 0) {
                displayName = bleName
            } else {
                displayName = name
            }
            displayName += "\n[" + shortAddr + "]"
            
            return {
                "name": displayName,
                "setName": bleName,
                "preferred": VescIf.getBlePreferred(addr),
                "bleAddr": addr,
                "tcpPort": 0,
                "hubUuid": "",
                "connectionType": 0
            }        
        }
        
        function formatUDPDevice(device){
           return {
                "name": device.name + " (TCP)\n" + device.ip + ":" + device.port,
                "setName": "",
                "preferred": true,
                "bleAddr": device.ip,
                "tcpPort": device.port,
                "hubUuid": "",
                "connectionType": 2
            }
        }
        
        function formatSerialPort(port){
            return {
                "name": "Serial " + 
                    (port.isVesc ? "STM32" : port.isEsp ? "ESP32" : "") + 
                    "\n" + port.systemPath,
                "setName": "",
                "preferred": true,
                "bleAddr": port.systemPath,
                "tcpPort": 0,
                "hubUuid": "",
                "connectionType": 1
            }
        }
        
        function formatTcpHubDevice(tcpHubDevice){
           return {                         
               "name": tcpHubDevice.id + " (TCP Hub)\n" + tcpHubDevice.server,
               "setName": "",
               "preferred": true,
               "bleAddr": "",
               "tcpPort": 0,
               "hubUuid": tcpHubDevice.uuid(),
               "connectionType": 3
           }
        }
        function isModelUpdated(array, model) {
            if (array.length !== model.count) return true
            for (var i = 0; i < array.length; ++i) {
                if (JSON.stringify(model.get(i)) !== JSON.stringify(array[i])) {
                    return true
                }
            }
            return false
        }
        function onScanDone(bleDevices, done) {
            if (done) {
                scanDotTimer.running = false
                scanning = false
                scanButton.text = qsTr("扫描...")
            }

            var devices = [];
            
            for (var addr in bleDevices){
                devices.push(formatBleDevice(bleDevices[addr], addr))
            }
            
            for(var udpDevice of vescsUdp){
                devices.push(formatUDPDevice(udpDevice))
            }
            
            if (Utility.hasSerialport()) {
                for (var serialPort of VescIf.listSerialPorts()){
                    if (serialPort.isVesc || serialPort.isEsp){
                        devices.push(formatSerialPort(serialPort))
                    }
                }
            }
           
            if (pingTcpHub){
                pingTcpHub = false
                disableDialog()
                var hubDevs = VescIf.getTcpHubDevs()
                for (tcpHubDevice of hubDevs) {
                    if (tcpHubDevice.ping()) {
                        devices.push(formatTcpHubDevice(tcpHubDevice))
                    }
                }
                enableDialog()
            }

            devices.sort((a, b) => {
                             if (a.preferred === b.preferred) {
                                 if (a.connectionType === b.connectionType) {
                                     return a.name.localeCompare(b.name)
                                 }

                                 return a.connectionType - b.connectionType
                             } else {
                                return a.preferred ? -1 : 1
                             }
                         })
            
           if (isModelUpdated(devices, bleModel)){
               bleModel.clear()
               for (var device of devices){
                   bleModel.append(device)
               }
           }
        }

        function onBleError(info) {
            VescIf.emitMessageDialog("BLE 错误", info, false, false)
            enableDialog()
        }
    }

    function disableDialog() {
        commDialog.open()
        column.enabled = false
        disableTimeoutTimer.stop()
        disableTimeoutTimer.start()
    }

    function enableDialog() {
        commDialog.close()
        column.enabled = true
        disableTimeoutTimer.stop()
    }

    Timer {
        id: disableTimeoutTimer
        running: false
        repeat: false
        interval: 15000

        onTriggered: {
            enableDialog()
            VescIf.emitMessageDialog("连接",
                                     "连接超时",
                                     false, false)
        }
    }

    Dialog {
        id: commDialog
        title: "正在连接..."
        closePolicy: Popup.NoAutoClose
        modal: true
        focus: true

        Overlay.modal: Rectangle {
            color: "#AA000000"
        }

        width: parent.width - 20 - notchLeft - notchRight
        x: parent.width/2 - width/2
        y: parent.height / 2 - height / 2
        parent: rootItem.dialogParent
        ProgressBar {
            anchors.fill: parent
            indeterminate: visible
        }
    }

    Dialog {
        property string addr: ""

        id: bleNameDialog
        standardButtons: Dialog.Ok | Dialog.Cancel
        modal: true
        focus: true
        title: "设置 BLE 设备名称"

        Overlay.modal: Rectangle {
            color: "#AA000000"
        }

        width: parent.width - 20 - notchLeft - notchRight
        height: 200
        closePolicy: Popup.CloseOnEscape
        x: parent.width/2 - width/2
        y: Math.max(parent.height / 4 - height / 2, 20)
        parent: rootItem.dialogParent

        Rectangle {
            anchors.fill: parent
            height: stringInput.implicitHeight + 14
            border.width: 2
            border.color: Utility.getAppHexColor("lightestBackground")
            color: Utility.getAppHexColor("normalBackground")
            radius: 3
            TextInput {
                id: stringInput
                color: Utility.getAppHexColor("lightText")
                anchors.fill: parent
                anchors.margins: 7
                font.pointSize: 12
                focus: true
            }
        }

        onAccepted: {
            VescIf.storeBleName(addr, stringInput.text)
            VescIf.storeSettings()
            bleModel.clear()
            mBle.emitScanDone()
        }
    }

    Dialog {
        property string uuid: ""

        id: hubPassDialog
        standardButtons: Dialog.Ok | Dialog.Cancel
        modal: true
        focus: true
        title: "设置 TCP 集线器密码"

        Overlay.modal: Rectangle {
            color: "#AA000000"
        }

        width: parent.width - 20 - notchLeft - notchRight
        height: 200
        closePolicy: Popup.CloseOnEscape
        x: parent.width/2 - width/2
        y: Math.max(parent.height / 4 - height / 2, 20)
        parent: rootItem.dialogParent

        Rectangle {
            anchors.fill: parent
            height: hubPassInput.implicitHeight + 14
            border.width: 2
            border.color: Utility.getAppHexColor("lightestBackground")
            color: Utility.getAppHexColor("normalBackground")
            radius: 3
            TextInput {
                id: hubPassInput
                color: Utility.getAppHexColor("lightText")
                anchors.fill: parent
                anchors.margins: 7
                font.pointSize: 12
                focus: true
            }
        }

        onAccepted: {
            VescIf.updateTcpHubPassword(uuid, hubPassInput.text)
        }
    }

    Dialog {
        id: bleEn
        standardButtons: Dialog.Ok
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape
        anchors.centerIn: parent
        parent: rootItem.dialogParent
        Overlay.modal: Rectangle {
            color: "#AA000000"
        }

        title: "BLE 扫描"

        Text {
            color: Utility.getAppHexColor("lightText")
            verticalAlignment: Text.AlignVCenter
            anchors.fill: parent
            wrapMode: Text.WordWrap
            text: "BLE 扫描似乎无法进行。请确保您设备上的" +
                  "定位服务已开启。"
        }
    }

    Dialog {
        id: bleScanStart
        standardButtons: Dialog.Ok | Dialog.No
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape
        anchors.centerIn: parent

        width: parent.width - 20 - notchLeft - notchRight
        height: Math.min(implicitHeight, parent.height - 40 - notchBot - notchTop)
        x: (parent.width - width) / 2
        y: (parent.height - height + notchTop) / 2

        parent: rootItem.dialogParent

        Overlay.modal: Rectangle {
            color: "#AA000000"
        }

        onAccepted: {
            scanning = true
            scanDotTimer.running = true
            bleModel.clear()
            vescsUdp = []
            mBle.startScan()

            if (!Utility.isBleScanEnabled()) {
                bleEn.open()
            }
        }

        onRejected: {
            VescIf.emitMessageDialog(
                        "位置权限",
                        "如果无法获取位置权限，VESC Tool 将无法扫描蓝牙设备或记录带位置信息的数据。" +
                        "请接受请求以使用这些功能。",
                        false, false)
        }

        title: "BLE 扫描"

        Text {
            color: Utility.getAppHexColor("lightText")
            verticalAlignment: Text.AlignVCenter
            anchors.fill: parent
            wrapMode: Text.WordWrap
            text:
                "VESC Tool 需要访问您设备的位置信息以扫描" +
                "蓝牙设备，以及在实时数据记录时记录您的位置。\n\n" +

                "为了在 VESC Tool 处于后台和/或屏幕关闭时继续记录，" +
                "还需要后台数据记录权限。" +
                "否则日志只会在屏幕开启且 VESC Tool 在前台运行时记录位置信息和电机数据。"
        }
    }
}
