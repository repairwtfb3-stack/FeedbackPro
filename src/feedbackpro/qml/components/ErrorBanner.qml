import QtQuick
import QtQuick.Controls
Rectangle { property string message:""; visible: message.length>0; color:"#FFECEC"; radius:6; height:44; Label{anchors.centerIn:parent;text:message;color:"#9A1B1B"} }
