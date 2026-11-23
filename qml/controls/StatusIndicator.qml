import QtQuick
import QtQuick.Controls
import "."

Rectangle {

    property string status: "disabled"
    property real size: 100


    id: indicatorBorder
    width: size
    height: size
    color: Theme.disabled // Darker border background
    radius: width / 2
    border.color: Theme.track
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
            PropertyChanges { target: indicatorInner; color: Theme.error } // Red
        },
        State {
            name: "enabled"
            PropertyChanges { target: indicatorInner; color: Theme.success } // Green
        },
        State {
            name: "checking"
            PropertyChanges { target: indicatorInner; color: Theme.warning } // Orange
        }
    ]

    state: status

    Behavior on state {
        ColorAnimation { target: indicatorInner; duration: 300 }
    }
}