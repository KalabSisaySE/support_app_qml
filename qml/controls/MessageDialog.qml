// controls/MessageDialog.qml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

Dialog {
    id: messageDialog

    // --- Custom Properties ---
    property string dialogTitle: "Informácia"
    property string dialogText: ""
    property bool isSuccess: true

    // --- Core Settings ---
    anchors.centerIn: Overlay.overlay
    modal: true
    focus: true
    padding: 0
    width: Math.min(500, Overlay.overlay.width - 40)
    height: 240
    closePolicy: Popup.NoAutoClose

    // --- Animation State ---
    opacity: 0
    scale: 0.9

    // --- Animations ---
    Behavior on opacity { NumberAnimation { duration: 200; easing.type: Easing.OutQuad } }
    Behavior on scale { NumberAnimation { duration: 200; easing.type: Easing.OutBack } }

    function closeWithAnimation() {
        scale = 0.9
        opacity = 0
        closeTimer.start()
    }

    Component.onCompleted: {
        scale = 1.0
        opacity = 1.0
    }

    Timer {
        id: closeTimer
        interval: 200
        onTriggered: messageDialog.close()
    }

    // --- Custom Visuals ---
    background: Rectangle {
        id: backgroundRect
        color: "#3a4150"
        radius: 8
        border.color: isSuccess ? "#16a086" : "#e74c3c"
        border.width: 2
    }

    DropShadow {
        source: backgroundRect
        radius: 15
        samples: 25
        color: "#90000000"
        verticalOffset: 4
    }

    header: Row {
        height: 55
        spacing: 10
        leftPadding: 15

        // FIXED: The status icon is now visible and uses layer.effect for the color overlay.
        Image {
            id: icon
            width: 24
            height: 24
            anchors.verticalCenter: parent.verticalCenter
            source: isSuccess ? "../../images/svg_images/success_icon.svg" : "../../images/svg_images/fail_icon.svg"
            antialiasing: true

            // By enabling the layer, we can apply an effect directly.
            layer.enabled: true
            layer.effect: ColorOverlay {
                color: "#ffffff"
            }
        }

        // The title Label
        Label {
            text: dialogTitle
            font.bold: true
            font.pointSize: 12
            color: "#ffffff"
            anchors.verticalCenter: parent.verticalCenter
        }
    }

    contentItem: Label {
        text: dialogText
        wrapMode: Text.WordWrap
        font.pointSize: 10
        color: "#e0e0e0"
        padding: 20
        topPadding: 0
    }

    footer: DialogButtonBox {
        background: Rectangle { color: "transparent" }
        padding: 15

        CustomButton {
            text: qsTr("OK")
            onClicked: messageDialog.closeWithAnimation()
            colorDefault: isSuccess ? "#16a086" : "#c0392b"
            implicitWidth: 100
        }
    }

    onClosed: destroy()
}