import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: output_root;
    property alias title: output_title.text;
    property alias output_text: output_text_label.text;

    Label {
        id: output_title;
        color: Style.foreground;

        Layout.fillWidth: true;

        padding: 5;

        background: Rectangle {
            radius: 5; 
            color: Style.primary;
        }
    }

    ScrollView {
        id: text_scroll;

        background: Rectangle{
            radius: 5;
            color: Style.backgroundfaint;
        }

        Layout.fillWidth: true;
        Layout.fillHeight: true;

        ScrollBar.vertical.policy: ScrollBar.AlwaysOn;
        clip: true;

        Label {
            color: Style.foreground;
            id: output_text_label;
            textFormat: Text.PlainText;
            padding: 5;
        }
    }
}