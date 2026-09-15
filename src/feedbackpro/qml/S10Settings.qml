import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
Item {
 FileDialog{id:backupDialog;fileMode:FileDialog.SaveFile;nameFilters:["SQLite (*.db)"];onAccepted:backend.backup(selectedFile.toString())}
 ColumnLayout{anchors.fill:parent;anchors.margins:28;Label{text:"Настройки";font.pixelSize:30;font.bold:true}RowLayout{TextField{id:k;text:"organization_name"}TextField{id:v;placeholderText:"Значение";Layout.fillWidth:true}Button{text:"Сохранить";onClicked:backend.setSetting(k.text,v.text)}}RowLayout{Button{text:"Backup";onClicked:backupDialog.open()}Button{text:"Проверить целостность";onClicked:backend.integrity()}Label{text:"Schema v3 • Offline-first • Analysis a2-rules-1.0";color:"#657086"}}Item{Layout.fillHeight:true}}
}
