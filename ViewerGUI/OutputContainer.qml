import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: output_root;
    property alias title: output_title.text;
    property alias output_text: output_text_label.text;

    Text {
        id: output_title;
    }

    ScrollView {
        id: text_scroll;

        Layout.fillWidth: true;
        Layout.fillHeight: true;

        background: Rectangle {
            opacity: 1;
            color: "white";
        }

        ScrollBar.vertical.policy: ScrollBar.AlwaysOn;
        clip: true;

        Text {
            id: output_text_label;
            textFormat: Text.PlainText
        }
    }
}