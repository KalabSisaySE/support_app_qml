import QtQuick
import QtQuick.Controls
import "../controls"
import QtQuick.Layouts

Item {

    Rectangle {
        id: rectangle
        color: "#2c313c"
        anchors.fill: parent

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

            // Legend-style title
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
                    text: "Inštalácia a Spustenie"
                    color: "#c1f6ec"
                    font.pointSize: 14
                }

            }


            ColumnLayout {
                id: columnLayout
                spacing: -100
                anchors.fill: parent

                Row {
                    id: macrosoftQuickSupportIndicatorRow
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.leftMargin: 25
                    anchors.rightMargin: 25

                    Label {
                        id: macrosoftQuickSupportIndicatorLabel
                        text: "Aplikácia MacrosoftConnectQuickSupport:"
                        font.pointSize: 13
                        Layout.alignment: Qt.AlignVCenter
                        color: "#ffffff"
                    }

                    Item {
                        id: macrosoftQuickSupportIndicator
                        width: 150
                        height: 30
                        anchors.right: parent.right
                        anchors.rightMargin: 0

                        StatusIndicator {
                            id: appIndicator
                            size: 20
                            status: backend.app_installation_status
                            Layout.alignment: Qt.AlignVCenter
                            anchors.centerIn: parent
                        }
                    }
                }

                Row {
                    id: serviceIndicatorRow
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.leftMargin: 25
                    anchors.rightMargin: 25

                    Label {
                        id: serviceIndicatorLabel
                        text: "Služba MacrosoftConnectQuickSupport:"
                        font.pointSize: 13
                        Layout.alignment: Qt.AlignVCenter
                        color: "#ffffff"
                    }

                    Item {
                        id: serviceIndicatorContainer
                        width: 150
                        height: 30
                        anchors.right: parent.right
                        anchors.rightMargin: 0

                        StatusIndicator {
                            id: serviceIndicator
                            size: 20
                            // status: backend.app_installation_status
                            Layout.alignment: Qt.AlignVCenter
                            anchors.centerIn: parent
                        }
                    }
                }

                Row {
                    id: macrosoftQuickSupportLabelRow
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.leftMargin: 25
                    anchors.rightMargin: 25

                    Label {
                        id: macrosoftQuickSupportLabel
                        text: "Macrosoft QuickSupport:"
                        anchors.verticalCenter: parent.verticalCenter
                        font.pointSize: 13
                        Layout.alignment: Qt.AlignVCenter
                        color: "#ffffff"
                    }


                    CustomButton {
                        id: macrosoftQuickSupportButton

                        text: "Inštalovať"
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.right: parent.right
                        anchors.rightMargin: 0

                        Layout.fillWidth: true
                        width: 185
                        height: 32

                        enabled: backend.is_app_installation_running

                        onClicked: {
                            backend.install_or_uninstall()
                        }
                    }
                }

                Row {
                    id: startAppLabelRow
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.leftMargin: 25
                    anchors.rightMargin: 25

                    Label {
                        id: startAppLabel
                        text: "Spustiť Aplikáciu:"
                        anchors.verticalCenter: parent.verticalCenter
                        font.pointSize: 13
                        Layout.alignment: Qt.AlignVCenter
                        color: "#ffffff"
                    }


                    CustomButton {
                        id: startAppButton

                        text: "Spustiť MacrosoftQuickSupport"
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.right: parent.right
                        anchors.rightMargin: 0

                        Layout.fillWidth: true
                        width: 185
                        height: 32

                        enabled: backend.app_installation_status

                        onClicked: {
                            backend.start_app()
                        }
                    }
                }


            }
        }
    }


    Connections {
        target: backend

        function onSetName(name) {
            indicatorLabel.text = name
        }

        function onAddCounter(text) {
            abtnChangeName.colorDefault = "#ff0000"
        }

        function onAppInstallationStatusChanged(status) {
            if (status === "enabled") {
                macrosoftQuickSupportButton.text = "Odinštalovať"
                macrosoftQuickSupportButton.colorDefault = "#ff0000"
            } else {
                macrosoftQuickSupportButton.text = "Inštalovať"
                macrosoftQuickSupportButton.colorDefault = "#35b59d"
            }
        }

    }


    Component.onCompleted: {

        if (backend.app_installation_status === "enabled") {
                macrosoftQuickSupportButton.text = "Odinštalovať"
                macrosoftQuickSupportButton.colorDefault = "#ff0000"

            } else {
                macrosoftQuickSupportButton.text = "Inštalovať"
                macrosoftQuickSupportButton.colorDefault = "#35b59d"

            }
        // Call the function when the component mounts
    }
}




