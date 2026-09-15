import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "qml"

ApplicationWindow {
    id: root; width: 1440; height: 900; visible: true; title: "FeedbackPro"; color: "#F5F7FA"
    property int page: 0
    property int selectedReviewId: 0
    property int selectedDecisionId: 0
    property var names: ["S01 Дашборд","S02 Отзывы","S03 Карточка отзыва","S04 Импорт","S05 Решения","S06 Карточка решения","S07 Контроль","S08 Аналитика","S09 Справочники","S10 Настройки"]
    RowLayout { anchors.fill: parent; spacing: 0
        Rectangle { Layout.preferredWidth: 250; Layout.fillHeight: true; color: "#172033"
            ColumnLayout { anchors.fill: parent; anchors.margins: 18; spacing: 8
                Label { text: "FeedbackPro"; color: "white"; font.pixelSize: 24; font.bold: true; Layout.bottomMargin: 12 }
                Repeater { model: root.names; delegate: Button { Layout.fillWidth: true; text: modelData; flat: true; highlighted: root.page===index; onClicked: root.page=index } }
                Item { Layout.fillHeight: true }
                Label { text: backend.message; color: "#B8C4D9"; wrapMode: Text.Wrap; Layout.fillWidth: true }
            }
        }
        StackLayout { Layout.fillWidth: true; Layout.fillHeight: true; currentIndex: root.page
            S01Dashboard { onOpenDrilldown: function(kind,value){ root.page=1 } }
            S02Reviews { onOpenReview: function(id){ root.selectedReviewId=id; root.page=2 } }
            S03ReviewCard { reviewId: root.selectedReviewId }
            S04Import {}
            S05Decisions { onOpenDecision: function(id){ root.selectedDecisionId=id; root.page=5 } }
            S06DecisionCard { decisionId: root.selectedDecisionId }
            S07Control {}
            S08Analytics {}
            S09Dictionaries {}
            S10Settings {}
        }
    }
}
