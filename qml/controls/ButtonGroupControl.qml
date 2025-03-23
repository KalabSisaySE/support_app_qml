import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


Item {
    id: controlRoot

    // Label properties
    property string labelText: "Action"
    property real labelFontSize: 12

    // Button properties
    property string buttonText: "Click"
    property real buttonWidth: 100
    property real sizeRatio: 0.25
    property real fontSize: 12
    property color buttonColor: "#16a086"


    // Backend integration
    // signal clicked()
    signal buttonClicked()
    // signal customActionRequested()
    property var customActionRequested: undefined

    implicitHeight: rowLayout.implicitHeight
    anchors.margins: 30

    RowLayout {
        id: rowLayout
        anchors.fill: parent
        spacing: 15

        Label {
            text: controlRoot.labelText
            font.pointSize: controlRoot.labelFontSize
            Layout.alignment: Qt.AlignVCenter
            color: "#ffffff"
            // font.bold: true
        }

        Item {
            Layout.fillWidth: true
            Layout.minimumWidth: 10
        }


        ActionButton {
            id: customButton
            buttonText: controlRoot.buttonText
            buttonWidth: controlRoot.buttonWidth
            baseColor: controlRoot.buttonColor
            sizeRatio: controlRoot.sizeRatio
            fontSize:  controlRoot.fontSize

            onClicked: {
                if(controlRoot.buttonHandler) controlRoot.buttonHandler()
                controlRoot.clicked()
            }

            Layout.alignment: Qt.AlignVCenter
            Layout.rightMargin: 5
        }
    }
}
