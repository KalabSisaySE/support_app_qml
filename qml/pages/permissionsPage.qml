import QtQuick
import QtQuick.Controls
import "../controls" // Assuming this path is correct for your project
import QtQuick.Layouts

Item {
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
                    text: qsTr("Povolenia")
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

                // Property to control the visibility of the collapsible section.
                // It is correctly set to false, so it will be hidden by default.
                property bool detailsVisible: false

                // --- One Click Setup Button ---
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
                        // Assuming a dummy property for demonstration if backend is not available
                        enabled: typeof backend !== 'undefined' ? backend.is_app_install_btn_enabled : true
                        onClicked: if (typeof backend !== 'undefined') backend.one_click_setup()
                    }
                }

                // --- Toggle Button Row ---
                RowLayout {
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignHCenter

                    CustomButton {
                        id: toggleDetailsButton
                        text: columnLayout.detailsVisible ? qsTr("Skryť Detaily ▲") : qsTr("Zobraziť Detaily ▼")
                        Layout.preferredWidth: 170
                        Layout.preferredHeight: 32
                        colorDefault: "#3498db"
                        onClicked: columnLayout.detailsVisible = !columnLayout.detailsVisible
                    }
                }

                // --- FIX: Collapsible Container Wrapper ---
                // This Item acts as a container for the collapsible content. We will animate
                // its Layout.preferredHeight, which works smoothly inside a ColumnLayout.
                Item {
                    id: collapsibleContainer
                    Layout.fillWidth: true
                    // The container's height is bound to the content's implicitHeight when visible
                    Layout.preferredHeight: columnLayout.detailsVisible ? collapsibleContent.implicitHeight : 0
                    clip: true // Ensure content doesn't draw outside the animated bounds

                    // This Behavior creates the smooth transition effect on the correct property
                    Behavior on Layout.preferredHeight {
                        NumberAnimation {
                            duration: 300
                            easing.type: Easing.InOutQuad
                        }
                    }

                    // --- The actual content is now inside the container ---
                    ColumnLayout {
                        id: collapsibleContent
                        // Use anchors to fill the wrapper item
                        anchors.fill: parent
                        // --- FIX: Hide content when collapsed for performance ---
                        // This prevents the items from receiving mouse events or taking up
                        // resources when they are not visible.
                        visible: collapsibleContainer.Layout.preferredHeight > 0

                        // --- Top Group: Status (Now inside collapsible area) ---
                        RowLayout {
                            Layout.fillWidth: true
                            Layout.preferredHeight: mainContainer.rowHeight
                            Label { text: qsTr("Stav Povolenia:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                            Item { Layout.fillWidth: true }
                            // Assuming StatusIndicator is a custom component
                            // StatusIndicator { size: 20; status: typeof backend !== 'undefined' ? backend.permission_status : 0; Layout.alignment: Qt.AlignVCenter;}
                        }

                        // --- Bottom Group: Buttons (Now inside collapsible area) ---
                        RowLayout {
                            Layout.fillWidth: true
                            Layout.preferredHeight: mainContainer.rowHeight
                            Label { text: qsTr("Povoliť prístup k mikrofónu:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                            Item { Layout.fillWidth: true }
                            CustomButton { text: qsTr("Povoliť len Mikrofón"); Layout.preferredWidth: 170; Layout.preferredHeight: 28; enabled: typeof backend !== 'undefined' ? backend.is_enable_microphone_only_btn_enabled : true; onClicked: if (typeof backend !== 'undefined') backend.enable_microphone_only() }
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            Layout.preferredHeight: mainContainer.rowHeight
                            Label { text: qsTr("Povoliť mikrofón a kameru:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                            Item { Layout.fillWidth: true }
                            CustomButton { text: qsTr("Povoliť všetko"); Layout.preferredWidth: 170; Layout.preferredHeight: 28; enabled: typeof backend !== 'undefined' ? backend.is_enable_microphone_and_camera_btn_enabled : true; onClicked: if (typeof backend !== 'undefined') backend.enable_microphone_and_camera() }
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            Layout.preferredHeight: mainContainer.rowHeight
                            Label { text: qsTr("Otvoriť stránku v prehliadači:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                            Item { Layout.fillWidth: true }
                            CustomButton { text: qsTr("Otvoriť webstránku"); Layout.preferredWidth: 170; Layout.preferredHeight: 28; enabled: typeof backend !== 'undefined' ? backend.is_open_browser_btn_enabled : true; onClicked: if (typeof backend !== 'undefined') backend.open_webpage() }
                        }
                    } // End of collapsibleContent
                } // End of collapsibleContainer

                // This spacer will take up all the extra vertical space
                Item {
                    Layout.fillHeight: true
                }
            }
        }
    }
}