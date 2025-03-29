import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    title: "WebSocket Client"
    width: 600
    height: 400
    visible: true

    ColumnLayout {
        anchors.fill: parent
        spacing: 10

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true

            TextArea {
                id: logArea
                readOnly: true
                wrapMode: Text.Wrap
            }
        }

        TextField {
            id: messageInput
            Layout.fillWidth: true
            placeholderText: "Type message here..."
            onAccepted: sendButton.clicked()
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Button {
                id: connectButton
                text: websocketHandler.isConnected ? "Disconnect" : "Connect"
                onClicked: websocketHandler.toggleConnection()
            }

            Button {
                id: sendButton
                text: "Send"
                enabled: websocketHandler.isConnected
                onClicked: {
                    websocketHandler.sendMessage(messageInput.text)
                    messageInput.clear()
                }
            }
        }
    }

    Connections {
        target: websocketHandler
        function onMessageReceived(message) {
            logArea.append(message)
        }
        function onErrorOccurred(error) {
            logArea.append(error)
        }
    }
}