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
    // ADDED: New property to control the dialog's state
    property bool isSuccess: true

    // --- Core Settings ---
    anchors.centerIn: Overlay.overlay
    modal: true
    focus: true
    padding: 0
    width: Math.min(500, Overlay.overlay.width - 40)
    height: 240 // Increased height
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
        // MODIFIED: Border color is now conditional
        border.color: isSuccess ? "#16a086" : "#e74c3c" // Green for success, Red for fail
        // MODIFIED: Border is slightly thicker to be more visible
        border.width: 2
    }

    DropShadow {
        source: backgroundRect
        radius: 15
        samples: 25
        color: "#90000000"
        verticalOffset: 4
    }

    // MODIFIED: The header is now a Row to accommodate the icon
    header: Row {
        height: 55
        spacing: 10
        // FIXED: Removed "anchors.verticalCenter: parent.verticalCenter" to prevent anchor loop.
        leftPadding: 15 // Use padding on the Row itself

        // ADDED: The status icon
        Image {
            id: icon
            width: 24
            height: 24
            anchors.verticalCenter: parent.verticalCenter
            source: { isSuccess ? "../../images/svg_images/success_icon.svg" : "../../images/svg_images/fail_icon.svg" }
            antialiasing: true
            visible: false // The ColorOverlay will be the visible element

            // FIXED: ColorOverlay is now a child of the Image to avoid conflict with the Row's layout.
            ColorOverlay {
                anchors.fill: parent
                source: parent
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
        padding: 15 // Added padding to the button box

        // MODIFIED: Using your CustomButton for consistency
        CustomButton {
            text: qsTr("OK")
            onClicked: messageDialog.closeWithAnimation()
            // MODIFIED: The button's color is now conditional
            colorDefault: isSuccess ? "#16a086" : "#c0392b"
            implicitWidth: 100
        }
    }

    onClosed: destroy()
}