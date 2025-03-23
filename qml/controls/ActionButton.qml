// CustomButton.qml
import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root

    // Customizable properties
    property string buttonText: "Button"
    property real buttonWidth: 120
    property real sizeRatio: 0.25  // Height proportion relative to width
    property alias fontSize: btnText.font.pixelSize
    property color baseColor: "#4CAF50"
    signal clicked()

    // Size calculations
    width: buttonWidth
    height: buttonWidth * sizeRatio
    implicitHeight: height  // For layout compatibility

    // Visual styling
    color: baseColor
    radius: 4
    border {
        color: Qt.darker(baseColor, 1.2)
        width: 1
    }

    // Text element
    Text {
        id: btnText
        text: root.buttonText
        color: "white"
        anchors.centerIn: parent
        font {
            pixelSize: 14
            bold: true
        }
    }

    // Mouse interaction
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: {
            // root.clicked()
            controlRoot.buttonClicked()
            controlRoot.customActionRequested()
        }

        onPressed: { parent.color = Qt.darker(baseColor, 1.1) }
        onReleased: { parent.color = baseColor }
        onEntered: parent.border.color = Qt.lighter(baseColor, 1.2)
        onExited: parent.border.color = Qt.darker(baseColor, 1.2)
    }

    // Color transitions
    Behavior on color { ColorAnimation { duration: 100 } }
    Behavior on border.color { ColorAnimation { duration: 100 } }
}
