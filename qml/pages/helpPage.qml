import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../controls"

Item {
    // Rectangle {
    //     id: rectangle
    //     color: "#2c313c"
    //     anchors.fill: parent
    //
    //     Rectangle {
    //         id: groupBox
    //
    //         radius: 5
    //         border.color: "#16a086"
    //         border.width: 1
    //         color: "transparent"
    //
    //         anchors {
    //             fill: parent
    //             topMargin: parent.height * 0.08
    //             leftMargin: parent.width * 0.15
    //             rightMargin: parent.width * 0.15
    //             bottomMargin: parent.height * 0.08
    //         }
    //
    //         // Legend-style title
    //         Rectangle {
    //             // text: "Permissions"
    //             color: "#2c313c"
    //             // color: "#0000ff"
    //             // font.bold: true
    //             width: groupBoxTitle.width + 6
    //             height: groupBoxTitle.height + 6
    //             x: 15
    //             y: -10
    //             // Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
    //
    //
    //
    //             Text {
    //                 id: groupBoxTitle
    //                 horizontalAlignment: Text.AlignHCenter
    //                 verticalAlignment: Text.AlignVCenter
    //                 // Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
    //                 leftPadding: 4
    //
    //                 text: "Permissions"
    //                 color: "#c1f6ec"
    //                 // font.bold: true
    //                 font.pointSize: 14
    //             }
    //
    //         }
    //
    //         ColumnLayout {
    //             id: columnLayout
    //             spacing: 9
    //
    //
    //             TextGroupControl {
    //                 id: textGroupControl1
    //                 labelFontSize: 14
    //                 textFontSize: 15
    //             }
    //
    //             IndicatorGroupControl {
    //                 id: indicatorGroupControl1
    //                 labelFontSize: 14
    //                 indicatorSize: 20
    //                 indicatorStatus: "enabled"
    //             }
    //
    //             IndicatorGroupControl {
    //                 id: indicatorGroupControl3
    //                 labelFontSize: 14
    //                 indicatorSize: 20
    //             }
    //
    //             ButtonGroupControl {
    //                 id: buttonGroupControl1
    //                 labelFontSize: 14
    //                 buttonWidth: 125
    //                 buttonText: "Spustiť MacrosoftQuickSupport"
    //                 // buttonHandler: backend.start_action
    //                 customActionRequested: backend.start_action
    //             }
    //         }
    //     }
    //
    // }

    RowLayout {
        id: rowLayout
        anchors.left: parent.left
        anchors.right: parent.right

        Label {
            id: indicatorLabel
            text: labelText
            font.pointSize: labelFontSize
            Layout.alignment: Qt.AlignVCenter
            color: "#ffffff"
            // font.bold: true
        }

        Item {
            Layout.fillWidth: true
        }

        Item {
            width: 125
            height: width * 0.25

            StatusIndicator {
                id: permissionIndicator
                size: indicatorSize
                status: indicatorStatus
                Layout.alignment: Qt.AlignVCenter
                anchors.centerIn: parent
            }
        }
    }

}