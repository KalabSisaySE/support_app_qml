pragma Singleton

import QtQuick

QtObject {
    // Active palette (dark by default; setDark() updates these)
    property bool dark: true

    // Surfaces
    property color background: "#2c313c"
    property color backgroundAlt: "#282c34"
    property color surface: "#1c1d20"
    property color surfaceHover: "#23272E"
    property color logBackground: "#171917"
    property color dialogSurface: "#3a4150"
    property color border: "#383e4c"
    property color panelSurface: "#1d2128"

    // Accents
    property color accent: "#16a086"
    property color accentButton: "#35b59d"
    property color accentMenu: "#35b8a0"
    property color accentPink: "#ff007f"
    property color accentSoft: "#c1f6ec"
    property color valueText: "#13b899"
    property color successStrong: "#27ae60"
    property color info: "#3498db"

    // Text
    property color textPrimary: "#ffffff"
    property color textMuted: "#c3cbdd"
    property color textDim: "#5f6a82"
    property color textDisabled: "#aaa"
    property color textSoft: "#e0e0e0"
    property color helpText: "#a9b2c8"

    // Feedback
    property color disabled: "#555"
    property color track: "#333"
    property color logPanel: "#ffffff"
    property color logText: "#333333"
    property color danger: "#c0392b"
    property color error: "#e74c3c"
    property color success: "#2ecc71"
    property color warning: "#f39c12"
    property color switchOff: "#777"
    property color switchOffBorder: "#666"
    property color overlay: "#80000000"
    property color overlayStrong: "#90000000"

    // Geometry
    readonly property int radiusSmall: 3
    readonly property int radiusMedium: 10

    function setDark(value) {
        dark = value
        if (value) {
            background = "#2c313c"
            backgroundAlt = "#282c34"
            surface = "#1c1d20"
            surfaceHover = "#23272E"
            logBackground = "#171917"
            dialogSurface = "#3a4150"
            border = "#383e4c"
            panelSurface = "#1d2128"
            accentSoft = "#c1f6ec"
            valueText = "#13b899"
            textPrimary = "#ffffff"
            textMuted = "#c3cbdd"
            textDim = "#5f6a82"
            textDisabled = "#aaa"
            textSoft = "#e0e0e0"
            helpText = "#a9b2c8"
            disabled = "#555"
            track = "#333"
            logPanel = "#ffffff"
            logText = "#333333"
            switchOff = "#777"
            switchOffBorder = "#666"
        } else {
            background = "#f4f6f8"
            backgroundAlt = "#e9edf2"
            surface = "#ffffff"
            surfaceHover = "#e3e9f0"
            logBackground = "#e9edf2"
            dialogSurface = "#ffffff"
            border = "#d1d2d2"
            panelSurface = "#ffffff"
            accentSoft = "#d8f5ee"
            valueText = "#0f8f77"
            textPrimary = "#1c1e22"
            textMuted = "#3a4150"
            textDim = "#5f6a82"
            textDisabled = "#8a8f98"
            textSoft = "#4a5059"
            helpText = "#3a4150"
            disabled = "#cbd2dc"
            track = "#d8dee6"
            logPanel = "#ffffff"
            logText = "#333333"
            switchOff = "#b0b7c3"
            switchOffBorder = "#9aa3b2"
        }
    }
}
