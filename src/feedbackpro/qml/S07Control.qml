import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
Item { property var rows:{try{return JSON.parse(backend.controlsJson)}catch(e){return[]}}
 ColumnLayout{anchors.fill:parent;anchors.margins:28;Label{text:"Контроль";font.pixelSize:30;font.bold:true}
  RowLayout{TextField{id:did;placeholderText:"ID решения"}ComboBox{id:st;model:["planned","in_progress","completed","verified"]}TextField{id:due;placeholderText:"YYYY-MM-DD"}TextField{id:out;placeholderText:"Результат";Layout.fillWidth:true}Button{text:"Сохранить";onClicked:backend.setControl(parseInt(did.text),st.currentText,due.text,out.text)}}
  ListView{Layout.fillWidth:true;Layout.fillHeight:true;model:rows;delegate:Rectangle{width:ListView.view.width;height:58;color:"white";border.color:"#E1E6EE";RowLayout{anchors.fill:parent;anchors.margins:9;Label{text:"Решение #"+modelData.decision_id;font.bold:true}Label{text:modelData.decision_title;Layout.fillWidth:true}Label{text:modelData.status+(modelData.verified_at?" ✓":"")}}}}
 }}
