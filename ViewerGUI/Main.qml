import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root;
    visible: true
    title: "TRX Viewer"

    required property QtObject trxTestsModel
    signal selectedTest(int test_index)

    Label {
        anchors.left: parent.left;
        anchors.right: parent.right;

        id: test_title
        text: root.trxTestsModel.get_test_run_name();
        font.pointSize: 20;
    }

    Label {
        anchors.top: test_title.bottom;
        anchors.left: parent.left;
        anchors.right: parent.right;

        id: test_filename;
        text: "File: " + root.trxTestsModel.get_filename();
        font.pointSize: 10;
    }

    DropArea {
        anchors.top: parent.top;
        anchors.right: parent.right;

        anchors.bottom: tests_view.top; 
        // TODO: Connect with model and load file.
    }

    RowLayout {
        id: tests_view;
        anchors.top: test_filename.bottom;
        anchors.bottom: parent.bottom;
        anchors.left: parent.left;
        anchors.right: parent.right;

        uniformCellSizes: true;

        ColumnLayout {
            TextField {
                Layout.fillWidth: true;

                id: filter_input
            }

            ListView {
                id: test_list_view;

                onCurrentIndexChanged: root.selectedTest(currentIndex)

                Layout.fillHeight: true;
                Layout.fillWidth: true;

                spacing: 10;
                clip: true;

                orientation: Qt.Vertical;

                // TODO: Horizontal scroll doesn't work yet.
                flickableDirection: Flickable.AutoFlickIfNeeded
                boundsBehavior: Flickable.StopAtBounds

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
                        
                        radius: 5;
                        color: success ? "darkgreen" : "darkred"
                    }
                    Text {
                        id: label;
                        text: name;
                        color: "white";
                        padding: 5;
                    }
                    MouseArea {
                        anchors.fill: parent
                        onClicked: test_list_view.currentIndex = index
                    }
                    Component.onCompleted: backgroundRect.parent = test_list_view.contentItem
                }

                highlight: Rectangle {
                    color: "darkblue";
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
            }

            Text {
                id: test_name_label;
                wrapMode: Text.Wrap;

                bottomPadding: 10;

                anchors.top: test_information.top;
                anchors.left: test_information.left;
                anchors.right: test_outcome_image.left;
            }

            Text {
                id: execution_id_label;
                anchors.top: test_name_label.bottom;
                anchors.left: test_information.left;
            }

            Text {
                id: date_difference_label;
                anchors.top: execution_id_label.bottom;
                anchors.left: test_information.left;
            }

            Text {
                id: time_difference_label;
                anchors.top: date_difference_label.bottom;
                anchors.left: test_information.left;
            }

            Text {
                id: test_type_label;
                anchors.top: time_difference_label.bottom;
                anchors.left: test_information.left;
            }

            Connections {
                target: root;
                function onSelectedTest(index) {
                    test_name_label.text = "Name: " + root.trxTestsModel.get_attr(index, "test_name");
                    execution_id_label.text = "Execution ID: " + root.trxTestsModel.get_attr(index, "execution_id");
                    test_outcome_image.source = root.trxTestsModel.get_attr(index, "outcome") == "Passed" ? "passed.svg" :  "failed.svg";
                    date_difference_label.text = "Time: " + root.trxTestsModel.get_formatted_start_date(index) + " - " + root.trxTestsModel.get_formatted_end_date(index);
                    time_difference_label.text = "Duration: " + root.trxTestsModel.get_attr(index, "duration");
                    test_type_label.text = "Test Type: " +  + root.trxTestsModel.get_attr(index, "test_type");
                }
            }
        }
    }
}