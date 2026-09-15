import QtQuick
import QtQuick.Controls
Item { property bool running:false; visible:running; BusyIndicator{anchors.centerIn:parent;running:parent.running} }
