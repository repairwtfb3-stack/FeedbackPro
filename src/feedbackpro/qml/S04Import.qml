import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
Item {
    property var p: ({})
    FileDialog{id:openDialog;title:"Выберите CSV/XLSX";nameFilters:["Отзывы (*.csv *.xlsx *.xlsm)"];onAccepted:{try{p=JSON.parse(backend.previewImport(selectedFile.toString()))}catch(e){p={error:String(e)}}}}
    ColumnLayout{anchors.fill:parent;anchors.margins:28;spacing:12
        Label{text:"Импорт";font.pixelSize:30;font.bold:true}
        RowLayout{Button{text:"Выбрать файл";onClicked:openDialog.open()} Button{text:"Импортировать и анализировать";enabled:!!p.path;onClicked:{backend.importFile(p.path);p={}}}}
        Rectangle{Layout.fillWidth:true;Layout.fillHeight:true;radius:10;color:"white";border.color:"#E1E6EE";Column{anchors.fill:parent;anchors.margins:16;spacing:7
            Label{text:p.error?"Ошибка: "+p.error:"Предпросмотр";font.bold:true}
            Label{text:"Файл: "+(p.source_file||"—")+" • строк: "+(p.total||0)+" • валидно: "+(p.accepted||0)+" • ошибок: "+(p.rejected||0)}
            Label{text:"Колонки: "+(p.columns||[]).join(", ");wrapMode:Text.Wrap;width:parent.width}
            Label{text:"Первые ошибки: "+JSON.stringify((p.errors||[]).slice(0,5));wrapMode:Text.Wrap;width:parent.width;color:"#657086"}
        }}
    }
}
