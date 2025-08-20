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
    property bool isClosing: false

    // --- Core Settings ---
    anchors.centerIn: Overlay.overlay
    modal: true
    focus: true
    padding: 0
    width: Math.min(400, Overlay.overlay.width - 40)

    // --- Animation State ---
    opacity: 0
    scale: 0.9

    // --- Animations ---
    Behavior on opacity { NumberAnimation { duration: 200; easing.type: Easing.OutQuad } }
    Behavior on scale { NumberAnimation { duration: 200; easing.type: Easing.OutBack } }

    Component.onCompleted: {
        scale = 1.0
        opacity = 1.0
    }

    // --- THE FIX: Using a 'Connections' element ---
    // This is a more robust way to connect to a signal on the component itself,
    // avoiding the "non-existent property" error.
    Connections {
        target: messageDialog // Explicitly target the dialog

        // Use the function syntax for the signal handler
        function onClosing(close) {
            if (!isClosing) {
                // 1. Prevent the dialog from closing right now
                close.accepted = false;

                // 2. Set our flag to true
                isClosing = true;

                // 3. Start the closing animation
                scale = 0.9
                opacity = 0

                // 4. Use a timer to call the actual close() after the animation is done
                closeTimer.start()
            }
        }
    }

    Timer {
        id: closeTimer
        interval: 200 // Must match the animation duration
        onTriggered: {
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

    DropShadow {
        anchors.fill: backgroundRect
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
            onClicked: messageDialog.accept() // accept() will trigger the 'onClosing' handler

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
                verticalAlignment: Text.AlignVCenter
            }
        }
    }

    onClosed: destroy()
}