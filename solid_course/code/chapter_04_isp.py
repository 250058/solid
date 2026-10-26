"""
chapter_04_isp.py — ISP(인터페이스 분리 원칙) 예제: 복합기와 프린터

목적
    인쇄·스캔·팩스를 한 덩어리로 묶은 '뚱뚱한' Machine 인터페이스가
    단순 프린터와 그 사용자(클라이언트)를 어떻게 괴롭히는지 보고,
    클라이언트가 실제로 쓰는 기능 단위의 작은 인터페이스(Protocol)로 나눈다.

다루는 원칙
    ISP: 클라이언트는 자신이 사용하지 않는 메서드에 의존하도록 강요받으면 안 된다.
         파이썬에서는 typing.Protocol(구조적 타이핑) 또는 ABC 로 작은 인터페이스를 표현한다.

실행 방법
    python3 chapter_04_isp.py
"""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


# ======================================================================
# 나쁜 코드: 모든 기능을 담은 뚱뚱한 Machine 인터페이스
# ======================================================================

class Machine(ABC):
    # [문제 1] 인쇄·스캔·팩스를 하나의 인터페이스에 몰아넣었다.
    #   → 이 인터페이스를 '구현하는 쪽'은 할 수 없는 기능까지 구현해야 하고,
    #   → 이 인터페이스를 '사용하는 쪽'은 필요 없는 기능에까지 엮인다(인터페이스 오염).
    @abstractmethod
    def print_doc(self, doc: str) -> str: ...

    @abstractmethod
    def scan_doc(self, doc: str) -> str: ...

    @abstractmethod
    def fax_doc(self, doc: str, number: str) -> str: ...


class BadMultiFunctionPrinter(Machine):
    """복합기: 세 기능을 모두 할 수 있으니 문제없어 보인다."""

    def print_doc(self, doc: str) -> str:
        return f"[복합기] 인쇄: {doc}"

    def scan_doc(self, doc: str) -> str:
        return f"[복합기] 스캔: {doc}.pdf"

    def fax_doc(self, doc: str, number: str) -> str:
        return f"[복합기] 팩스 {number} 로 전송: {doc}"


class BadSimplePrinter(Machine):
    """단순 프린터: 인쇄밖에 못 하는데 Machine 을 상속해야 '프린터'로 인정받는다."""

    def print_doc(self, doc: str) -> str:
        return f"[프린터] 인쇄: {doc}"

    # [문제 2] 못 하는 기능을 억지로 구현 → 예외를 던지는 '가짜 구현'.
    #   → Machine 을 믿고 scan_doc 을 부른 코드는 런타임에 터진다(3장 LSP 위반과 같은 모양).
    def scan_doc(self, doc: str) -> str:
        raise NotImplementedError("이 프린터는 스캔을 지원하지 않습니다")

    # [문제 3] 팩스 시그니처가 바뀌면(예: 해상도 인자 추가) 팩스와 무관한
    #   단순 프린터 코드까지 고쳐야 한다. '쓰지도 않는 메서드'가 변경 이유가 된다.
    def fax_doc(self, doc: str, number: str) -> str:
        raise NotImplementedError("이 프린터는 팩스를 지원하지 않습니다")


class BadPrintQueue:
    # [문제 4] 인쇄만 하는 클라이언트인데 Machine 전체에 의존한다.
    #   → 테스트용 가짜(fake) 객체를 만들 때도 scan/fax 까지 구현해야 하고,
    #   → Machine 에 메서드가 하나 늘 때마다 이 클라이언트의 의존 대상도 같이 커진다.
    def __init__(self, machine: Machine) -> None:
        self.machine = machine

    def run(self, docs: list[str]) -> list[str]:
        return [self.machine.print_doc(d) for d in docs]


# ======================================================================
# 개선 코드: 클라이언트가 쓰는 역할 단위로 작은 Protocol 을 나눈다
# ======================================================================

# [해결 1] 역할(능력)별로 인터페이스를 쪼갠다. 각 Protocol 은 메서드 하나뿐이다.
#   Protocol 은 '이런 메서드를 가진 객체면 된다'는 구조적 타이핑이라
#   구현 클래스가 상속하지 않아도 된다(덕 타이핑을 타입 검사기가 이해하는 형태).
#   @runtime_checkable 은 데모에서 isinstance 로 확인해 보려고 붙였다(메서드 존재 여부만 검사).

@runtime_checkable
class Printer(Protocol):
    def print_doc(self, doc: str) -> str: ...


@runtime_checkable
class Scanner(Protocol):
    def scan_doc(self, doc: str) -> str: ...


@runtime_checkable
class Fax(Protocol):
    def fax_doc(self, doc: str, number: str) -> str: ...


