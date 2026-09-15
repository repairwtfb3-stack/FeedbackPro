import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
Item { property int decisionId:0
 ColumnLayout{anchors.fill:parent;anchors.margins:28;Label{text:"Карточка решения #"+decisionId;font.pixelSize:30;font.bold:true}
  Label{text:"Допустимый маршрут: created → planned → in_progress → completed → verified";color:"#657086"}
  RowLayout{ComboBox{id:st;model:["planned","in_progress","completed","verified"]}Button{text:"Перевести";enabled:decisionId>0;onClicked:backend.transitionDecision(decisionId,st.currentText)}}
  Item{Layout.fillHeight:true}
 }}
