import QtQuick
import QtQuick.Controls
import "../controls"
import QtQuick.Layouts

Item {
    Rectangle {
        id: mainContainer
        color: "#2c313c"
        anchors.fill: parent

        property real rowHeight: 30
        property real columnSpacing: 12 // This will now be our fixed gap size

        Rectangle {
            id: groupBox
            radius: 4
            border.color: "#16a086"
            border.width: 1
            color: "transparent"
            anchors {
                fill: parent
                topMargin: 25
                leftMargin: parent.width * 0.1
                rightMargin: parent.width * 0.1
                bottomMargin: 25
            }

            Rectangle {
                color: "#2c313c"
                width: groupBoxTitle.width + 10
                height: groupBoxTitle.height
                x: 15
                y: -groupBoxTitle.height / 2
                Text {
                    id: groupBoxTitle
                    anchors.centerIn: parent
                    text: qsTr("Prehľad Informácií")
                    color: "#c1f6ec"
                    font.pointSize: 12
                }
            }

            ColumnLayout {
                id: columnLayout
                anchors {
                    fill: parent
                    topMargin: 25
                    leftMargin: 20
                    rightMargin: 20
                    bottomMargin: 20
                }
                spacing: mainContainer.columnSpacing // Use the fixed spacing

                // --- User Info ---
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Vaše meno:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    Text { text: qsTr(backend.username); font.pixelSize: 16; font.bold: true; color: "#13b899"; Layout.alignment: Qt.AlignVCenter }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Vaše ID:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    Text { text: backend.rust_id; font.pixelSize: 16; font.bold: true; color: "#13b899"; Layout.alignment: Qt.AlignVCenter }
                }

                // --- Statuses ---
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Aplikácia MacrosoftConnectQuickSupport:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    StatusIndicator { size: 20; status: backend.app_installation_status; Layout.alignment: Qt.AlignVCenter }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Služba MacrosoftConnectQuickSupport:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    StatusIndicator { size: 20; status: backend.app_service_status; Layout.alignment: Qt.AlignVCenter }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Stav Povolenia:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    StatusIndicator { size: 20; status: backend.permission_status; Layout.alignment: Qt.AlignVCenter }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Stav WebSocketu:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    StatusIndicator { size: 20; status: backend.app_websocket_status; Layout.alignment: Qt.AlignVCenter }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Aplikácia OBS:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    StatusIndicator { size: 20; status: backend.obs_installation_status; Layout.alignment: Qt.AlignVCenter }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Stav nahrávania:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    StatusIndicator { size: 20; status: backend.recording_status; Layout.alignment: Qt.AlignVCenter }
                }

                // This spacer will take up all the extra vertical space
                Item {
                    Layout.fillHeight: true
                }
            }
        }
    }
}