/*
    Copyright 2019 Benjamin Vedder	benjamin@vedder.se

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

import QtQuick 2.7
import QtQuick.Controls 2.10
import QtQuick.Layouts 1.3

import Vedder.vesc.vescinterface 1.0
import Vedder.vesc.commands 1.0
import Vedder.vesc.configparams 1.0
import Vedder.vesc.utility 1.0

Item {
    property var dialogParent: ApplicationWindow.overlay

    function openDialog() {
        dialog.open()
        loadUuids()
    }

    function loadUuids() {
        pairModel.clear()
        var uuids = VescIf.getPairedUuids()
        for (var i = 0;i < uuids.length;i++) {
            pairModel.append({"uuid": uuids[i]})
        }
    }

    Dialog {
        property ConfigParams mAppConf: VescIf.appConfig()
        property Commands mCommands: VescIf.commands()

        id: dialog
        modal: true
        focus: true
        width: parent.width - 20 - notchLeft - notchRight
        height: parent.height - 60
        closePolicy: Popup.CloseOnEscape
        x: (parent.width - width)/2
        y: 50
        parent: dialogParent
        padding: 10

        Overlay.modal: Rectangle {
            color: "#AA000000"
        }

        ColumnLayout {
            anchors.fill: parent

            Text {
                id: text
                Layout.fillWidth: true
                color: Utility.getAppHexColor("lightText")
                text: qsTr("这些是与此 VESC Tool 实例配对的 VESC。")
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
            }

            ListModel {
                id: pairModel
            }

            ListView {
                id: pairList
                Layout.fillWidth: true
                Layout.fillHeight: true
                focus: true
                clip: true
                spacing: 5

                Component {
                    id: pairDelegate

                    Rectangle {
                        property variant modelData: model

                        width: pairList.width
                        height: 60
                        color: "#30000000"
                        radius: 5

                        RowLayout {
                            anchors.fill: parent
                            spacing: 10

                            Image {
                                id: image
                                fillMode: Image.PreserveAspectFit
                                mipmap: true
                                Layout.preferredWidth: 40
                                Layout.preferredHeight: 40
                                Layout.alignment: Qt.AlignVCenter
                                Layout.leftMargin: 10
                                source: "qrc:/res/icon.svg"
                            }

                            Text {
                                Layout.fillWidth: true
                                color: Utility.getAppHexColor("lightText")
                                text: uuid
                                wrapMode: Text.Wrap
                            }

                            Button {
                                Layout.alignment: Qt.AlignVCenter
                                Layout.rightMargin: 10
                                text: "删除"

                                onClicked: {
                                    deleteDialog.open()
                                }

                                Dialog {
                                    id: deleteDialog
                                    property int indexNow: 0
                                    standardButtons: Dialog.Ok | Dialog.Cancel
                                    modal: true
                                    focus: true
                                    width: parent.width - 20
                                    closePolicy: Popup.CloseOnEscape
                                    title: "删除已配对的 VESC"
                                    x: 10
                                    y: 10 + parent.height / 2 - height / 2
                                    parent: dialogParent

                                    Overlay.modal: Rectangle {
                                        color: "#AA000000"
                                    }

                                    Text {
                                        color: Utility.getAppHexColor("lightText")
                                        verticalAlignment: Text.AlignVCenter
                                        anchors.fill: parent
                                        wrapMode: Text.WordWrap
                                        text: "这将从配对列表中删除此 VESC。如果该 VESC " +
                                              "已设置配对标志，您将无法再通过 BLE 连接它。" +
                                              "确定吗？"
                                    }

                                    onAccepted: {
                                        VescIf.deletePairedUuid(uuid)
                                        VescIf.storeSettings()
                                    }
                                }
                            }
                        }
                    }
                }

                model: pairModel
                delegate: pairDelegate
            }

            RowLayout {
                Layout.fillWidth: true
                Button {
                    Layout.preferredWidth: 50
                    Layout.fillWidth: true
                    text: "..."
                    onClicked: menu.open()

                    Menu {
                        id: menu
                        width: 500

                        MenuItem {
                            text: "添加当前设备（不配对）"
                            onTriggered: {
                                if (VescIf.isPortConnected()) {
                                    VescIf.addPairedUuid(VescIf.getConnectedUuid());
                                    VescIf.storeSettings()
                                } else {
                                    VescIf.emitMessageDialog("添加 UUID",
                                                             "您尚未连接到 VESC。请先连接然后再添加它。",
                                                             false, false)
                                }
                            }
                        }

                        MenuItem {
                            text: "通过 UUID 添加"
                            onTriggered: {
                                uuidEnter.open()
                            }
                        }

                        MenuItem {
                            text: "取消配对已连接的设备"
                            onTriggered: {
                                if (VescIf.isPortConnected()) {
                                    if (mCommands.isLimitedMode()) {
                                    VescIf.emitMessageDialog("取消配对 VESC",
                                                             "必须先更新固件才能取消配对此 VESC。",
                                                             false, false)
                                    } else {
                                        unpairConnectedDialog.open()
                                    }
                                } else {
                                    VescIf.emitMessageDialog("取消配对 VESC",
                                                             "您尚未连接到 VESC。请先连接然后再取消配对。",
                                                             false, false)
                                }
                            }
                        }
                    }
                }

                Button {
                    id: pairConnectedButton
                    text: "配对 VESC"
                    Layout.fillWidth: true
                    onClicked: {
                        if (VescIf.isPortConnected()) {
                            if (mCommands.isLimitedMode()) {
                                VescIf.emitMessageDialog("配对 VESC",
                                                         "必须先更新固件才能配对此 VESC。",
                                                         false, false)
                            } else {
                                pairConnectedDialog.open()
                            }
                        } else {
                            VescIf.emitMessageDialog("配对 VESC",
                                                     "您尚未连接到 VESC。请先连接然后再配对它。",
                                                     false, false)
                        }
                    }
                }

                Button {
                    text: "关闭"
                    Layout.fillWidth: true
                    onClicked: {
                        dialog.close()
                    }
                }
            }
        }
    }

    Dialog {
        id: pairConnectedDialog
        property int indexNow: 0
        standardButtons: Dialog.Ok | Dialog.Cancel
        modal: true
        focus: true
        width: parent.width - 20 - notchLeft - notchRight
        closePolicy: Popup.CloseOnEscape
        title: "配对已连接的 VESC"
        x: (parent.width - width)/2
        y: 10 + Math.max((parent.height - height) / 2, 10)
        parent: dialogParent

        Overlay.modal: Rectangle {
            color: "#AA000000"
        }

        Text {
            color: Utility.getAppHexColor("lightText")
            verticalAlignment: Text.AlignVCenter
            anchors.fill: parent
            wrapMode: Text.WordWrap
            text: "这将把已连接的 VESC 与此 VESC Tool 实例配对。未与此 VESC 配对的 VESC Tool 实例" +
                  "将无法再通过蓝牙连接。是否继续？"
        }

        onAccepted: {
            VescIf.addPairedUuid(VescIf.getConnectedUuid());
            VescIf.storeSettings()
            mAppConf.updateParamBool("pairing_done", true, null)
            mCommands.setAppConf()
            if (Utility.waitSignal(mCommands, "2ackReceived(QString)", 2000)) {
                VescIf.emitMessageDialog("配对成功！",
                                         "配对完成！请记下此 VESC 的 UUID（或截图保存）以便将来" +
                                         "将其添加到未配对的 VESC Tool 实例中。UUID 为：\n" +
                                         VescIf.getConnectedUuid(),
                                         true, false)
            }
        }
    }

    Dialog {
        id: unpairConnectedDialog
        property int indexNow: 0
        standardButtons: Dialog.Ok | Dialog.Cancel
        modal: true
        focus: true
        width: parent.width - 20 - notchLeft - notchRight
        closePolicy: Popup.CloseOnEscape
        title: "取消配对已连接的 VESC"
        x: (parent.width - width)/2
        y: 10 + parent.height / 2 - height / 2
        parent: dialogParent

        Overlay.modal: Rectangle {
            color: "#AA000000"
        }

        Text {
            color: Utility.getAppHexColor("lightText")
            verticalAlignment: Text.AlignVCenter
            anchors.fill: parent
            wrapMode: Text.WordWrap
            text: "这将取消配对已连接的 VESC。是否继续？"
        }

        onAccepted: {
            VescIf.deletePairedUuid(VescIf.getConnectedUuid());
            VescIf.storeSettings()
            mAppConf.updateParamBool("pairing_done", false, null)
            mCommands.setAppConf()
        }
    }

    Dialog {
        id: uuidEnter
        standardButtons: Dialog.Ok | Dialog.Cancel
        modal: true
        focus: true
        title: "添加 UUID"

        width: parent.width - 20  - notchLeft - notchRight
        height: 200
        closePolicy: Popup.CloseOnEscape
        x: (parent.width - width)/2
        y: (parent.height - height)/2
        parent: dialogParent

        Overlay.modal: Rectangle {
            color: "#AA000000"
        }

        Rectangle {
            anchors.fill: parent
            height: 20
            border.width: 2
            border.color: Utility.getAppHexColor("disabledText")
            color: Utility.getAppHexColor("lightBackground")
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
            if (stringInput.text.length > 0) {
                VescIf.addPairedUuid(stringInput.text)
            }
        }
    }

    Connections {
        target: VescIf

        function onPairingListUpdated() {
            loadUuids()
        }
    }
}
