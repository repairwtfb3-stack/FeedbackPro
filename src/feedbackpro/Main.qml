import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    width: 1440; height: 900; visible: true; title: "FeedbackPro"; color: "#F5F7FA"
    property int page: 0
    property var names: ["S01 Дашборд","S02 Отзывы","S03 Карточка отзыва","S04 Импорт","S05 Решения","S06 Карточка решения","S07 Контроль","S08 Аналитика","S09 Справочники","S10 Настройки"]
    RowLayout {
        anchors.fill: parent; spacing: 0
        Rectangle {
            Layout.preferredWidth: 250; Layout.fillHeight: true; color: "#172033"
            ColumnLayout {
                anchors.fill: parent; anchors.margins: 18; spacing: 8
                Label { text: "FeedbackPro"; color: "white"; font.pixelSize: 24; font.bold: true; Layout.bottomMargin: 12 }
                Repeater { model: root.names; delegate: Button { Layout.fillWidth: true; text: modelData; flat: true; highlighted: root.page===index; onClicked: root.page=index } }
                Item { Layout.fillHeight: true }
                Label { text: backend.message; color: "#B8C4D9"; wrapMode: Text.Wrap; Layout.fillWidth: true }
            }
        }
        StackLayout {
            Layout.fillWidth: true; Layout.fillHeight: true; currentIndex: root.page
            Item { // S01
                ColumnLayout { anchors.fill: parent; anchors.margins: 28
                    Label { text: "Дашборд"; font.pixelSize: 30; font.bold: true }
                    Label { text: "Фактические KPI локального корпуса"; color: "#657086" }
                    Flow { Layout.fillWidth: true; spacing: 12
                        Repeater { model: { try { var d=JSON.parse(backend.dashboardJson); return [["Всего",d.total_reviews],["Проанализировано",d.analyzed_reviews],["Негативных",d.negative_reviews],["Критических",d.critical_reviews],["Решений",d.decision_count],["В контроле",d.open_controls]] } catch(e) { return [] } }
                            delegate: Rectangle { width:190; height:105; radius:10; color:"white"; border.color:"#E1E6EE"; Column { anchors.centerIn:parent; Label{text:modelData[0];color:"#657086"} Label{text:modelData[1];font.pixelSize:28;font.bold:true} } }
                        }
                    }
                    Button { text: "Повторно проанализировать всё"; onClicked: backend.analyzeAll() }
                    Item { Layout.fillHeight: true }
                }
            }
            Item { // S02
                property var rows: { try { return JSON.parse(backend.reviewsJson) } catch(e) { return [] } }
                ColumnLayout { anchors.fill:parent; anchors.margins:28
                    Label { text:"Отзывы"; font.pixelSize:30; font.bold:true }
                    ListView { Layout.fillWidth:true; Layout.fillHeight:true; spacing:8; model:parent.parent.rows; delegate: Rectangle { width:ListView.view.width; height:86; radius:8; color:"white"; border.color:"#E1E6EE"; Column { anchors.fill:parent; anchors.margins:10; Label{text:"#"+modelData.id+" • "+modelData.source; font.bold:true} Label{width:parent.width;text:modelData.text;elide:Text.ElideRight} Label{width:parent.width;color:"#657086";text:"sentiment: "+(modelData.sentiment||"—")+" • criticality: "+(modelData.criticality||"—")+" • "+(modelData.aspects||[]).join(", ");elide:Text.ElideRight} } } }
                }
            }
            Item { // S03
                ColumnLayout { anchors.fill:parent; anchors.margins:28
                    Label{text:"Карточка отзыва";font.pixelSize:30;font.bold:true}
                    Rectangle{Layout.fillWidth:true;Layout.fillHeight:true;radius:10;color:"white";border.color:"#E1E6EE";Label{anchors.centerIn:parent;text:"Review → sentiment + aspects + criticality → Decision"}}
                }
            }
            Item { // S04
                ColumnLayout { anchors.fill:parent; anchors.margins:28
                    Label{text:"Импорт";font.pixelSize:30;font.bold:true}
                    Label{text:"CSV/XLSX → нормализация → dedup → анализ";color:"#657086"}
                    Rectangle{Layout.fillWidth:true;height:130;radius:10;color:"white";border.color:"#E1E6EE";Column{anchors.centerIn:parent;spacing:8;Label{text:"Импорт выполняется функциональным слоем core/CLI"}Label{text:"feedbackpro --db feedbackpro.db import <файл.csv|xlsx>";font.family:"monospace"}}}
                    Item{Layout.fillHeight:true}
                }
            }
            Item { // S05
                property var rows:{try{return JSON.parse(backend.decisionsJson)}catch(e){return[]}}
                ColumnLayout { anchors.fill:parent; anchors.margins:28
                    Label{text:"Решения";font.pixelSize:30;font.bold:true}
                    GridLayout{columns:4;Layout.fillWidth:true
                        TextField{id:dt;placeholderText:"Название";Layout.columnSpan:2;Layout.fillWidth:true} TextField{id:dr;placeholderText:"ID отзыва";validator:IntValidator{bottom:1}} ComboBox{id:dp;model:["low","medium","high","critical"]}
                        TextField{id:dd;placeholderText:"Описание";Layout.columnSpan:2;Layout.fillWidth:true} TextField{id:due;placeholderText:"YYYY-MM-DD"} Button{text:"Создать";onClicked:backend.createDecision(dt.text,dd.text,dp.currentText,parseInt(dr.text),due.text)}
                    }
                    ListView{Layout.fillWidth:true;Layout.fillHeight:true;model:parent.parent.rows;spacing:6;delegate:Rectangle{width:ListView.view.width;height:62;color:"white";border.color:"#E1E6EE";RowLayout{anchors.fill:parent;anchors.margins:10;Label{text:"#"+modelData.id;font.bold:true}Label{text:modelData.title;Layout.fillWidth:true}Label{text:modelData.priority+" / "+modelData.status}}}}
                }
            }
            Item { // S06
                ColumnLayout{anchors.fill:parent;anchors.margins:28;Label{text:"Карточка решения";font.pixelSize:30;font.bold:true}Rectangle{Layout.fillWidth:true;Layout.fillHeight:true;radius:10;color:"white";border.color:"#E1E6EE";Label{anchors.centerIn:parent;text:"Decision → связанные Reviews → ControlItem"}}}
            }
            Item { // S07
                property var rows:{try{return JSON.parse(backend.controlsJson)}catch(e){return[]}}
                ColumnLayout{anchors.fill:parent;anchors.margins:28
                    Label{text:"Контроль";font.pixelSize:30;font.bold:true}
                    RowLayout{TextField{id:cid;placeholderText:"ID решения";validator:IntValidator{bottom:1}}ComboBox{id:cs;model:["planned","in_progress","completed","verified"]}TextField{id:cdue;placeholderText:"YYYY-MM-DD"}TextField{id:co;placeholderText:"Результат";Layout.fillWidth:true}Button{text:"Сохранить";onClicked:backend.setControl(parseInt(cid.text),cs.currentText,cdue.text,co.text)}}
                    ListView{Layout.fillWidth:true;Layout.fillHeight:true;model:parent.parent.rows;delegate:Rectangle{width:ListView.view.width;height:60;color:"white";border.color:"#E1E6EE";RowLayout{anchors.fill:parent;anchors.margins:10;Label{text:"#"+modelData.id+" / решение #"+modelData.decision_id;font.bold:true}Label{text:modelData.decision_title;Layout.fillWidth:true}Label{text:modelData.status}}}}
                }
            }
            Item { // S08
                ColumnLayout{anchors.fill:parent;anchors.margins:28;Label{text:"Аналитика";font.pixelSize:30;font.bold:true}Label{text:"Агрегаты строятся только по фактическим данным; BEFORE/AFTER до апробации не подставляются.";wrapMode:Text.Wrap;Layout.fillWidth:true}Rectangle{Layout.fillWidth:true;height:130;radius:10;color:"white";border.color:"#E1E6EE";Column{anchors.centerIn:parent;spacing:8;Label{text:"Экспорт отчёта:"}Label{text:"feedbackpro --db feedbackpro.db report feedbackpro_report.md";font.family:"monospace"}}}Item{Layout.fillHeight:true}}
            }
            Item { // S09
                property var rows:{try{return JSON.parse(backend.topicsJson)}catch(e){return[]}}
                ColumnLayout{anchors.fill:parent;anchors.margins:28;Label{text:"Справочники";font.pixelSize:30;font.bold:true}RowLayout{TextField{id:tc;placeholderText:"Код"}TextField{id:tt;placeholderText:"Название";Layout.fillWidth:true}CheckBox{id:ta;text:"Активна";checked:true}Button{text:"Сохранить";onClicked:backend.setTopic(tc.text,tt.text,ta.checked)}}ListView{Layout.fillWidth:true;Layout.fillHeight:true;model:parent.parent.rows;delegate:Rectangle{width:ListView.view.width;height:50;color:"white";border.color:"#E1E6EE";RowLayout{anchors.fill:parent;anchors.margins:9;Label{text:modelData.code;font.bold:true;Layout.preferredWidth:150}Label{text:modelData.title;Layout.fillWidth:true}Label{text:modelData.active?"активна":"отключена"}}}}}
            }
            Item { // S10
                ColumnLayout{anchors.fill:parent;anchors.margins:28;Label{text:"Настройки";font.pixelSize:30;font.bold:true}RowLayout{TextField{id:sk;text:"organization_name";placeholderText:"Ключ"}TextField{id:sv;placeholderText:"Значение";Layout.fillWidth:true}Button{text:"Сохранить";onClicked:backend.setSetting(sk.text,sv.text)}}Rectangle{Layout.fillWidth:true;Layout.fillHeight:true;radius:10;color:"white";border.color:"#E1E6EE";Column{anchors.centerIn:parent;spacing:8;Label{text:"Offline-first"}Label{text:"SQLite"}Label{text:"Analysis version: a2-rules-1.0"}}}}
            }
        }
    }
}
