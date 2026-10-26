"""
6장. 종합: 도서관 대출 시스템에 SOLID 5원칙 함께 적용하기

목적:
    하나의 도메인(학교 도서관 대출)에서 SRP·OCP·LSP·ISP·DIP가 각각 어디에 쓰이는지,
    그리고 '어디까지만' 적용해야 하는지(YAGNI, 과잉 설계 경계)를 함께 보여 준다.

구성:
    1) 5원칙 적용 전: 모든 일을 혼자 하는 BeforeLibrary
    2) 5원칙 적용 후: 역할별로 나뉜 작은 클래스들 + 조립 지점(build_library)

실행 방법:
    python3 code/chapter_06_summary.py
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Protocol


# =====================================================================
# 5원칙 적용 전: 한 클래스가 규칙·저장·알림·출력을 모두 떠안는다
# =====================================================================

class BeforeLibrary:
    def __init__(self) -> None:
        self.books: dict[str, str] = {"B1": "파이썬 입문", "B2": "객체지향의 사실과 오해"}
        self.loans: list[tuple[str, str, date]] = []  # (회원ID, 책ID, 반납 예정일)

    def checkout(self, member_id: str, member_type: str, book_id: str, today: date) -> None:
        # [문제 1: SRP 위반] 대출 규칙, 저장, 알림, 영수증 출력이 한 메서드에 섞여 있다.
        #   → 영수증 양식이 바뀌어도, 알림 수단이 바뀌어도, 대출 규칙이 바뀌어도 이 메서드를 연다.

        # [문제 2: OCP 위반] 회원 유형이 늘 때마다(졸업생, 외부인...) elif를 추가해야 한다.
        if member_type == "student":
            limit, days = 3, 14
        elif member_type == "teacher":
            limit, days = 10, 30
        else:
            raise ValueError("알 수 없는 회원 유형")

        current = sum(1 for m, _, _ in self.loans if m == member_id)
        if current >= limit:
            print(f"[거절] {member_id}: 대출 한도({limit}권) 초과")
            return

        due = today + timedelta(days=days)
        # [문제 3: DIP 위반] 저장소(내부 리스트)와 알림(print로 흉내 낸 이메일)에 직접 묶여 있다.
        #   → DB로 바꾸거나 SMS로 바꾸려면 업무 규칙 코드를 고쳐야 하고, 테스트용 가짜도 못 넣는다.
        self.loans.append((member_id, book_id, due))
        print(f"[EMAIL] {member_id}님, '{self.books[book_id]}' 반납일은 {due}입니다.")
        print(f"[영수증] {member_id} | {book_id} | ~{due}")


# =====================================================================
# 5원칙 적용 후
# =====================================================================

@dataclass(frozen=True)
class Book:
    book_id: str
    title: str


@dataclass(frozen=True)
class Loan:
    member_id: str
    book: Book
    due: date


# ---------------------------------------------------------------------
# [해결 2: OCP] + [해결 3: LSP] 회원 유형별 대출 정책
# ---------------------------------------------------------------------
class LoanPolicy(ABC):
    """대출 정책의 '계약'.

    계약(모든 하위 클래스가 지켜야 함):
      - max_books()는 1 이상의 정수를 돌려준다.
      - loan_days()는 1 이상의 정수를 돌려준다.
      - 예외를 던져 '대출 자체를 막는' 방식으로 계약을 바꾸지 않는다.
    → LoanService는 어떤 하위 정책이 오든 이 계약만 믿고 동작한다(치환 가능성, LSP).
    """

    @abstractmethod
    def max_books(self) -> int: ...

    @abstractmethod
    def loan_days(self) -> int: ...


class StudentPolicy(LoanPolicy):
    def max_books(self) -> int:
        return 3

    def loan_days(self) -> int:
        return 14


class TeacherPolicy(LoanPolicy):
    def max_books(self) -> int:
        return 10

    def loan_days(self) -> int:
        return 30


class GraduatePolicy(LoanPolicy):
    """요구 변경 '졸업생도 1권, 7일 대출 허용': 새 클래스 추가만으로 흡수(OCP).

    [LSP 주의] '졸업생은 대출 불가'를 표현하려고 max_books()에서 예외를 던지면
    부모 계약을 깨는 것이다. 그런 요구라면 정책이 아니라 회원 자격 검사에서 다뤄야 한다.
    """

    def max_books(self) -> int:
        return 1

    def loan_days(self) -> int:
        return 7


# ---------------------------------------------------------------------
# [해결 4: ISP] 클라이언트가 필요한 만큼만 아는 작은 인터페이스(Protocol)
# ---------------------------------------------------------------------
class BookFinder(Protocol):
    def find(self, book_id: str) -> Book: ...


class LoanRecorder(Protocol):
    def add(self, loan: Loan) -> None: ...
    def count_by_member(self, member_id: str) -> int: ...


class Notifier(Protocol):
    def notify(self, member_id: str, message: str) -> None: ...


# ---------------------------------------------------------------------
# 저수준 구현들 (세부 사항)
# ---------------------------------------------------------------------
class InMemoryCatalog:
    """BookFinder를 '구조적으로' 만족한다(상속 없이 find 메서드만 있으면 됨)."""

    def __init__(self, books: list[Book]) -> None:
        self._books = {b.book_id: b for b in books}

    def find(self, book_id: str) -> Book:
        return self._books[book_id]


@dataclass
class InMemoryLoans:
    """LoanRecorder를 만족한다. 나중에 DB 버전이 필요해지면 그때 같은 모양으로 하나 더 만든다."""

    loans: list[Loan] = field(default_factory=list)

    def add(self, loan: Loan) -> None:
        self.loans.append(loan)

    def count_by_member(self, member_id: str) -> int:
        return sum(1 for loan in self.loans if loan.member_id == member_id)


class ConsoleEmailNotifier:
    def notify(self, member_id: str, message: str) -> None:
        print(f"[EMAIL] {member_id}님, {message}")


class FakeNotifier:
    """테스트용: 실제로 보내지 않고 기록만 남긴다(DIP 덕분에 끼울 수 있음)."""

    def __init__(self) -> None:
        self.messages: list[str] = []

    def notify(self, member_id: str, message: str) -> None:
        self.messages.append(f"{member_id}:{message}")


# ---------------------------------------------------------------------
# [해결 1: SRP] 변경 이유별로 나눈 클래스
# ---------------------------------------------------------------------
class ReceiptFormatter:
    """변경 이유: '영수증 양식'이 바뀔 때만."""

    def format(self, loan: Loan) -> str:
        return f"[영수증] {loan.member_id} | {loan.book.title} | ~{loan.due}"


class LoanService:
    """변경 이유: '대출 업무 규칙'이 바뀔 때만.

    [해결 5: DIP] 저장소·알림·정책을 직접 만들지 않고 추상(Protocol/ABC)으로 주입받는다.
    → 이 클래스 안에는 InMemory..., ConsoleEmail... 같은 구현 이름이 한 번도 나오지 않는다.
    """

    def __init__(self, finder: BookFinder, recorder: LoanRecorder, notifier: Notifier) -> None:
        self.finder = finder
        self.recorder = recorder
        self.notifier = notifier

    def checkout(self, member_id: str, policy: LoanPolicy, book_id: str, today: date) -> Loan | None:
        if self.recorder.count_by_member(member_id) >= policy.max_books():
            print(f"[거절] {member_id}: 대출 한도({policy.max_books()}권) 초과")
            return None
        book = self.finder.find(book_id)
        loan = Loan(member_id, book, today + timedelta(days=policy.loan_days()))
        self.recorder.add(loan)
        self.notifier.notify(member_id, f"'{book.title}' 반납일은 {loan.due}입니다.")
        return loan


# [YAGNI] 일부러 만들지 않은 것들:
#   - 결제 플러그인 인터페이스, 다중 DB 어댑터, 정책을 읽는 설정 파일 로더 ...
#   지금 요구사항에 없고 변경이 반복된 적도 없다. 실제로 필요해지는 순간 위 구조에
#   클래스 하나를 더하는 것으로 충분하므로, 미리 추상화 층을 쌓지 않는다.


def build_library(notifier: Notifier) -> LoanService:
    """조립 지점(Composition Root): 어떤 구현을 쓸지는 여기 한 곳에서만 정한다."""
    catalog = InMemoryCatalog([Book("B1", "파이썬 입문"), Book("B2", "객체지향의 사실과 오해")])
    return LoanService(catalog, InMemoryLoans(), notifier)


if __name__ == "__main__":
    today = date(2026, 3, 2)

    print("=== 5원칙 적용 전 ===")
    before = BeforeLibrary()
    before.checkout("s01", "student", "B1", today)
    try:
        before.checkout("g01", "graduate", "B2", today)
    except ValueError as e:
        print(f"[오류] 졸업생 대출 불가 → 코드를 열어 elif 추가 필요 ({e})")

    print("\n=== 5원칙 적용 후 ===")
    service = build_library(ConsoleEmailNotifier())
    formatter = ReceiptFormatter()
    for member, policy, book in [
        ("s01", StudentPolicy(), "B1"),
        ("t01", TeacherPolicy(), "B2"),
        ("g01", GraduatePolicy(), "B1"),   # 새 정책: 기존 코드 수정 없이 추가
        ("g01", GraduatePolicy(), "B2"),   # 한도 1권 → 거절
    ]:
        loan = service.checkout(member, policy, book, today)
        if loan:
            print(formatter.format(loan))

    print("\n=== 가짜 알림으로 테스트 ===")
    fake = FakeNotifier()
    build_library(fake).checkout("s02", StudentPolicy(), "B2", today)
    assert fake.messages == ["s02:'객체지향의 사실과 오해' 반납일은 2026-03-16입니다."]
    print(f"기록된 알림: {fake.messages}")
    print("테스트 통과")
