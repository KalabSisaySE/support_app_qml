import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: textGroupControl

    property string labelText: "Label"
    property real labelFontSize: 12
    property real textFontSize: 12
    property string textValue: "Value"
    property color textColor: "#16a086"

    // Allow parent to determine height
    implicitHeight: rowLayout.implicitHeight
    anchors.margins: 30

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

            Text {
                id: text1
                color: textGroupControl.textColor
                text: textGroupControl.textValue
                font.pixelSize: textGroupControl.textFontSize
                font.family: "Arial"
                font.bold: true
                font.italic: true
                // Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                anchors.centerIn: parent
            }
        }
    }
}
