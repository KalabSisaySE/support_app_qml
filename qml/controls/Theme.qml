pragma Singleton

import QtQuick

QtObject {
    // Surfaces
    readonly property color background: "#2c313c"
    readonly property color backgroundAlt: "#282c34"
    readonly property color surface: "#1c1d20"
    readonly property color surfaceHover: "#23272E"
    readonly property color logBackground: "#171917"
    readonly property color dialogSurface: "#3a4150"
    readonly property color border: "#383e4c"

    // Accents
    readonly property color accent: "#16a086"
    readonly property color accentButton: "#35b59d"
    readonly property color accentMenu: "#35b8a0"
    readonly property color accentPink: "#ff007f"

    // Text
    readonly property color textPrimary: "#ffffff"
    readonly property color textMuted: "#c3cbdd"
    readonly property color textDim: "#5f6a82"
    readonly property color textDisabled: "#aaa"
    readonly property color textSoft: "#e0e0e0"

    // Feedback
    readonly property color disabled: "#555"
    readonly property color track: "#333"
    readonly property color danger: "#c0392b"
    readonly property color error: "#e74c3c"
    readonly property color success: "#2ecc71"
    readonly property color warning: "#f39c12"
    readonly property color switchOff: "#777"
    readonly property color switchOffBorder: "#666"
    readonly property color overlay: "#80000000"
    readonly property color overlayStrong: "#90000000"

    // Geometry
    readonly property int radiusSmall: 3
    readonly property int radiusMedium: 10
}
