import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

ApplicationWindow {
    id: root;
    visible: true
    title: "TRX Viewer"

    color: Style.background

    required property QtObject trxTestsModel
    signal selectedTest(int test_index)

    menuBar: MenuBar {
        Menu {
            title: "File"
            Action {
                text: "Open...";
                onTriggered: trx_file_picker.open();
            }
            MenuSeparator { }
            Action {
                text: "Quit"
                onTriggered: Qt.quit();
            }
        }
        Menu {
            title: "Help"
            Action {
                text: "About"
                onTriggered: about_dialog.open();
            }
        }
    }

    FileDialog {
        id: trx_file_picker
        title: "Please choose a file"
        onAccepted: {
            console.log("Picked file: " + trx_file_picker.selectedFile);
            root.trxTestsModel.load_file(trx_file_picker.selectedFile.toString().replace("file://",""))
        }
        nameFilters: [ "TRX files (*.trx)", "All files (*)" ]
    }

    Dialog {
        id: about_dialog
        title: "About"
        popupType: Popup.Item
        standardButtons: Dialog.Ok

        x: Math.round((parent.width - width) / 2)
        y: Math.round((parent.height - height) / 2)

        ColumnLayout {
            anchors.fill: parent;

            Label {
                text: "TRX Viewer version 0.1.0"
            }

            Image {
                source: "logo.svg"

                Layout.preferredHeight: 128
                Layout.preferredWidth: 128

                Layout.alignment: Qt.AlignHCenter
            }

            Label {
                text: `Developed by Roddy Rappaport.
Using QT open-source licensed code (GPLv3).`
            }
        }
    }

    footer: Label {
        id: num_tests_label;

        Layout.leftMargin: 5;
        Layout.rightMargin: 5;

        color: Style.foreground;
        text: (test_list_view.model.get_is_loading() ? "Loading... " : "") + "Displayed tests: " + test_list_view.count
    }

    // TODO: Make these labels and the drop a header, why not.
    Label {
        id: test_title

        anchors.left: parent.left;
        anchors.right: parent.right;
        anchors.leftMargin: 5;
        anchors.rightMargin: 5;

        text: root.trxTestsModel.test_run_name ? "TRX Tests Viewer - " + root.trxTestsModel.test_run_name : "Open a file";
        font.pointSize: 20;
        color: Style.foreground;
    }

    Label {
        id: test_filename;

        anchors.top: test_title.bottom;
        anchors.left: parent.left;
        anchors.right: parent.right;
        anchors.leftMargin: 5;
        anchors.rightMargin: 5;

        text: root.trxTestsModel.filename ? "File: " + root.trxTestsModel.filename : "";
        font.pointSize: 10;
        color: Style.foreground;
    }

    DropArea {
        anchors.top: parent.top;
        anchors.right: parent.right;

        anchors.bottom: test_filename.bottom; 
        // TODO: Connect with model and load file.
    }

    RowLayout {
        id: tests_view;
        anchors.top: test_filename.bottom;
        anchors.bottom: parent.bottom;
        anchors.left: parent.left;
        anchors.right: parent.right;
        anchors.leftMargin: 5;
        anchors.rightMargin: 5;

        uniformCellSizes: true;

        ColumnLayout {
            TextField {
                id: filter_input

                // Don't allow to edit the filters if there's no active file.
                enabled: root.trxTestsModel.test_run_name ? true : false;
                placeholderText: "Enter filter..."

                Layout.fillWidth: true;

                color: Style.foreground;
                placeholderTextColor: Style.foregrounddim;
                background: Rectangle {
                    radius: 5;
                    color: Style.backgroundfaint;
                }

                onEditingFinished: {
                    filter_input.background.color = root.trxTestsModel.apply_filter_string(filter_input.text) ? Style.success : Style.failure;
                }
            }

            ListView {
                id: test_list_view;

                onCurrentIndexChanged: root.selectedTest(currentIndex)

                Layout.fillHeight: true;
                Layout.fillWidth: true;

                spacing: 2;
                clip: true;

                orientation: Qt.Vertical;

                // TODO: Horizontal scroll doesn't work yet.
                flickableDirection: Flickable.AutoFlickIfNeeded
                boundsBehavior: Flickable.StopAtBounds

                // Remove slow animation, mostly because it gets chopped in dynamic loading of
                // long files.
                highlightMoveDuration: -1
                highlightMoveVelocity: -1
                highlightResizeDuration: -1
                highlightResizeVelocity: -1

                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                    active: ScrollBar.AsNeeded
                }

                ScrollBar.horizontal: ScrollBar {
                    policy: ScrollBar.AsNeeded
                    active: ScrollBar.AsNeeded
                }

                model: root.trxTestsModel
                delegate: Item {
                    required property int index
                    required property string name
                    required property bool success

                    id: wrapper;
                    width: label.width;
                    height: label.height;
                    Rectangle {
                        id: backgroundRect
                        y: wrapper.y
                        width: label.width
                        height: label.height;
                        radius: 2;
                        color: success ? Style.success : Style.failure
                    }
                    Label {
                        id: label;
                        text: name;
                        color: Style.foreground;
                        padding: 5;
                    }
                    MouseArea {
                        anchors.fill: parent
                        onClicked: test_list_view.currentIndex = index
                    }
                    Component.onCompleted: backgroundRect.parent = test_list_view.contentItem
                }

                highlight: Rectangle {
                    color: Style.accent;
                    width: test_list_view.contentWidth;
                    z: .5;
                }
                focus: true;
            }
        }

        Item {
            id: test_information;
            Layout.fillHeight: true;
            Layout.fillWidth: true;

            Image {
                id: test_outcome_image;
                anchors.top: test_information.top;
                anchors.right: test_information.right;

                width: 128;
                height: 128;
            }

            ScrollView {
                anchors.top: test_information.top;
                anchors.left: test_information.left;
                anchors.right: test_outcome_image.left;
                anchors.bottom: test_outcome_image.bottom;
                clip: true;


                ColumnLayout {
                    anchors.fill: parent;

                    Label {
                        color: Style.foreground;
                        id: test_name_label;
                        wrapMode: Text.Wrap;

                        bottomPadding: 10;
                    }

                    Label {
                        color: Style.foreground;
                        id: execution_id_label;
                    }

                    Label {
                        color: Style.foreground;
                        id: date_difference_label;
                    }

                    Label {
                        color: Style.foreground;
                        id: time_difference_label;
                    }

                    Label {
                        color: Style.foreground;
                        id: test_type_label;
                    }
                }
            }

            ColumnLayout {
                id: test_output_layout;

                anchors.top: test_outcome_image.bottom;
                anchors.bottom: parent.bottom;
                anchors.right: parent.right;
                anchors.left: parent.left;
                anchors.topMargin: 10;

                Layout.alignment: Qt.AlignTop;
                uniformCellSizes: true;

                OutputContainer {
                    id: stdout_panel;
                    title: "Standard Output"
                }

                OutputContainer {
                    id: stderr_panel;
                    title: "Standard Error"
                }
            }

            Connections {
                target: root;
                function onSelectedTest(index) {
                    test_name_label.text = "Name: " + root.trxTestsModel.get_attr(index, "test_name");
                    execution_id_label.text = "Execution ID: " + root.trxTestsModel.get_attr(index, "execution_id");
                    test_outcome_image.source = root.trxTestsModel.get_attr(index, "outcome") == "Passed" ? "passed.svg" :  "failed.svg";
                    date_difference_label.text = "Time: " + root.trxTestsModel.get_formatted_start_date(index) + " - " + root.trxTestsModel.get_formatted_end_date(index);
                    time_difference_label.text = "Duration: " + root.trxTestsModel.get_attr(index, "duration");
                    test_type_label.text = "Test Type: " + root.trxTestsModel.get_attr(index, "test_type");

                    stdout_panel.output_text = root.trxTestsModel.get_stdout(index);
                    stderr_panel.output_text = root.trxTestsModel.get_stderr(index);
                }
            }
        }
    }
}