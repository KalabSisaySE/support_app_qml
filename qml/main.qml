import QtQuick
import QtQuick.Window
import QtQuick.Controls
import Qt5Compat.GraphicalEffects
import "controls"
import QtQuick.Dialogs
import QtQuick.Layouts
import Qt.labs.settings 1.0

Window {
    id: mainWindow
    width: 920
    height: 650
    minimumWidth: 800
    minimumHeight: 600
    visible: true
    color: "#00000000"
    title: qsTr("Macrosoft Support")

    // Persisted window/page state
    Settings {
        id: appSettings
        category: "window"
        property int windowWidth: 920
        property int windowHeight: 650
        property string currentPage: "pages/infoPage.qml"
    }

    onWidthChanged: appSettings.windowWidth = width
    onHeightChanged: appSettings.windowHeight = height

    Component.onCompleted: {
        width = Math.max(minimumWidth, appSettings.windowWidth)
        height = Math.max(minimumHeight, appSettings.windowHeight)
        Theme.setDark(backend.is_dark_theme)
    }

    function setActivePage(page) {
        btnHome.isActiveMenu = page === "pages/infoPage.qml"
        btnServices.isActiveMenu = page === "pages/appPage.qml"
        btnPermissions.isActiveMenu = page === "pages/permissionsPage.qml"
        btnRecording.isActiveMenu = page === "pages/recordingPage.qml"
        btnHelp.isActiveMenu = page === "pages/helpPage.qml"
    }

    function navigate(page) {
        setActivePage(page)
        appSettings.currentPage = page
        stackView.push(Qt.resolvedUrl(page))
    }


    // Remove title bar
    flags: Qt.Window | Qt.FramelessWindowHint

    // Propeties
    property int windowStatus: 0
    property int windowMargin: 10

    // Text Edit Properties
    property alias actualPage: stackView.currentItem

    QtObject {
        id: dialogManager

        // UPDATED: Add the 'isSuccess' parameter
        function showMessage(title, text, isSuccess) {
            var component = Qt.createComponent("controls/MessageDialog.qml");
            if (component.status === Component.Ready) {
                var dialog = component.createObject(mainWindow);
                if (dialog) {
                    dialog.dialogTitle = title;
                    dialog.dialogText = text;
                    // NEW: Pass the success state to the dialog
                    dialog.isSuccess = isSuccess;
                    dialog.open();
                } else {
                    console.error("Error creating dialog object.");
                }
            } else {
                console.error("Error loading dialog component:", component.errorString());
            }
        }
    }

    // --- NEW: Connection to Backend Signal ---
    Connections {
        target: backend
        // UPDATED: Add the 'isSuccess' parameter
        function onShowDialog(title, text, isSuccess) {
            dialogManager.showMessage(title, text, isSuccess);
        }

        function onThemeChanged(isDark) {
            Theme.setDark(isDark);
        }
    }

    // Internal functions
    QtObject{
        id: internal

        function resetResizeBorders(){
            // Resize visibility
            resizeLeft.visible = true
            resizeRight.visible = true
            resizeBottom.visible = true
            resizeWindow.visible = true
        }

        function maximizeRestore(){
            if(windowStatus == 0){
                mainWindow.showMaximized()
                windowStatus = 1
                windowMargin = 0
                // Resize visibility
                resizeLeft.visible = false
                resizeRight.visible = false
                resizeBottom.visible = false
                resizeWindow.visible = false
                btnMaximizeRestore.btnIconSource = "../../images/svg_images/restore_icon.svg"
            }
            else{
                mainWindow.showNormal()
                windowStatus = 0
                windowMargin = 10
                // Resize visibility
                internal.resetResizeBorders()
                btnMaximizeRestore.btnIconSource = "../../images/svg_images/maximize_icon.svg"
            }
        }

        function ifMaximizedWindowRestore(){
            if(windowStatus == 1){
                mainWindow.showNormal()
                windowStatus = 0
                windowMargin = 10
                // Resize visibility
                internal.resetResizeBorders()
                btnMaximizeRestore.btnIconSource = "../../images/svg_images/maximize_icon.svg"
            }
        }

        function restoreMargins(){
            windowStatus = 0
            windowMargin = 10
            // Resize visibility
            internal.resetResizeBorders()
            btnMaximizeRestore.btnIconSource = "../../images/svg_images/maximize_icon.svg"
        }
    }



    Rectangle {
        id: bg
        color: Theme.background
        border.color: Theme.border
        // FIX: Remove the border when maximized to prevent a visible line at the screen edge.
        border.width: windowMargin > 0 ? 1 : 0
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.rightMargin: windowMargin
        anchors.leftMargin: windowMargin
        anchors.bottomMargin: windowMargin
        anchors.topMargin: windowMargin
        z: 1

        Rectangle {
            id: appContainer
            color: "#00000000"
            anchors.fill: parent
            anchors.rightMargin: 1
            anchors.leftMargin: 1
            anchors.bottomMargin: 1
            anchors.topMargin: 1

            Rectangle {
                id: topBar
                height: 50
                color: Theme.surface
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.rightMargin: 0
                anchors.leftMargin: 0
                anchors.topMargin: 0
                z: 2

                Rectangle {
                    id: topBarDescription
                    y: 28
                    height: 22
                    color: Theme.backgroundAlt
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    anchors.rightMargin: 0
                    anchors.leftMargin: 60
                    anchors.bottomMargin: 0

                    Label {
                        id: labelTopInfo
                        color: Theme.textDim
                        text: qsTr("Popis aplikácie")
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        verticalAlignment: Text.AlignVCenter
                        anchors.bottomMargin: 0
                        anchors.rightMargin: 300
                        anchors.topMargin: 0
                        anchors.leftMargin: 10
                        font.pointSize: 9
                    }

                    Label {
                        id: labelRightInfo

                        property string currentTime: ""


                        color: Theme.textDim
                        text: `| ${currentTime}`
                        anchors.left: labelTopInfo.right
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        horizontalAlignment: Text.AlignRight
                        verticalAlignment: Text.AlignVCenter
                        anchors.topMargin: 0
                        anchors.rightMargin: 10
                        anchors.leftMargin: 0
                        anchors.bottomMargin: 0
                        font.pointSize: 9


                        Timer {
                            interval: 1000 // Update every 1 second
                            running: true
                            repeat: true
                            onTriggered: {
                                labelRightInfo.currentTime = Qt.formatDateTime(new Date(), "dd.MM.yyyy - hh:mm:ss")
                            }
                        }

                        Component.onCompleted: {labelRightInfo.currentTime = Qt.formatDateTime(new Date(), "dd.MM.yyyy - hh:mm:ss")}
                    }
                }

                Rectangle {
                    id: titleBar
                    height: 28
                    color: "#00000000"
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.rightMargin: 100
                    anchors.leftMargin: 60
                    anchors.topMargin: 0

                    DragHandler {
                        onActiveChanged: if(active){
                                             mainWindow.startSystemMove()
                                             internal.ifMaximizedWindowRestore()
                                         }
                    }

                    Image {
                        id: iconApp
                        width: 20
                        height: 20
                        anchors.left: parent.left
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        source: "../images/icon.png"
                        anchors.bottomMargin: 0
                        anchors.leftMargin: 5
                        anchors.topMargin: 0
                        fillMode: Image.PreserveAspectFit
                    }

                    Label {
                        id: label
                        color: Theme.textMuted
                        text: qsTr("Macrosoft Support")
                        anchors.left: iconApp.right
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        verticalAlignment: Text.AlignVCenter
                        font.pointSize: 9
                        anchors.leftMargin: 5
                    }
                }

                Row {
                    id: rowBtns
                    height: 28
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.topMargin: 0
                    anchors.rightMargin: 0
                    spacing: 0

                    TopBarButton{
                        id: btnMinimize
                        onClicked: {
                            mainWindow.showMinimized()
                            internal.restoreMargins()
                        }
                    }

                    TopBarButton {
                        id: btnMaximizeRestore
                        btnIconSource: "../../images/svg_images/maximize_icon.svg"
                        onClicked: internal.maximizeRestore()
                    }

                    TopBarButton {
                        id: btnClose
                        btnColorClicked: Theme.accentPink
                        btnIconSource: "../../images/svg_images/close_icon.svg"
                        onClicked: mainWindow.close()
                    }
                }
            }

            Rectangle {
                id: content
                color: "#00000000"
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: topBar.bottom
                anchors.bottom: parent.bottom
                anchors.topMargin: 0
                // FIX: Clip all child content to the bounds of this rectangle.
                // This acts as a master container for the sidebar and main content.
                clip: true

                Rectangle {
                    id: leftMenu
                    width: 60
                    color: Theme.surface
                    anchors.left: parent.left
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    clip: true
                    anchors.topMargin: 0
                    anchors.bottomMargin: 0
                    anchors.leftMargin: 0
                    z: 2

                    PropertyAnimation{
                        id: animationMenu
                        target: leftMenu
                        property: "width"
                        to: if(leftMenu.width === 60) return 230; else return 60
                        duration: 400
                        easing.type: Easing.InOutCubic
                    }

                    Column {
                        id: columnMenus
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        clip: true
                        anchors.rightMargin: 0
                        anchors.leftMargin: 0
                        anchors.bottomMargin: 70
                        anchors.topMargin: 0

                        LeftMenuBtn {
                            id: btnHome
                            width: leftMenu.width
                            text: qsTr("Informácie")
                            isActiveMenu: true
                            onClicked: navigate("pages/infoPage.qml")
                        }

                        LeftMenuBtn {
                            id: btnServices
                            width: leftMenu.width
                            text: qsTr("Služby")

                            btnIconSource: "../../images/svg_images/services.svg"
                            onClicked: navigate("pages/appPage.qml")
                        }

                        LeftMenuBtn {
                            id: btnPermissions
                            width: leftMenu.width
                            text: qsTr("Povolenia")

                            btnIconSource: "../../images/svg_images/permissions.svg"
                            onClicked: navigate("pages/permissionsPage.qml")
                        }

                        LeftMenuBtn {
                            id: btnRecording
                            width: leftMenu.width
                            text: qsTr("Nahrávanie")

                            btnIconSource: "../../images/svg_images/recording.svg"
                            onClicked: navigate("pages/recordingPage.qml")
                            visible: backend.is_user_lectoure
                        }


                    }

                    LeftMenuBtn {
                        id: btnHelp
                        width: leftMenu.width
                        text: qsTr("Pomoc")
                        anchors.bottom: parent.bottom
                        anchors.bottomMargin: 20
                        btnIconSource: "../../images/svg_images/help.svg"
                        onClicked: navigate("pages/helpPage.qml")
                    }
                }

                Rectangle {
                    id: mainContentArea
                    color: "transparent"
                    anchors.left: leftMenu.right
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    z: 1
                    clip: true

                    // Restore the last page (recording is lecturer-only).
                    Component.onCompleted: {
                        var page = appSettings.currentPage
                        if (page === "pages/recordingPage.qml" && !backend.is_user_lectoure) {
                            page = "pages/infoPage.qml"
                        }
                        navigate(page)
                    }

                    // This container holds the pages and the process/log area
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 0

                        StackView {
                            id: stackView
                            Layout.fillWidth: true
                            Layout.fillHeight: true // Takes up remaining space
                            // FIX: Removed initialItem property. We now handle this in onCompleted.
                        }

                        Rectangle {
                            id: processContainer
                            Layout.fillWidth: true
                            // Dynamic height based on switch
                            Layout.preferredHeight: showLogsSwitch.checked ? 140 : 40
                            color: Theme.logBackground

                            Behavior on Layout.preferredHeight {
                                NumberAnimation { duration: 300; easing.type: Easing.InOutQuad }
                            }

                            ColumnLayout {
                                anchors.fill: parent
                                spacing: 5
                                anchors.leftMargin: 10
                                anchors.rightMargin: 10

                                CustomProgressBar {
                                    id: mainProgressBar
                                    Layout.fillWidth: true
                                    Layout.topMargin: 10
                                    Layout.preferredHeight: 15
                                    value: backend.progress
                                }

                                ScrollView {
                                    id: scrollView
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true // Takes remaining space in this container
                                    visible: showLogsSwitch.checked
                                    clip: true
                                    background: Rectangle {
                                        color: Theme.logPanel
                                        radius: 4
                                    }

                                    TextArea {
                                        id: logTextArea
                                        readOnly: true
                                        wrapMode: Text.Wrap
                                        font.family: "Monospace"
                                        font.pointSize: 9
                                        selectByMouse: true
                                        color: Theme.logText
                                        background: Rectangle { color: "transparent" }
                                        leftPadding: 5
                                        rightPadding: 5

                                        onTextChanged: {
                                            Qt.callLater(() => {
                                                if (scrollView.flickableItem) {
                                                    scrollView.flickableItem.contentY =
                                                        Math.max(0, scrollView.flickableItem.contentHeight - scrollView.flickableItem.height)
                                                }
                                            })
                                            const lines = text.split('\n')
                                            if (lines.length > maxLines) {
                                                text = lines.slice(-maxLines).join('\n')
                                            }
                                        }

                                        property int maxLines: 1000
                                    }
                                }
                            }
                        }

                                                Rectangle {
                            id: statusBar
                            Layout.fillWidth: true
                            // Minimized height
                            Layout.preferredHeight: 20
                            color: Theme.backgroundAlt

                            Switch {
                                id: showLogsSwitch
                                anchors.verticalCenter: parent.verticalCenter
                                anchors.left: parent.left
                                anchors.leftMargin: 10

                                text: qsTr("Zobraziť záznamy")
                                checked: false
                                // UPDATED: Matched implicitHeight to the new indicator height
                                implicitHeight: 16
                                padding: 0
                                spacing: 4

                                indicator: Rectangle {
                                    // UPDATED: Reduced indicator size for a more compact look
                                    implicitWidth: 32
                                    implicitHeight: 16
                                    radius: height / 2
                                    color: showLogsSwitch.checked ? Theme.accent : Theme.switchOff
                                    border.color: showLogsSwitch.checked ? Theme.accent : Theme.switchOffBorder
                                    anchors.verticalCenter: parent.verticalCenter

                                    Rectangle {
                                        // UPDATED: Reduced knob size to fit the new indicator
                                        width: 12
                                        height: 12
                                        radius: 6
                                        color: "white"
                                        anchors.verticalCenter: parent.verticalCenter
                                        // The 'x' formula automatically adjusts to the new parent (indicator) and knob sizes
                                        x: showLogsSwitch.checked ? parent.width - width - 2 : 2
                                        Behavior on x { NumberAnimation { duration: 200 } }
                                    }
                                }

                                contentItem: Text {
                                    text: qsTr(showLogsSwitch.text)
                                    color: "white"
                                    verticalAlignment: Text.AlignVCenter
                                    font.pointSize: 9
                                    leftPadding: showLogsSwitch.indicator.width + showLogsSwitch.spacing
                                }

                                background: null
                            }

                            Label {
                                id: copyrightLabel
                                color: Theme.textDim
                                text: qsTr("Autorské práva © 2025 Macrosoft. Všetky práva vyhradené.")
                                anchors.centerIn: parent
                                font.pointSize: 9
                            }

                                                        MouseArea {
                                id: resizeWindow
                                // UPDATED: Set width and height to match the statusBar's dimensions.
                                // This ensures the entire area is clickable and not clipped.
                                width: 20
                                height: 20
                                opacity: 0.5
                                anchors.right: parent.right
                                anchors.bottom: parent.bottom
                                cursorShape: Qt.SizeFDiagCursor

                                DragHandler{
                                    target: null
                                    onActiveChanged: if (active){
                                                         mainWindow.startSystemResize(Qt.RightEdge | Qt.BottomEdge)
                                                     }
                                }

                                Image {
                                    id: resizeImage
                                    // The icon is 16x16, so it fits perfectly inside the 20x20 area.
                                    width: 16
                                    height: 16
                                    anchors.centerIn: parent
                                    source: "../images/svg_images/resize_icon.svg"
                                    sourceSize.height: 16
                                    sourceSize.width: 16
                                    fillMode: Image.PreserveAspectFit
                                }
                            }
                        }
                    }
                }
            }
        }
    }


    DropShadow{
        anchors.fill: bg
        horizontalOffset: 0
        verticalOffset: 0
        radius: 10
        samples: 16
        color: Theme.overlay
        source: bg
        z: 0
    }

    MouseArea {
        id: resizeLeft
        width: 10
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.leftMargin: 0
        anchors.bottomMargin: 10
        anchors.topMargin: 10
        cursorShape: Qt.SizeHorCursor

        DragHandler{
            target: null
            onActiveChanged: if (active) { mainWindow.startSystemResize(Qt.LeftEdge) }
        }
    }

    MouseArea {
        id: resizeRight
        width: 10
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.rightMargin: 0
        anchors.bottomMargin: 10
        anchors.topMargin: 10
        cursorShape: Qt.SizeHorCursor

        DragHandler{
            target: null
            onActiveChanged: if (active) { mainWindow.startSystemResize(Qt.RightEdge) }
        }
    }

    MouseArea {
        id: resizeBottom
        height: 10
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.rightMargin: 10
        anchors.leftMargin: 10
        anchors.bottomMargin: 0
        cursorShape: Qt.SizeVerCursor

        DragHandler{
            target: null
            onActiveChanged: if (active) { mainWindow.startSystemResize(Qt.BottomEdge) }
        }
    }

    Connections{
        target: backend

        function onNewLogAdded(text) {
            logTextArea.append(`(${String(new Date().getHours()).padStart(2, '0')}:${String(new Date().getMinutes()).padStart(2, '0')}): ` + text)
        }
    }
}