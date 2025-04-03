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
                    text: "Recording"
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
                        text: "Streaming Url:"
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
                            text: backend.streaming_url
                            Layout.alignment: Qt.AlignVCenter
                            anchors.centerIn: parent
                            font.pixelSize: 18  // Adjust size as needed
                            font.italic: true
                            font.bold: true
                            color: "#13b899"
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight

                    Label {
                        text: "Course Name:"
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
                            text: backend.course_name
                            Layout.alignment: Qt.AlignVCenter
                            anchors.centerIn: parent
                            font.pixelSize: 18  // Adjust size as needed
                            font.italic: true
                            font.bold: true
                            color: "#13b899"
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight

                    Label {
                        text: "Aplikácia OBS:"
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
                            size: 20
                            status: backend.obs_installation_status
                            Layout.alignment: Qt.AlignVCenter
                            anchors.centerIn: parent
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight

                    Label {
                        text: "OBS Websocket:"
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
                            size: 20
                            status: backend.obs_websocket_status
                            Layout.alignment: Qt.AlignVCenter
                            anchors.centerIn: parent
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight

                    Label {
                        text: "Recording Status:"
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
                            size: 20
                            status: backend.recording_status
                            Layout.alignment: Qt.AlignVCenter
                            anchors.centerIn: parent
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight

                    Label {
                        text: "OBS Application:"
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
                            id: obsInstallBtn
                            text: "Install OBS"
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.right: parent.right
                            anchors.rightMargin: 0

                            Layout.fillWidth: true
                            width: 185
                            height: 32

                            enabled: backend.is_obs_install_btn_enabled

                            onClicked: {
                                backend.install_obs()
                            }
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight

                    Label {
                        text: "OBS:"
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
                            text: "Open OBS"
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.right: parent.right
                            anchors.rightMargin: 0

                            Layout.fillWidth: true
                            width: 185
                            height: 32

                            enabled: backend.is_open_obs_btn_enabled

                            onClicked: {
                                backend.open_obs()
                            }
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight

                    Label {
                        text: "Recording:"
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
                            id: recordingButton
                            text: "Spustiť nahrávanie"
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.right: parent.right
                            anchors.rightMargin: 0

                            Layout.fillWidth: true
                            width: 185
                            height: 32

                            enabled: backend.is_obs_record_btn_enabled

                            onClicked: {
                                backend.toggle_recording()
                            }
                        }
                    }
                }
            }
        }
    }

    Connections {

        target: backend

        function onRecordingStatusChanged(status) {
            if (status === "enabled") {
                recordingButton.text = "Zastaviť nahrávanie"
                recordingButton.colorDefault = "#ff0000"
            } else {
                recordingButton.text = "Spustiť nahrávanie"
                recordingButton.colorDefault = "#35b59d"
            }
        }

        function onObsInstallationStatusChanged(status) {
            if (status === "enabled") {
                obsInstallBtn.text = "Uninstall OBS"
                obsInstallBtn.colorDefault = "#ff0000"
            } else {
                obsInstallBtn.text = "Install OBS"
                obsInstallBtn.colorDefault = "#35b59d"
            }
        }

    }


    Component.onCompleted: {

        if (backend.recording_status === "enabled") {
            recordingButton.text = "Zastaviť nahrávanie"
            recordingButton.colorDefault = "#ff0000"
        } else {
            recordingButton.text = "Spustiť nahrávanie"
            recordingButton.colorDefault = "#35b59d"
        }

        if (backend.obs_installation_status === "enabled") {
            obsInstallBtn.text = "Uninstall OBS"
                obsInstallBtn.colorDefault = "#ff0000"
            } else {
                obsInstallBtn.text = "Install OBS"
                obsInstallBtn.colorDefault = "#35b59d"
            }


    }


}




