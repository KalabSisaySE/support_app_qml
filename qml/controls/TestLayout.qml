import QtQuick
import QtQuick.Controls

Rectangle {
    id: groupBox
    x: 61
    y: 272
    width: 420
    height: 309
    radius: 5
    border.color: "#cccccc"
    border.width: 3
    color: "transparent"

    // Legend-style title
    Text {
        text: "Permissions"
        color: "#000"
        font.bold: true
        x: 15
        y: -10

        Rectangle {
            color: groupBox.parent ? groupBox.parent.color : "white"
            width: parent.width + 6
            height: parent.height + 4
            x: -3
            y: -1
        }
    }

    Column {
        id: column
        anchors {
            fill: parent
            topMargin: 15
            leftMargin: 10
            rightMargin: 10
            bottomMargin: 10
        }
        spacing: 59

        TextGroupControl {
            id: textGroupControl1
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.leftMargin: 0
            anchors.rightMargin: 0
        }

        IndicatorGroupControl {
            id: indicatorGroupControl1
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: textGroupControl1.bottom
            anchors.leftMargin: 0
            anchors.rightMargin: 0
            anchors.topMargin: 0
        }

        IndicatorGroupControl {
            id: indicatorGroupControl3
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: indicatorGroupControl1.bottom
            anchors.leftMargin: 0
            anchors.rightMargin: 0
            anchors.topMargin: 0
        }

        ButtonGroupControl {
            id: buttonGroupControl1
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: indicatorGroupControl3.bottom
            anchors.leftMargin: 0
            anchors.rightMargin: 0
            anchors.topMargin: 0
        }
    }
}
