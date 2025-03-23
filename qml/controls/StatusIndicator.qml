import QtQuick
import QtQuick.Controls

Rectangle {

    property string status: "disabled"
    property real size: 100


    id: indicatorBorder
    width: size
    height: size
    color: "#ffffff"
    radius: width / 2
    border.color: "#000"
    border.width: width * 0.06

    Rectangle {

        property real innerSize: parent.width * 0.7

        id: indicatorInner
        width: innerSize
        height: innerSize
        radius: innerSize / 2
        anchors.centerIn: parent
    }

    states: [
        State {
            name: "disabled"
            PropertyChanges { target: indicatorInner; color: "#ff0000" }
        },
        State {
            name: "enabled"
            PropertyChanges { target: indicatorInner; color: "#4CAF50" }
        },
        State {
            name: "checking"
            PropertyChanges { target: indicatorInner; color: "#ff6600" }
        }
    ]

    state: status
}
