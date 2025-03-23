import QtQuick
import QtQuick.Controls

Item {
    id: root
    width: 200
    height: 30

    // Customizable properties
    property real value: 0    // Range: 0.0-1.0
    property color backgroundColor: "#e0e0e0"
    property color progressColor: "#4CAF50"
    property real radius: height / 4  // Perfect pill shape

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
            width: (root.value / 100 )* background.width
            radius: root.radius
            color: progressColor

            // Smooth animation for value changes
            Behavior on width {
                NumberAnimation { duration: 300 }
            }
        }
    }
}

/*##^##
Designer {
    D{i:0;autoSize:true;height:40;width:200}
}
##^##*/
