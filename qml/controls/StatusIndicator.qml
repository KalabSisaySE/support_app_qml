import QtQuick
import QtQuick.Controls

Rectangle {

    property string status: "disabled"
    property real size: 100


    id: indicatorBorder
    width: size
    height: size
    color: "#555" // Darker border background
    radius: width / 2
    border.color: "#333"
    border.width: 1

    Rectangle {
        // Thinner border by making inner circle larger
        property real innerSize: parent.width * 0.8

        id: indicatorInner
        width: innerSize
        height: innerSize
        radius: innerSize / 2
        anchors.centerIn: parent
    }

    states: [
        State {
            name: "disabled"
            PropertyChanges { target: indicatorInner; color: "#e74c3c" } // Red
        },
        State {
            name: "enabled"
            PropertyChanges { target: indicatorInner; color: "#2ecc71" } // Green
        },
        State {
            name: "checking"
            PropertyChanges { target: indicatorInner; color: "#f39c12" } // Orange
        }
    ]

    state: status

    Behavior on state {
        ColorAnimation { target: indicatorInner; duration: 300 }
    }
}