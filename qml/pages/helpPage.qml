import QtQuick
import QtQuick.Controls
import "../controls"
import QtQuick.Layouts

Item {
    Rectangle {
        id: rectangle
        color: "#2c313c"
        anchors.fill: parent

        Rectangle {
            id: rectangleVisible
            color: "#1d2128"
            radius: 4
            anchors.fill: parent
            anchors.margins: 20

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 15
                spacing: 5

                Label {
                    id: labelTextName
                    color: "#c3cbdd"
                    text: qsTr("Pomoc a Licencia")
                    Layout.alignment: Qt.AlignHCenter
                    font.pointSize: 14
                    font.bold: true
                }

                Label {
                    id: labelDate
                    color: "#55aaff"
                    text: qsTr("GNU GENERAL PUBLIC LICENSE - Version 3, 29 June 2007")
                    Layout.alignment: Qt.AlignHCenter
                    font.pointSize: 10
                }

                ScrollView {
                    id: scrollView
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true

                    TextArea {
                        id: textHome
                        readOnly: true
                        wrapMode: Text.WordWrap
                        color: "#a9b2c8"
                        font.pointSize: 10
                        textFormat: Text.RichText
                        background: Rectangle { color: "transparent" }
                        text: "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\np, li { white-space: pre-wrap; }\n</style></head><body style=\" font-family:'Segoe UI'; font-size:10pt; font-weight:400; font-style:normal;\">\n<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Copyright (c) 2025 <span style=\" font-weight:600;\">Macrosoft s.r.o</span></p>\n<p style=\"-qt-paragraph-type:empty; margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600;\"><br /></p>\n<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#55aaff;\">Attention</span>: This application is provided under the terms of the GNU GPLv3. By using this software, you agree to be bound by its terms. The license provides you with freedoms to use, share, and modify the software, but also comes with certain obligations, such as providing the source code of modified versions.</p>\n<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">For full license details, please refer to the official GNU GPLv3 documentation. This software is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.</p></body></html>"
                    }
                }
            }
        }
    }
}