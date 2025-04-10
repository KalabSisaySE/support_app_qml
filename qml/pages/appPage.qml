import QtQuick
import QtQuick.Controls
import "../controls"
import QtQuick.Layouts

Item {
    Rectangle {
        id: mainContainer
        color: "#2c313c"
        anchors.fill: parent

        property real rowHeight: 35
        property real columnSpacing: mainContainer.height * 0.02

        Rectangle {
            id: groupBox
            radius: 5
            border.color: "#16a086"
            border.width: 1
            color: "transparent"
            anchors {
                fill: parent
                topMargin: parent.height * 0.08
                leftMargin: parent.width * 0.15
                rightMargin: parent.width * 0.15
                bottomMargin: parent.height * 0.08
            }

            Rectangle {
                color: "#2c313c"
                width: groupBoxTitle.width + 6
                height: groupBoxTitle.height + 6
                x: 15
                y: -10
                Text {
                    id: groupBoxTitle
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    leftPadding: 4
                    text: qsTr("Installation and Launch")
                    color: "#c1f6ec"
                    font.pointSize: 14
                }
            }

            ColumnLayout {
                id: columnLayout
                anchors {
                    top: parent.top
                    left: parent.left
                    right: parent.right
                    topMargin: 20
                    leftMargin: 10
                    rightMargin: 10
                }
                Layout.fillWidth: true
                spacing: mainContainer.columnSpacing

                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight

                    Label {
                        text: qsTr("MacrosoftConnectQuickSupport Application:")
                        font.pointSize: 13
                        Layout.alignment: Qt.AlignVCenter
                        color: "#ffffff"
                    }

                    Item {
                        Layout.fillWidth: true
                    }

                    Item {
                        width: 150
                        height: 30
                        Layout.alignment: Qt.AlignVCenter

                        StatusIndicator {
                            id: appIndicator
                            size: 20
                            status: backend.app_installation_status
                            Layout.alignment: Qt.AlignVCenter
                            anchors.centerIn: parent
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight

                    Label {
                        text: qsTr("MacrosoftConnectQuickSupport Service:")
                        font.pointSize: 13
                        Layout.alignment: Qt.AlignVCenter
                        color: "#ffffff"
                    }


                    Item {
                        Layout.fillWidth: true
                    }

                    Item {
                        width: 150
                        height: 30
                        Layout.alignment: Qt.AlignVCenter

                        StatusIndicator {
                            id: serviceIndicator
                            size: 20
                            status: backend.app_service_status
                            Layout.alignment: Qt.AlignVCenter
                            anchors.centerIn: parent
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight

                    Label {
                        text: qsTr("Your ID:")
                        font.pointSize: 13
                        Layout.alignment: Qt.AlignVCenter
                        color: "#ffffff"
                    }

                    Item {
                        Layout.fillWidth: true
                    }

                    Item {
                        width: 150
                        height: 30
                        Layout.alignment: Qt.AlignVCenter

                        Text {
                            text: backend.rust_id
                            Layout.alignment: Qt.AlignVCenter
                            anchors.centerIn: parent
                            font.pixelSize: 18  // Adjust size as needed
                            font.italic: true
                            font.bold: true
                            color: "#13b899"
                        }
                    }
                }

                // Install button
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight

                    Label {
                        text: qsTr("Macrosoft QuickSupport Application:")
                        font.pointSize: 13
                        Layout.alignment: Qt.AlignVCenter
                        color: "#ffffff"
                    }

                    Item {
                        Layout.fillWidth: true
                    }

                    Item {
                        width: 185
                        height: 32
                        Layout.alignment: Qt.AlignVCenter

                        CustomButton {
                            id: macrosoftQuickSupportButton

                            text: qsTr("Install")
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.right: parent.right
                            anchors.rightMargin: 0

                            Layout.fillWidth: true
                            width: 185
                            height: 32

                            enabled: backend.is_app_install_btn_enabled
                            onClicked: { backend.install_or_uninstall() }
                        }
                    }
                }

                // Start button
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight

                    Label {
                        text: "Run Application:"
                        font.pointSize: 13
                        Layout.alignment: Qt.AlignVCenter
                        color: "#ffffff"
                    }

                    Item {
                        Layout.fillWidth: true
                    }

                    Item {
                        width: 185
                        height: 32
                        Layout.alignment: Qt.AlignVCenter

                        CustomButton {
                            id: startAppButton

                            text: "Start MacrosoftQuickSupport"
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.right: parent.right
                            anchors.rightMargin: 0

                            Layout.fillWidth: true
                            width: 185
                            height: 32

                            enabled: backend.is_app_start_btn_enabled

                            onClicked: {
                                backend.start_app()
                            }
                        }

                    }


                }

                // Start Service button
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight

                    Label {
                        text: "Service:"
                        font.pointSize: 13
                        Layout.alignment: Qt.AlignVCenter
                        color: "#ffffff"
                    }

                    Item {
                        Layout.fillWidth: true
                    }

                    Item {
                        width: 185
                        height: 32
                        Layout.alignment: Qt.AlignVCenter

                        CustomButton {
                            id: startServiceButton

                            text: "Start Service"
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.right: parent.right
                            anchors.rightMargin: 0

                            Layout.fillWidth: true
                            width: 185
                            height: 32

                            enabled: backend.is_app_service_btn_enabled
                            onClicked: { backend.toggle_service() }
                        }


                    }

                }


                // Rust Id button
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight

                    Label {
                        text: "Get ID for access:"
                        font.pointSize: 13
                        Layout.alignment: Qt.AlignVCenter
                        color: "#ffffff"
                    }

                    Item {
                        Layout.fillWidth: true
                    }

                    Item {
                        width: 185
                        height: 32
                        Layout.alignment: Qt.AlignVCenter

                        CustomButton {
                            id: getRustIdButton

                            text: "Get ID"
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.right: parent.right
                            anchors.rightMargin: 0

                            Layout.fillWidth: true
                            width: 185
                            height: 32

                            enabled: backend.is_app_rust_id_btn_enabled
                            onClicked: { backend.get_rustid() }
                        }


                    }

                }

            }
        }
    }


    Connections {
        target: backend

        function onAppInstallationStatusChanged(status) {
            if (status === "enabled") {
                macrosoftQuickSupportButton.text = "Uninstall"
                macrosoftQuickSupportButton.colorDefault = "#ff0000"
            } else {
                macrosoftQuickSupportButton.text = "Install"
                macrosoftQuickSupportButton.colorDefault = "#35b59d"
            }
        }

        function onAppServiceStatusChanged(status) {
            if (status === "enabled") {
                startServiceButton.text = "Stop Service"
                startServiceButton.colorDefault = "#ff0000"
            } else {
                startServiceButton.text = "Start Service"
                startServiceButton.colorDefault = "#35b59d"
            }
        }

    }


    Component.onCompleted: {

        if (backend.app_installation_status === "enabled") {
            macrosoftQuickSupportButton.text = "Uninstall"
            macrosoftQuickSupportButton.colorDefault = "#ff0000"
        } else {
            macrosoftQuickSupportButton.text = "Install"
            macrosoftQuickSupportButton.colorDefault = "#35b59d"
        }

        if (backend.app_service_status  === "enabled") {
            startServiceButton.text = "Stop Service"
            startServiceButton.colorDefault = "#ff0000"
        } else {
            startServiceButton.text = "Start Service"
            startServiceButton.colorDefault = "#35b59d"
        }

    }
}









