import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
Item {
    signal openDrilldown(string kind,string value)
    property var d: { try { return JSON.parse(backend.dashboardJson) } catch(e) { return {} } }
    ColumnLayout { anchors.fill: parent; anchors.margins: 28; spacing: 14
        Label { text: "Дашборд"; font.pixelSize: 30; font.bold: true }
        Label { text: "Фактические показатели локального корпуса"; color: "#657086" }
        Flow { Layout.fillWidth: true; spacing: 12
            Repeater { model: [["Всего",d.total_reviews||0],["Проанализировано",d.analyzed_reviews||0],["Негативных",d.negative_reviews||0],["Критических",d.critical_reviews||0],["Решений",d.decision_count||0],["В контроле",d.open_controls||0]]
                delegate: Rectangle { width:190;height:105;radius:10;color:"white";border.color:"#E1E6EE"; Column{anchors.centerIn:parent;Label{text:modelData[0];color:"#657086"}Label{text:modelData[1];font.pixelSize:28;font.bold:true}} }
            }
        }
        Label { text: "Drill-down доступен из аналитики S08"; color: "#657086" }
        Item { Layout.fillHeight: true }
    }
}
