import QtQuick
import QtQuick.Controls

Item {
    id: root
    width: 200
    height: 15 // Made thinner

    // Customizable properties
    property real value: 0    // Range: 0.0-100.0
    property color backgroundColor: "#333"
    property color progressColor: "#16a086"
    property real radius: height / 2  // Perfect pill shape

    // Background
    Rectangle {
        id: background
        anchors.fill: parent
        radius: root.radius
        color: backgroundColor
        clip: true  // Essential for rounded corners

        // Progress fill
        Rectangle {
            id: progress
            height: parent.height
            width: (root.value / 100 ) * background.width
            radius: root.radius
            color: progressColor

            // Smooth animation for value changes
            Behavior on width {
                NumberAnimation { duration: 250; easing.type: Easing.InOutQuad }
            }
        }
    }
}