import QtQuick
import QtQuick.Controls
import Qt5Compat.GraphicalEffects
import "."

Button {
    id: button

    // Custom Properties
    property color colorDefault: Theme.accentButton
    property color colorMouseOver: Qt.lighter(colorDefault, 1.2)
    property color colorPressed: Qt.darker(colorDefault, 1.2)
    property color colorDisabled: Theme.disabled // Darker disabled color

    font.bold: true
    font.pointSize: 10

    QtObject {
        id: internal

        property var dynamicColor: button.enabled
            ? (button.down ? colorPressed : (button.hovered ? colorMouseOver : colorDefault))
            : colorDisabled
    }

    text: qsTr("Button")

    contentItem: Text {
        text: qsTr(button.text)
        font: button.font
        color: button.enabled ? Theme.textPrimary : Theme.textDisabled // Lighter disabled text
        anchors.verticalCenter: parent.verticalCenter
        horizontalAlignment: Text.AlignHCenter
        elide: Text.ElideRight // This will add "..." if the text is too long

        // Add padding so text doesn't touch the edges
        leftPadding: 5
        rightPadding: 5
        width: parent.width
    }

    background: Rectangle {
        color: internal.dynamicColor
        radius: 3 // Sharper corners
    }

    // Prevent interaction when disabled
    onPressed: {if (!enabled) return}
    onReleased: {if (!enabled) return}
}