import QtQuick
import QtQuick.Controls
import Qt5Compat.GraphicalEffects

Button {
    id: button

    // Custom Properties
    property color colorDefault: "#35b59d"
    property color colorMouseOver: Qt.lighter(colorDefault, 1.2)
    property color colorPressed: Qt.darker(colorDefault, 1.2)
    property color colorDisabled: "#b0b0b0"

    font.bold: true

    QtObject {
        id: internal

        property var dynamicColor: button.enabled
            ? (button.down ? colorPressed : (button.hovered ? colorMouseOver : colorDefault))
            : colorDisabled
    }

    text: qsTr("Button")

    contentItem: Item {
        Text {
            id: name
            text: qsTr(button.text)
            font: button.font
            color: button.enabled ? "#ffffff" : "#d0d0d0"
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
        }
    }

    background: Rectangle {
        color: internal.dynamicColor
        radius: 4
    }

    // Prevent interaction when disabled
    onPressed: {if (!enabled) return}
    onReleased: {if (!enabled) return}
}
