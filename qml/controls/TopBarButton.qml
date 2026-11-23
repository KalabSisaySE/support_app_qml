import QtQuick
import QtQuick.Controls
import Qt5Compat.GraphicalEffects
import "."

Button{
    id: btnTopBar
    // CUSTOM PROPERTIES
    property url btnIconSource: "../../images/svg_images/minimize_icon.svg"
    property color btnColorDefault: "transparent" // Make transparent by default
    property color btnColorMouseOver: Theme.surfaceHover
    property color btnColorClicked: Theme.accent

    QtObject{
        id: internal

        // MOUSE OVER AND CLICK CHANGE COLOR
        property var dynamicColor: if(btnTopBar.down){
                                       btnTopBar.down ? btnColorClicked : btnColorDefault
                                   } else {
                                       btnTopBar.hovered ? btnColorMouseOver : btnColorDefault
                                   }

    }

    width: 32 // Reduced size
    height: 28 // Reduced size to match title bar height

    background: Rectangle{
        id: bgBtn
        color: internal.dynamicColor

        Image {
            id: iconBtn
            source: btnIconSource
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            height: 12 // Smaller icon
            width: 12
            visible: false
            fillMode: Image.PreserveAspectFit
            antialiasing: true
        }

        ColorOverlay{
            anchors.fill: iconBtn
            source: iconBtn
            color: Theme.textMuted // Match title text color
            antialiasing: true
        }
    }
}