"""
3차시 활동 3-5 시작 코드: 설계안 A와 B 비교 (읽고 실행만 한다)

요구 (2학년 3반 학급 문고):
    "누가 어떤 책을 빌려 갔는지 기록하고, 목록을 출력해 주세요.
     반장이 쉬는 시간에 쓰는 프로그램이고, 책은 30권 정도입니다."

같은 요구를 두 모둠이 다르게 설계했다. 두 설계는 같은 출력을 낸다.
실행하면 두 결과와 각 설계의 클래스 수, 줄 수를 보여 준다.
어느 쪽이 "더 좋은 설계"인지는 학습지에서 논쟁한다.

실행 방법:
    python3 s3_yagni_compare.py
"""

import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol


# =====================================================================
# 설계안 A (모둠 가): 클래스 2개
# =====================================================================
@dataclass
class Entry:
    student: str
    title: str
    day: str


class ClassLibraryLog:
    def __init__(self) -> None:
        self.entries: list[Entry] = []

    def borrow(self, student: str, title: str, day: str) -> None:
        self.entries.append(Entry(student, title, day))

    def report(self) -> str:
        return "\n".join(f"{e.day} {e.student} - {e.title}" for e in self.entries)


DESIGN_A = [Entry, ClassLibraryLog]


# =====================================================================
# 설계안 B (모둠 나): Protocol 6개 + 구현 + 전략 4개 + 팩토리
# =====================================================================
@dataclass
class LogEntry:
    student: str
    title: str
    day: str


class LogRepository(Protocol):
    def add(self, entry: LogEntry) -> None: ...
    def all(self) -> list[LogEntry]: ...


class Clock(Protocol):
    def today(self, given: str) -> str: ...


class Formatter(Protocol):
    def format(self, entry: LogEntry) -> str: ...


class Joiner(Protocol):
    def join(self, lines: list[str]) -> str: ...


class Validator(Protocol):
    def validate(self, entry: LogEntry) -> None: ...


class Sorter(Protocol):
    def sort(self, entries: list[LogEntry]) -> list[LogEntry]: ...


class ListLogRepository:
    def __init__(self) -> None:
        self._items: list[LogEntry] = []

    def add(self, entry: LogEntry) -> None:
        self._items.append(entry)

    def all(self) -> list[LogEntry]:
        return list(self._items)


class GivenDayClock:
    def today(self, given: str) -> str:
        return given


class LineFormatStrategy(ABC):
    @abstractmethod
    def format(self, entry: LogEntry) -> str: ...


class DayFirstFormat(LineFormatStrategy):
    def format(self, entry: LogEntry) -> str:
        return f"{entry.day} {entry.student} - {entry.title}"


class NewlineJoiner:
    def join(self, lines: list[str]) -> str:
        return "\n".join(lines)


class NoOpValidator:
    def validate(self, entry: LogEntry) -> None:
        return None


class InsertionOrderSorter:
    def sort(self, entries: list[LogEntry]) -> list[LogEntry]:
        return entries


class BorrowService:
    def __init__(self, repo: LogRepository, clock: Clock, validator: Validator) -> None:
        self.repo, self.clock, self.validator = repo, clock, validator

    def borrow(self, student: str, title: str, day: str) -> None:
        entry = LogEntry(student, title, self.clock.today(day))
        self.validator.validate(entry)
        self.repo.add(entry)


class ReportService:
    def __init__(self, repo: LogRepository, fmt: Formatter, joiner: Joiner, sorter: Sorter) -> None:
        self.repo, self.fmt, self.joiner, self.sorter = repo, fmt, joiner, sorter

    def report(self) -> str:
        entries = self.sorter.sort(self.repo.all())
        return self.joiner.join([self.fmt.format(e) for e in entries])


class ClassLibraryFactory:
    @staticmethod
    def create() -> tuple[BorrowService, ReportService]:
        repo = ListLogRepository()
        borrow = BorrowService(repo, GivenDayClock(), NoOpValidator())
        report = ReportService(repo, DayFirstFormat(), NewlineJoiner(), InsertionOrderSorter())
        return borrow, report


DESIGN_B = [
    LogEntry, LogRepository, Clock, Formatter, Joiner, Validator, Sorter,
    ListLogRepository, GivenDayClock, LineFormatStrategy, DayFirstFormat,
    NewlineJoiner, NoOpValidator, InsertionOrderSorter,
    BorrowService, ReportService, ClassLibraryFactory,
]


# =====================================================================
# 실행: 같은 기록을 두 설계에 넣고 결과와 크기를 비교한다
# =====================================================================
RECORDS = [("김하늘", "어린 왕자", "3/4"), ("박도윤", "모모", "3/4"), ("이서연", "갈매기의 꿈", "3/5")]


def size(classes: list) -> tuple[int, int]:
    lines = sum(len(inspect.getsource(c).splitlines()) for c in classes)
    return len(classes), lines


if __name__ == "__main__":
    a = ClassLibraryLog()
    for r in RECORDS:
        a.borrow(*r)

    b_borrow, b_report = ClassLibraryFactory.create()
    for r in RECORDS:
        b_borrow.borrow(*r)

    print("== 설계안 A 출력 ==")
    print(a.report())
    print("\n== 설계안 B 출력 ==")
    print(b_report.report())
    print(f"\n두 출력이 같은가? {a.report() == b_report.report()}")

    for name, classes in (("A", DESIGN_A), ("B", DESIGN_B)):
        n, lines = size(classes)
        print(f"설계안 {name}: 클래스(Protocol 포함) {n}개, 클래스 코드 {lines}줄")
