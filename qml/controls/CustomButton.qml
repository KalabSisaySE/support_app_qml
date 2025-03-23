import QtQuick 2.15
import QtQuick.Controls 2.15
import Qt5Compat.GraphicalEffects

Button {
    id: button

    // Custom Properties
    property color colorDefault: "#35b59d"
    property color colorMouseOver: Qt.lighter(colorDefault, 1.2)
    property color colorPressed: Qt.darker(colorDefault, 1.2)


    QtObject{
        id: internal

        property var dynamicColor: if(button.down){
                                       button.down ? colorPressed : colorDefault
                                   }else{
                                       button.hovered ? colorMouseOver : colorDefault
                                   }
    }

    text: qsTr("Button")
    contentItem: Item{
        Text {
            id: name
            text: button.text
            font: button.font
            color: "#ffffff"
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
        }
    }

    background: Rectangle{
        color: internal.dynamicColor
        radius: 4
    }
}
/*##^##
Designer {
    D{i:0;autoSize:true;height:40;width:200}
}
##^##*/
