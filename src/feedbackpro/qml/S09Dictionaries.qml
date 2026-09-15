import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
Item { property var rows:{try{return JSON.parse(backend.topicsJson)}catch(e){return[]}}
 ColumnLayout{anchors.fill:parent;anchors.margins:28;Label{text:"Справочники";font.pixelSize:30;font.bold:true}RowLayout{TextField{id:c;placeholderText:"Код"}TextField{id:t;placeholderText:"Название";Layout.fillWidth:true}CheckBox{id:a;text:"Активна";checked:true}Button{text:"Сохранить";onClicked:backend.setTopic(c.text,t.text,a.checked)}}ListView{Layout.fillWidth:true;Layout.fillHeight:true;model:rows;delegate:Label{text:modelData.code+" — "+modelData.title}}}
}
