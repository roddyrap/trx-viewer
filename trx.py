from typing import List, Optional
from xml.etree import ElementTree
from dataclasses import dataclass
from datetime import datetime

TRX_SCHEMA_NAME = "{http://microsoft.com/schemas/VisualStudio/TeamTest/2010}"
TEST_RESULT_TAG = f"{TRX_SCHEMA_NAME}Results/{TRX_SCHEMA_NAME}UnitTestResult"

@dataclass
class TestOutput:
    stdout: Optional[str] = None
    stderr: Optional[str] = None


@dataclass
class TestData:
    execution_id: str
    test_id: str
    test_name: str

    computer_name: str
    duration: float

    start_date: datetime
    end_date: datetime

    output: TestOutput

    test_type: str
    outcome: str

    @staticmethod
    def __parse_test_duration(duration_str: str) -> float:
        # TRX: duration="00:00:00.0000046"
        (hours, minutes, seconds) = map(float, duration_str.split(":"))

        return hours * 3600 + minutes * 60 + seconds

    @classmethod
    def from_xml(cls, xml_node: ElementTree.Element):
        output_node = xml_node.find(f"{TRX_SCHEMA_NAME}Output")
        return cls(
            xml_node.get("executionId"),
            xml_node.get("testId"),
            xml_node.get("testName"),

            xml_node.get("computerName"),
            cls.__parse_test_duration(xml_node.get("duration")),

            datetime.fromisoformat(xml_node.get("startTime")),
            datetime.fromisoformat(xml_node.get("endTime")),

            # TODO: StdErr isn't tested.
            TestOutput(output_node.find(f"{TRX_SCHEMA_NAME}StdOut"), output_node.find(f"{TRX_SCHEMA_NAME}StdErr")),

            xml_node.get("testType"),
            xml_node.get("outcome"),
        )

@dataclass
class TestRun:
    name: str
    id: int
    tests: List[TestData]

    @classmethod
    def from_trx_file(cls, filename: str):
        with open(filename, "rb") as trx_file:
            tree = ElementTree.parse(trx_file)

        root = tree.getroot()

        name = root.get('name')
        trx_id = root.get('trx_id')
        tests = [TestData.from_xml(test_xml) for test_xml in tree.getroot().findall(TEST_RESULT_TAG)]

        return cls(name, trx_id, tests)