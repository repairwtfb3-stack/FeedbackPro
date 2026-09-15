import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
Item {
 FileDialog{id:saveReport;fileMode:FileDialog.SaveFile;nameFilters:["Markdown (*.md)"];onAccepted:backend.exportReport(selectedFile.toString())}
 FileDialog{id:saveReviews;fileMode:FileDialog.SaveFile;nameFilters:["CSV (*.csv)","Excel (*.xlsx)"];onAccepted:backend.exportReviews(selectedFile.toString())}
 ColumnLayout{anchors.fill:parent;anchors.margins:28;spacing:12
  Label{text:"Аналитика";font.pixelSize:30;font.bold:true}
  Label{text:"Все метрики строятся по фактическим данным. BEFORE/AFTER не подставляются до пилотной апробации.";wrapMode:Text.Wrap;Layout.fillWidth:true}
  RowLayout{Button{text:"Экспорт отчёта";onClicked:saveReport.open()}Button{text:"Экспорт отзывов";onClicked:saveReviews.open()}Button{text:"Quality run по размеченным";onClicked:backend.qualityRun("")}}
  Rectangle{Layout.fillWidth:true;Layout.fillHeight:true;color:"white";radius:10;border.color:"#E1E6EE";Label{anchors.centerIn:parent;text:"Тренды • sentiment • criticality • aspects • source/channel • drill-down";color:"#657086"}}
 }}
