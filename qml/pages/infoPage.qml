import QtQuick
import QtQuick.Controls
import "../controls"
import QtQuick.Layouts

Item {
    Rectangle {
        id: mainContainer
        color: Theme.background
        anchors.fill: parent

        property real rowHeight: 30
        property real columnSpacing: 12 // This will now be our fixed gap size

        Rectangle {
            id: groupBox
            radius: 4
            border.color: Theme.accent
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
                color: Theme.background
                width: groupBoxTitle.width + 10
                height: groupBoxTitle.height
                x: 15
                y: -groupBoxTitle.height / 2
                Text {
                    id: groupBoxTitle
                    anchors.centerIn: parent
                    text: qsTr("Prehľad Informácií")
                    color: Theme.accentSoft
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
                    Label { text: qsTr("Aktualizovať účet:"); font.pointSize: 11; color: Theme.textPrimary; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    CustomButton { text: qsTr("Zmeniť účet / Prihlásiť sa"); Layout.preferredWidth: 170; Layout.preferredHeight: 28; enabled: backend.is_change_account_btn_enabled; onClicked: backend.change_account() }
                    visible: backend.is_user_lectoure
                }

                // --- User Info ---
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Vaše meno:"); font.pointSize: 11; color: Theme.textPrimary; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    Text { text: qsTr(backend.username); font.pixelSize: 16; font.bold: true; color: Theme.valueText; Layout.alignment: Qt.AlignVCenter }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Vaše ID:"); font.pointSize: 11; color: Theme.textPrimary; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    Text { text: backend.rust_id; font.pixelSize: 16; font.bold: true; color: Theme.valueText; Layout.alignment: Qt.AlignVCenter }
                    CustomButton { text: qsTr("Kopírovať ID"); Layout.preferredWidth: 110; Layout.preferredHeight: 28; onClicked: backend.copy_rust_id() }
                }

                // --- Statuses ---
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Aplikácia MacrosoftConnectQuickSupport:"); font.pointSize: 11; color: Theme.textPrimary; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    StatusIndicator { size: 20; status: backend.app_installation_status; Layout.alignment: Qt.AlignVCenter }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Služba MacrosoftConnectQuickSupport:"); font.pointSize: 11; color: Theme.textPrimary; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    StatusIndicator { size: 20; status: backend.app_service_status; Layout.alignment: Qt.AlignVCenter }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Stav Povolenia:"); font.pointSize: 11; color: Theme.textPrimary; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    StatusIndicator { size: 20; status: backend.permission_status; Layout.alignment: Qt.AlignVCenter }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Stav WebSocketu:"); font.pointSize: 11; color: Theme.textPrimary; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    StatusIndicator { size: 20; status: backend.app_websocket_status; Layout.alignment: Qt.AlignVCenter }
                    visible: backend.is_user_lectoure

                }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Aplikácia OBS:"); font.pointSize: 11; color: Theme.textPrimary; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    StatusIndicator { size: 20; status: backend.obs_installation_status; Layout.alignment: Qt.AlignVCenter }
                    visible: backend.is_user_lectoure

                }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Stav nahrávania:"); font.pointSize: 11; color: Theme.textPrimary; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    StatusIndicator { size: 20; status: backend.recording_status; Layout.alignment: Qt.AlignVCenter }
                    visible: backend.is_user_lectoure

                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Otvoriť stránku v prehliadači:"); font.pointSize: 11; color: Theme.textPrimary; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    CustomButton { text: qsTr("Otvoriť webstránku"); Layout.preferredWidth: 170; Layout.preferredHeight: 28; enabled: backend.is_open_browser_btn_enabled; onClicked: backend.open_webpage() }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Pre-flight:"); font.pointSize: 11; color: Theme.textPrimary; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    CustomButton { text: qsTr("Skontrolovať pripravenosť"); Layout.preferredWidth: 210; Layout.preferredHeight: 28; onClicked: backend.run_preflight() }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Podpora:"); font.pointSize: 11; color: Theme.textPrimary; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    CustomButton { text: qsTr("Vytvoriť diagnostický balík"); Layout.preferredWidth: 210; Layout.preferredHeight: 28; onClicked: backend.create_diagnostics_bundle() }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Vzhľad:"); font.pointSize: 11; color: Theme.textPrimary; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    CustomButton { text: qsTr("Prepnúť tému"); Layout.preferredWidth: 210; Layout.preferredHeight: 28; onClicked: backend.toggle_theme() }
                }

                // This spacer will take up all the extra vertical space
                Item {
                    Layout.fillHeight: true
                }
            }
        }
    }
}