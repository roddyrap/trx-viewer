from typing import Generator, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# TODO: Consider using lxml instead.
from xml.etree import ElementTree

TRX_SCHEMA_NAME = "{http://microsoft.com/schemas/VisualStudio/TeamTest/2010}"
TEST_RUN_TAG = "{http://microsoft.com/schemas/VisualStudio/TeamTest/2010}TestRun"
TEST_RESULT_TAG = f"{TRX_SCHEMA_NAME}UnitTestResult"

# TODO: Should probably be namedtuple.
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

    def is_success(self):
        return self.outcome == "Passed"

    @staticmethod
    def __parse_test_duration(duration_str: str) -> float:
        # TRX: duration="00:00:00.0000046"
        (hours, minutes, seconds) = map(float, duration_str.split(":"))

        return hours * 3600 + minutes * 60 + seconds

    @classmethod
    def from_xml(cls, xml_node: ElementTree.Element):
        output_node = xml_node.find(f"{TRX_SCHEMA_NAME}Output")

        if (stdout_node := output_node.find(f"{TRX_SCHEMA_NAME}StdOut")) is not None: 
            stdout = stdout_node.text
        else:
            stdout = None

        # TODO: StdErr isn't tested.
        if (stderr_node := output_node.find(f"{TRX_SCHEMA_NAME}StdErr")) is not None: 
            stderr = stderr_node.text
        else:
            stderr = None

        return cls(
            xml_node.get("executionId"),
            xml_node.get("testId"),
            xml_node.get("testName"),

            xml_node.get("computerName"),
            cls.__parse_test_duration(xml_node.get("duration")),

            datetime.fromisoformat(xml_node.get("startTime")),
            datetime.fromisoformat(xml_node.get("endTime")),

            TestOutput(stdout, stderr),

            xml_node.get("testType"),
            xml_node.get("outcome"),
        )

# TODO: A class isn't really necessary, namedtuple maybe?
@dataclass
class TestRun:
    name: str
    id: int

    @classmethod
    def from_xml(cls, root: ElementTree.Element):
        name = root.get('name')
        trx_id = root.get('trx_id')

        return cls(name, trx_id)

class StreamedTestMetadata:
    def __init__(self, filename: str):
        self.filename = filename
        self.xml_parser = ElementTree.iterparse(self.filename, events=["start", "end"])

        # TODO: Better handling.
        last_event: Tuple[str, ElementTree.Element] = next(self.xml_parser)
        if last_event[0] != "start" or last_event[1].tag != TEST_RUN_TAG:
            raise RuntimeError(f"TestRun isn't first element in TRX! {last_event!r}")

        self.test_run = TestRun.from_xml(last_event[1])

    # This fully consumes the parser.
    def yield_tests(self) -> Generator[TestData]:
        event: Tuple[str, ElementTree.Element]
        for event in self.xml_parser:
            if event[0] != "end" or event[1].tag != TEST_RESULT_TAG:
                continue

            yield TestData.from_xml(event[1])

    # TODO: Manual Close is actually a real bummer.
    def close(self):
        self.xml_parser.close()
