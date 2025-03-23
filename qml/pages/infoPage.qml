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
                spacing: 80
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: 50

                RowLayout {
                    id: macrosoftQuickSupportLabelRow
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.topMargin: 25


                    Label {
                        id: macrosoftQuickSupportLabel
                        text: "Macrosoft QuickSupport:"
                        font.pointSize: 14
                        Layout.alignment: Qt.AlignVCenter
                        color: "#ffffff"
                        // font.bold: true
                    }

                    Item {
                        Layout.fillWidth: true
                    }


                    CustomButton {
                        id: macrosoftQuickSupportButton
                        text: "Inštalovať"
                        Layout.maximumWidth: 200
                        Layout.fillWidth: true
                        Layout.preferredHeight: 30
                        Layout.preferredWidth: 150

                        onClicked: {
                            backend.install_and_run_macrosoft_connect()
                        }
                    }
                }

                RowLayout {
                    id: macrosoftQuickSupportIndicatorRow
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.topMargin: 25


                    Label {
                        id: macrosoftQuickSupportIndicatorLabel
                        text: "Aplikácia MacrosoftConnectQuickSupport::"
                        font.pointSize: 14
                        Layout.alignment: Qt.AlignVCenter
                        color: "#ffffff"
                        // font.bold: true
                    }

                    Item {
                        Layout.fillWidth: true
                    }


                    Item {
                        id: macrosoftQuickSupportIndicator
                        width: 125
                        height: width * 0.25

                        StatusIndicator {
                            id: appIndicator
                            size: indicatorSize
                            status: indicatorStatus
                            Layout.alignment: Qt.AlignVCenter
                            anchors.centerIn: parent
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

        //
        // function onPrintTime(time){
        //     labelDate.text = time
        // }
        //
        // function onIsVisible(isVisible){
        //     rectangleVisible.visible = isVisible
        // }
    }

}




