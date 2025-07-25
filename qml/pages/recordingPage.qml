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
                    text: qsTr("Nahrávanie")
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

                // --- Top Group: Info & Statuses ---
                RowLayout {
                    Layout.fillWidth: true; Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Streamovacia adresa (URL):"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    Text { text: backend.streaming_url; font.pixelSize: 14; font.bold: true; color: "#13b899"; Layout.alignment: Qt.AlignVCenter }
                }
                RowLayout {
                    Layout.fillWidth: true; Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Názov kurzu:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    Text { text: backend.course_name; font.pixelSize: 14; font.bold: true; color: "#13b899"; Layout.alignment: Qt.AlignVCenter }
                }
                RowLayout {
                    Layout.fillWidth: true; Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Aplikácia OBS:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    StatusIndicator { size: 20; status: backend.obs_installation_status; Layout.alignment: Qt.AlignVCenter; Layout.rightMargin: 65 }
                }
                RowLayout {
                    Layout.fillWidth: true; Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("OBS Websocket:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    StatusIndicator { size: 20; status: backend.obs_websocket_status; Layout.alignment: Qt.AlignVCenter; Layout.rightMargin: 65 }
                }
                RowLayout {
                    Layout.fillWidth: true; Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Stav nahrávania:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    StatusIndicator { size: 20; status: backend.recording_status; Layout.alignment: Qt.AlignVCenter; Layout.rightMargin: 65 }
                }

                // --- Bottom Group: Buttons ---
                RowLayout {
                    Layout.fillWidth: true; Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Aplikácia OBS:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    CustomButton { id: obsInstallBtn; text: qsTr("Inštalovať OBS"); Layout.preferredWidth: 170; Layout.preferredHeight: 28; enabled: backend.is_obs_install_btn_enabled; onClicked: backend.install_obs() }
                }
                RowLayout {
                    Layout.fillWidth: true; Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("OBS:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    CustomButton { text: qsTr("Otvoriť OBS"); Layout.preferredWidth: 170; Layout.preferredHeight: 28; enabled: backend.is_open_obs_btn_enabled; onClicked: backend.open_obs() }
                }
                RowLayout {
                    Layout.fillWidth: true; Layout.preferredHeight: mainContainer.rowHeight
                    Label { text: qsTr("Nahrávanie:"); font.pointSize: 11; color: "#ffffff"; Layout.alignment: Qt.AlignVCenter }
                    Item { Layout.fillWidth: true }
                    CustomButton { id: recordingButton; text: qsTr("Spustiť nahrávanie"); Layout.preferredWidth: 170; Layout.preferredHeight: 28; enabled: backend.is_obs_record_btn_enabled; onClicked: backend.toggle_recording() }
                }

                // This spacer will take up all the extra vertical space
                Item {
                    Layout.fillHeight: true
                }
            }
        }
    }

    Connections {
        target: backend
        function onRecordingStatusChanged(status) {
            recordingButton.text = (status === "enabled") ? "Zastaviť nahrávanie" : "Spustiť nahrávanie";
            recordingButton.colorDefault = (status === "enabled") ? "#c0392b" : "#35b59d";
        }
        function onObsInstallationStatusChanged(status) {
            obsInstallBtn.text = (status === "enabled") ? "Odinštalovať OBS" : "Inštalovať OBS";
            obsInstallBtn.colorDefault = (status === "enabled") ? "#c0392b" : "#35b59d";
        }
    }

    Component.onCompleted: {
        onRecordingStatusChanged(backend.recording_status)
        onObsInstallationStatusChanged(backend.obs_installation_status)
    }
}