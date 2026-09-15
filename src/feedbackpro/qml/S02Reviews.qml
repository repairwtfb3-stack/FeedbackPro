import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
Item {
    signal openReview(int id)
    property var rows: []
    function reload(){ var r=backend.searchReviews(JSON.stringify({search:q.text,sentiment:sent.currentText=="all"?null:sent.currentText,criticality:crit.currentText=="all"?null:crit.currentText,unverified:unv.checked,sort:sort.currentText})); try{rows=JSON.parse(r)}catch(e){rows=[]} }
    Component.onCompleted: reload()
    ColumnLayout { anchors.fill:parent; anchors.margins:28; spacing:10
        Label{text:"Отзывы";font.pixelSize:30;font.bold:true}
        RowLayout { Layout.fillWidth:true
            TextField{id:q;placeholderText:"Поиск по тексту/автору";Layout.fillWidth:true;onTextChanged:reload()}
            ComboBox{id:sent;model:["all","positive","neutral","negative"];onCurrentTextChanged:reload()}
            ComboBox{id:crit;model:["all","low","medium","high","critical"];onCurrentTextChanged:reload()}
            CheckBox{id:unv;text:"Не проверено";onToggled:reload()}
            ComboBox{id:sort;model:["id_desc","id_asc","date_desc","date_asc"];onCurrentTextChanged:reload()}
        }
        ListView { Layout.fillWidth:true;Layout.fillHeight:true;spacing:7;model:rows
            delegate: Rectangle { width:ListView.view.width;height:96;radius:8;color:"white";border.color:"#E1E6EE"
                MouseArea{anchors.fill:parent;onClicked:openReview(modelData.id)}
                Column { anchors.fill:parent;anchors.margins:10;spacing:3
                    Label{text:"#"+modelData.id+" • "+modelData.source+" • "+(modelData.review_date||"—");font.bold:true}
                    Label{width:parent.width;text:modelData.text;elide:Text.ElideRight}
                    Label{color:"#657086";text:(modelData.sentiment||"—")+" • "+(modelData.criticality||"—")+" • "+(modelData.aspects||[]).join(", ")+(modelData.expert_label_id?" • эксперт ✓":"")}
                }
            }
        }
    }
}
