import QtQuick
import QtQuick.Controls
import Qt5Compat.GraphicalEffects
import "."

Button{
    id: btnLeftMenu
    text: qsTr("Left Menu Text")

    // CUSTOM PROPERTIES
    property url btnIconSource: "../../images/svg_images/info.svg"
    property color btnColorDefault: Theme.surface
    property color btnColorMouseOver: Theme.surfaceHover
    property color btnColorClicked: Theme.accent
    property int iconWidth: 20
    property int iconHeight: 20
    property color activeMenuColor: Theme.accentMenu
    property bool isActiveMenu: false

    QtObject{
        id: internal
        property var dynamicColor: if(btnLeftMenu.down){
                                       btnLeftMenu.down ? btnColorClicked : btnColorDefault
                                   } else {
                                       btnLeftMenu.hovered ? btnColorMouseOver : btnColorDefault
                                   }
    }

    implicitWidth: 230
    implicitHeight: 50

    background: Rectangle{
        id: bgBtn
        color: internal.dynamicColor

        Rectangle{
            anchors{
                top: parent.top
                left: parent.left
                bottom: parent.bottom
            }
            color: activeMenuColor
            width: 3
            visible: isActiveMenu
        }
    }

    contentItem: Item{
        id: content
        anchors.fill: parent

        Image {
            id: iconBtn
            source: btnIconSource
            // Icon is always centered in the 60px left area
            anchors.left: parent.left
            anchors.leftMargin: (60 - iconWidth) / 2
            anchors.verticalCenter: parent.verticalCenter
            sourceSize.width: iconWidth
            sourceSize.height: iconHeight
            fillMode: Image.PreserveAspectFit
            visible: false
            antialiasing: true
        }

        ColorOverlay{
            anchors.fill: iconBtn
            source: iconBtn
            color: Theme.textPrimary
            antialiasing: true
        }

        Text{
            color: Theme.textPrimary
            text: qsTr(btnLeftMenu.text)
            font.pointSize: 10
            font.bold: true
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: 65
            // Text is only visible when the menu is expanded
            visible: btnLeftMenu.width > 60
        }
    }
}