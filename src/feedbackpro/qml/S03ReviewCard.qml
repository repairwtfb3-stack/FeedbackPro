import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
Item {
    property int reviewId: 0; property var d: ({})
    function load(){ if(reviewId>0){ try{d=JSON.parse(backend.reviewDetail(reviewId))}catch(e){d={}} } }
    onReviewIdChanged: load(); Component.onCompleted:load()
    ColumnLayout { anchors.fill:parent;anchors.margins:28;spacing:10
        Label{text:"Карточка отзыва #"+reviewId;font.pixelSize:30;font.bold:true}
        Rectangle{Layout.fillWidth:true;Layout.preferredHeight:180;radius:10;color:"white";border.color:"#E1E6EE";Column{anchors.fill:parent;anchors.margins:14;spacing:5
            Label{text:d.text||"Выберите отзыв";wrapMode:Text.Wrap;width:parent.width}
            Label{text:"Источник: "+(d.source||"—")+" / "+(d.source_file||"—");color:"#657086"}
            Label{text:"AUTO: "+(d.sentiment||"—")+" / "+(d.criticality||"—")+" / "+(d.aspects||[]).join(", ");color:"#657086"}
            Label{text:"Версия: "+(d.analysis_version||"—")+" • "+(d.explanation||"");color:"#657086";wrapMode:Text.Wrap;width:parent.width}
        }}
        GridLayout{columns:2;Layout.fillWidth:true
            ComboBox{id:s;model:["positive","neutral","negative"]} ComboBox{id:c;model:["low","medium","high","critical"]}
            TextField{id:a;placeholderText:"aspects через запятую";Layout.fillWidth:true} TextField{id:com;placeholderText:"Комментарий эксперта";Layout.fillWidth:true}
            Button{text:"Подтвердить/скорректировать";Layout.columnSpan:2;onClicked:{backend.verify(reviewId,s.currentText,a.text,c.currentText,com.text);load()}}
        }
        Label{text:"Ревизий: "+((d.expert_history||[]).length)+" • связанных решений: "+((d.decisions||[]).length);color:"#657086"}
        Item{Layout.fillHeight:true}
    }
}
