import QtQuick
import QtQuick.Controls
import "../controls"
import QtQuick.Layouts

Item {

    function updateButtonStates() {
        // Logic from your onAppInstallationStatusChanged handler
        macrosoftQuickSupportButton.text = (backend.app_installation_status === "enabled") ? "Odinštalovať" : "Inštalovať";
        macrosoftQuickSupportButton.colorDefault = (backend.app_installation_status === "enabled") ? "#c0392b" : "#35b59d";

        // Logic from your onAppServiceStatusChanged handler
        startServiceButton.text = (backend.app_service_status === "enabled") ? "Zastaviť službu" : "Spustiť službu";
        startServiceButton.colorDefault = (backend.app_service_status === "enabled") ? "#c0392b" : "#35b59d";
    }

    Connections {
        target: backend

        function onAppInstallationStatusChanged(status) {
            updateButtonStates()
        }

        function onAppServiceStatusChanged(status) {
            updateButtonStates()
        }
    }

    Component.onCompleted: {
        updateButtonStates()
    }

    Rectangle {
        id: mainContainer
        color: "#2c313c"
        anchors.fill: parent

        property real rowHeight: 30
        property real columnSpacing: 15 // This will now be our fixed gap size

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
                    text: qsTr("Inštalácia a Spustenie")
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

                // --- Top Group: Statuses ---
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label {
                        text: qsTr("Aplikácia MacrosoftConnectQuickSupport:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter
                    }
                    Item {
                        Layout.fillWidth: true
                    }
                    StatusIndicator {
                        id:
                            appIndicator; size: 20; status: backend.app_installation_status; Layout.alignment: Qt.AlignVCenter; }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label {
                        text: qsTr("Služba MacrosoftConnectQuickSupport:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter
                    }
                    Item {
                        Layout.fillWidth: true
                    }
                    StatusIndicator {
                        id:
                            serviceIndicator; size: 20; status: backend.app_service_status; Layout.alignment: Qt.AlignVCenter; }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label {
                        text: qsTr("Vaše ID:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter
                    }
                    Item {
                        Layout.fillWidth: true
                    }
                    Text {
                        text: backend.rust_id; Layout.alignment: Qt.AlignRight | Qt.AlignVCenter; font.pixelSize: 16; font.italic: true; font.bold: true; color: "#13b899"; rightPadding: 10
                    }
                }

                // --- Bottom Group: Buttons ---
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label {
                        text: qsTr("Aplikácia Macrosoft QuickSupport:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter
                    }
                    Item {
                        Layout.fillWidth: true
                    }
                    CustomButton {
                        id:
                            macrosoftQuickSupportButton; text: qsTr("Inštalovať"); Layout.preferredWidth: 170; Layout.preferredHeight: 28; enabled: backend.is_app_install_btn_enabled; onClicked: backend.install_or_uninstall()
                    }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label {
                        text: "Spustiť Aplikáciu:"; font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter
                    }
                    Item {
                        Layout.fillWidth: true
                    }
                    CustomButton {
                        id:
                            startAppButton; text: "Spustiť MacrosoftQuickSupport"; Layout.preferredWidth: 170; Layout.preferredHeight: 28; enabled: backend.is_app_start_btn_enabled; onClicked: backend.start_app()
                    }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label {
                        text: "Služba:"; font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter
                    }
                    Item {
                        Layout.fillWidth: true
                    }
                    CustomButton {
                        id:
                            startServiceButton; text: "Spustiť službu"; Layout.preferredWidth: 170; Layout.preferredHeight: 28; enabled: backend.is_app_service_btn_enabled; onClicked: backend.toggle_service()
                    }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label {
                        text: "Získať ID pre prístup:"; font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter
                    }
                    Item {
                        Layout.fillWidth: true
                    }
                    CustomButton {
                        id:
                            getRustIdButton; text: "Získať ID"; Layout.preferredWidth: 170; Layout.preferredHeight: 28; enabled: backend.is_app_rust_id_btn_enabled; onClicked: backend.get_rustid()
                    }
                }

                 // NEW: One Click Setup Button
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight + 10 // A bit more space for emphasis
                    Label { text: qsTr("Kompletné Nastavenie:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    CustomButton {
                        id: oneClickSetupButton
                        text: qsTr("Spustiť Inštaláciu na 1-Klik")
                        Layout.preferredWidth: 170
                        Layout.preferredHeight: 32
                        colorDefault: "#27ae60" // A distinct green color
                        enabled: backend.is_app_install_btn_enabled // Reuse the same enabled logic for now
                        onClicked: backend.one_click_setup()
                    }
                }

                // This spacer will take up all the extra vertical space
                Item {
                    Layout.fillHeight: true
                }
            }
        }
    }

}