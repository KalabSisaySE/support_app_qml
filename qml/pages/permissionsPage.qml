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
                    text: "Information"
                    color: "#c1f6ec"
                    font.pointSize: 14
                }

            }


            ColumnLayout {
                id: columnLayout
                spacing: 10
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
                            status: backend.macrosoft_rust_desk_status
                            Layout.alignment: Qt.AlignVCenter
                            anchors.centerIn: parent
                        }
                    }
                }
            }
        }
    }




}




