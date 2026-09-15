import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
Item { signal openDecision(int id); property var rows:{try{return JSON.parse(backend.decisionsJson)}catch(e){return[]}}
 ColumnLayout{anchors.fill:parent;anchors.margins:28;Label{text:"Решения";font.pixelSize:30;font.bold:true}
  RowLayout{Layout.fillWidth:true;TextField{id:t;placeholderText:"Название";Layout.fillWidth:true}TextField{id:ids;placeholderText:"ID отзывов JSON, напр. [1,2]"}ComboBox{id:pr;model:["low","medium","high","critical"]}Button{text:"Создать";onClicked:backend.createDecision(t.text,"",pr.currentText,ids.text||"[]","")}}
  ListView{Layout.fillWidth:true;Layout.fillHeight:true;model:rows;delegate:Rectangle{width:ListView.view.width;height:62;color:"white";border.color:"#E1E6EE";MouseArea{anchors.fill:parent;onClicked:openDecision(modelData.id)}RowLayout{anchors.fill:parent;anchors.margins:10;Label{text:"#"+modelData.id;font.bold:true}Label{text:modelData.title;Layout.fillWidth:true}Label{text:modelData.status}}}}
 }}
