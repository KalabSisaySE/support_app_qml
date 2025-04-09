import QtQuick
import QtQuick.Controls
import QtQuick.Layouts



Item {
    id: indicatorGroupControl

    property string labelText: "Label"
    property real labelFontSize: 12
    property real indicatorSize: 12
    property string indicatorStatus: "disabled"

    // Allow parent to determine height
    implicitHeight: rowLayout.implicitHeight
    anchors.margins: 30

    RowLayout {
        id: rowLayout
        anchors.left: parent.left
        anchors.right: parent.right

        Label {
            id: indicatorLabel
            text: qsTr(labelText)
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
