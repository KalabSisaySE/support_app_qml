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
                        text: "Webstránka:"
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
                            text: "Otvoriť webstránku"
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.right: parent.right
                            anchors.rightMargin: 0

                            Layout.fillWidth: true
                            width: 185
                            height: 32

                            enabled: backend.is_open_browser_btn_enabled

                            onClicked: {
                                backend.open_webpage()
                            }
                        }

                    }


                }
            }
        }
    }



}




