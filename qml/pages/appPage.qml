import QtQuick
import QtQuick.Controls
import "../controls" // Assuming this path is correct for your project
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
        property real columnSpacing: 15

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
                spacing: mainContainer.columnSpacing

                // --- NEW: Property to control the dropdown ---
                property bool detailsVisible: false

                 // One Click Setup Button
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight + 10
                    Label { text: qsTr("Kompletné Nastavenie:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    CustomButton {
                        id: oneClickSetupButton
                        text: qsTr("Konfigurácia na 1 klik")
                        Layout.preferredWidth: 170
                        Layout.preferredHeight: 32
                        colorDefault: "#27ae60"
                        enabled: backend.is_app_install_btn_enabled
                        onClicked: backend.one_click_setup()
                    }
                }

                // --- Top Group: Statuses (Always Visible) ---
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Aplikácia MacrosoftConnectQuickSupport:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    StatusIndicator { id: appIndicator; size: 20; status: backend.app_installation_status; Layout.alignment: Qt.AlignVCenter; }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Služba MacrosoftConnectQuickSupport:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    StatusIndicator { id: serviceIndicator; size: 20; status: backend.app_service_status; Layout.alignment: Qt.AlignVCenter; }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Vaše ID:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    Text {
                        text: backend.rust_id; Layout.alignment: Qt.AlignRight | Qt.AlignVCenter; font.pixelSize: 16; font.italic: true; font.bold: true; color: "#13b899"; rightPadding: 10
                    }
                }

                // --- NEW: Toggle Button Row ---
                // This is placed right after the content that should always be visible.
                RowLayout {
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignHCenter

                    CustomButton {
                        id: toggleDetailsButton
                        text: columnLayout.detailsVisible ? qsTr("Skryť Možnosti ▲") : qsTr("Zobraziť Možnosti ▼")
                        Layout.preferredWidth: 170
                        Layout.preferredHeight: 32
                        colorDefault: "#3498db"
                        onClicked: columnLayout.detailsVisible = !columnLayout.detailsVisible
                    }
                }

                // --- NEW: Collapsible Container Wrapper ---
                // This Item will smoothly animate its height to show/hide the content within.
                Item {
                    id: collapsibleContainer
                    Layout.fillWidth: true
                    Layout.preferredHeight: columnLayout.detailsVisible ? collapsibleContent.implicitHeight : 0
                    clip: true // Important for clean animation

                    Behavior on Layout.preferredHeight {
                        NumberAnimation {
                            duration: 300
                            easing.type: Easing.InOutQuad
                        }
                    }

                    // --- NEW: Content is now inside this new layout ---
                    ColumnLayout {
                        id: collapsibleContent
                        anchors.fill: parent
                        spacing: mainContainer.columnSpacing // Keep spacing between the rows
                        visible: collapsibleContainer.Layout.preferredHeight > 0

                        // --- Bottom Group: Buttons (Now inside the collapsible area) ---
                        RowLayout {
                            Layout.fillWidth: true
                            Layout.preferredHeight: mainContainer.rowHeight
                            Label { text: qsTr("Aplikácia Macrosoft QuickSupport:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                            Item { Layout.fillWidth: true }
                            CustomButton {
                                id: macrosoftQuickSupportButton
                                text: qsTr("Inštalovať")
                                Layout.preferredWidth: 170
                                Layout.preferredHeight: 28
                                enabled: backend.is_app_install_btn_enabled
                                onClicked: backend.install_or_uninstall()
                            }
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            Layout.preferredHeight: mainContainer.rowHeight
                            Label { text: "Spustiť Aplikáciu:"; font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                            Item { Layout.fillWidth: true }
                            CustomButton {
                                id: startAppButton
                                text: "Spustiť MacrosoftQuickSupport"
                                Layout.preferredWidth: 170
                                Layout.preferredHeight: 28
                                enabled: backend.is_app_start_btn_enabled
                                onClicked: backend.start_app()
                            }
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            Layout.preferredHeight: mainContainer.rowHeight
                            Label { text: "Služba:"; font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                            Item { Layout.fillWidth: true }
                            CustomButton {
                                id: startServiceButton
                                text: "Spustiť službu"
                                Layout.preferredWidth: 170
                                Layout.preferredHeight: 28
                                enabled: backend.is_app_service_btn_enabled
                                onClicked: backend.toggle_service()
                            }
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            Layout.preferredHeight: mainContainer.rowHeight
                            Label { text: "Získať ID pre prístup:"; font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                            Item { Layout.fillWidth: true }
                            CustomButton {
                                id: getRustIdButton
                                text: "Získať ID"
                                Layout.preferredWidth: 170
                                Layout.preferredHeight: 28
                                enabled: backend.is_app_rust_id_btn_enabled
                                onClicked: backend.get_rustid()
                            }
                        }
                    } // End collapsibleContent
                } // End collapsibleContainer

                // This spacer will take up all the extra vertical space
                Item {
                    Layout.fillHeight: true
                }
            }
        }
    }
}