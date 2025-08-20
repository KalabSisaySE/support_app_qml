// controls/MessageDialog.qml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects // Import needed for the DropShadow effect

Dialog {
    id: messageDialog

    // --- Custom Properties ---
    property string dialogTitle: "Informácia"
    property string dialogText: ""

    // --- Core Settings ---
    anchors.centerIn: Overlay.overlay
    modal: true
    focus: true
    padding: 0
    // UPDATED: Made the dialog larger
    width: Math.min(500, Overlay.overlay.width - 40)

    // --- NEW: Close Policy ---
    // This is the key to preventing the dialog from closing on outside clicks or Esc key.
    // It can now ONLY be closed programmatically (e.g., by our button).
    closePolicy: Popup.NoAutoClose

    // --- Animation State ---
    opacity: 0
    scale: 0.9

    // --- Animations ---
    Behavior on opacity { NumberAnimation { duration: 200; easing.type: Easing.OutQuad } }
    Behavior on scale { NumberAnimation { duration: 200; easing.type: Easing.OutBack } }

    // --- Custom Close Function ---
    // We create our own function to handle the closing animation.
    function closeWithAnimation() {
        // 1. Start the closing animation
        scale = 0.9
        opacity = 0
        // 2. Use a timer to call the actual close() after the animation is done
        closeTimer.start()
    }

    // When the component is ready, trigger the "open" animation
    Component.onCompleted: {
        scale = 1.0
        opacity = 1.0
    }

    Timer {
        id: closeTimer
        interval: 200 // Must match the animation duration
        onTriggered: {
            // This is the only place where the dialog is now told to actually close.
            messageDialog.close();
        }
    }

    // --- Custom Visuals ---
    background: Rectangle {
        id: backgroundRect
        color: "#3a4150"
        radius: 8
        border.color: "#16a086"
        border.width: 1
    }

    // --- FIXED: Drop Shadow ---
    DropShadow {
        // REMOVED: anchors.fill - it's not needed and was causing the error.
        // The 'source' property is sufficient.
        source: backgroundRect
        radius: 15
        samples: 25
        color: "#90000000"
        verticalOffset: 4
    }

    header: Rectangle {
        color: "transparent"
        height: 45

        Label {
            text: dialogTitle
            font.bold: true
            font.pointSize: 12
            color: "#ffffff"
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: 20
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

        Button {
            text: qsTr("OK")
            // UPDATED: The button now calls our custom animation function
            // instead of accept().
            onClicked: messageDialog.closeWithAnimation()

            flat: true
            background: Rectangle {
                color: parent.down ? "#138a74" : "#16a086"
                radius: 4
                border.color: "#13b899"
                border.width: 1
            }
            contentItem: Text {
                text: parent.text
                color: "white"
                font: parent.font
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVenter
            }
        }
    }

    onClosed: destroy()
}