class SimplePrinter:
    # [해결 2] 단순 프린터는 할 수 있는 일(print_doc)만 구현한다.
    #   가짜 구현도, NotImplementedError 도 없다. Printer Protocol 을 상속하지 않았지만
    #   print_doc 시그니처가 같으므로 Printer 로 인정된다.
    def print_doc(self, doc: str) -> str:
        return f"[프린터] 인쇄: {doc}"


class MultiFunctionPrinter:
    # [해결 3] 복합기는 여러 역할을 '조합'해서 가진다. 한 클래스가 여러 Protocol 을
    #   동시에 만족하는 것은 자연스럽다. 인터페이스를 나눈다고 구현까지 쪼갤 필요는 없다.
    def print_doc(self, doc: str) -> str:
        return f"[복합기] 인쇄: {doc}"

    def scan_doc(self, doc: str) -> str:
        return f"[복합기] 스캔: {doc}.pdf"

    def fax_doc(self, doc: str, number: str) -> str:
        return f"[복합기] 팩스 {number} 로 전송: {doc}"


class PrintQueue:
    # [해결 4] 인쇄 클라이언트는 Printer 만 안다. 팩스 시그니처가 바뀌어도 영향이 없고,
    #   테스트할 때는 print_doc 하나짜리 가짜 객체면 충분하다.
    def __init__(self, printer: Printer) -> None:
        self.printer = printer

    def run(self, docs: list[str]) -> list[str]:
        return [self.printer.print_doc(d) for d in docs]


class ScanArchive:
    # [해결 5] 스캔 보관 클라이언트는 Scanner 만 요구한다.
    #   SimplePrinter 를 넘기면 '실행 중 예외'가 아니라 '타입 검사 단계의 오류'로 잡힌다.
    def __init__(self, scanner: Scanner) -> None:
        self.scanner = scanner

    def archive(self, doc: str) -> str:
        return f"보관 완료 <- {self.scanner.scan_doc(doc)}"


# ----------------------------------------------------------------------
# 요구 변경: "스테이플(철하기) 기능이 있는 사무용 프린터를 들여왔어요"
#   - 나쁜 코드: Machine 에 staple() 을 추가 → 복합기·단순 프린터 '모두'에
#     staple 구현(대부분 NotImplementedError)을 추가해야 한다.
#   - 개선 코드: Stapler Protocol 과 새 기기 클래스만 추가. 기존 클래스·클라이언트는 그대로.
# ----------------------------------------------------------------------

@runtime_checkable
class Stapler(Protocol):
    def staple(self, pages: int) -> str: ...


class OfficePrinter:
    """인쇄 + 스테이플만 하는 사무용 프린터."""

    def print_doc(self, doc: str) -> str:
        return f"[사무용] 인쇄: {doc}"

    def staple(self, pages: int) -> str:
        return f"[사무용] {pages}장 철하기 완료"


class BookletService:
    # 인쇄와 철하기가 '둘 다' 필요한 클라이언트는 두 역할을 각각 받는다.
    #   (같은 객체를 두 번 넘겨도 되고, 서로 다른 기계를 조합해도 된다.)
    def __init__(self, printer: Printer, stapler: Stapler) -> None:
        self.printer = printer
        self.stapler = stapler

    def make(self, pages: list[str]) -> list[str]:
        out = [self.printer.print_doc(p) for p in pages]
        out.append(self.stapler.staple(len(pages)))
        return out


if __name__ == "__main__":
    print("=== 나쁜 코드: 뚱뚱한 Machine 인터페이스 ===")
    machines: list[Machine] = [BadMultiFunctionPrinter(), BadSimplePrinter()]
    for m in machines:
        print(" ", BadPrintQueue(m).run(["보고서"])[0])
        # Machine 타입이니 scan_doc 이 있다고 믿고 불렀다가…
        try:
            print(" ", m.scan_doc("계약서"))
        except NotImplementedError as e:
            print("  [예외]", e)

    print()
    print("=== 개선 코드: 역할별 작은 Protocol ===")
    simple, mfp, office = SimplePrinter(), MultiFunctionPrinter(), OfficePrinter()
    for p in (simple, mfp, office):
        print(" ", PrintQueue(p).run(["보고서"])[0])
    print(" ", ScanArchive(mfp).archive("계약서"))
    for line in BookletService(office, office).make(["1쪽", "2쪽", "3쪽"]):
        print(" ", line)

    print()
    print("=== 누가 어떤 역할을 만족하나? (구조적 타이핑) ===")
    for obj in (simple, mfp, office):
        roles = [proto.__name__ for proto in (Printer, Scanner, Fax, Stapler) if isinstance(obj, proto)]
        print(f"  {type(obj).__name__:22} -> {', '.join(roles)}")
