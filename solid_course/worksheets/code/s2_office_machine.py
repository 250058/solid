"""2차시 시작 코드: 동아리방 사무기기 관리 프로그램 (활동 2-4)

사용법
    python3 s2_office_machine.py

처음 실행하면 아래쪽 '점검' 결과가 [미완성]으로 나온다. 정상이다.
TODO(학생) 1 -> 2 -> 3 순서로 고치면서 다시 실행해 [통과]를 늘려 간다.

규칙
    - 점검 코드(맨 아래 check_* 함수)는 고치지 않는다.
    - SmartMFP 와 OldPrinter 가 출력하는 문자열은 바꾸지 않는다.

표준 라이브러리만 사용, Python 3.12 이상.
"""
from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable, get_type_hints  # noqa: F401 (TODO에서 사용)


# ---------------------------------------------------------------
# 지금의 설계: 모든 기기가 지켜야 하는 '큰 약속' 하나
# ---------------------------------------------------------------
class Machine(ABC):
    """사무기기 약속: 출력, 스캔, 팩스, 스테이플을 모두 할 수 있다."""

    @abstractmethod
    def print_doc(self, doc: str) -> str: ...

    @abstractmethod
    def scan_doc(self, doc: str) -> str: ...

    @abstractmethod
    def fax_doc(self, doc: str, number: str) -> str: ...

    @abstractmethod
    def staple_doc(self, doc: str) -> str: ...


# TODO(학생) 1: 여기에 쓰는 쪽(클라이언트)이 실제로 필요한 만큼의 작은 약속을 정의하세요.
#   - 이름은 Printer, Scanner, Faxer 로 한다. (스테이플은 어디에 둘지 스스로 정한다.)
#   - typing.Protocol 을 사용하고, isinstance 로 검사할 수 있게 @runtime_checkable 을 붙인다.
#   - Protocol 안의 메서드 몸체는 ... 로 둔다.


class SmartMFP(Machine):
    """학교에서 새로 들여온 복합기: 모든 기능이 있다."""

    def print_doc(self, doc: str) -> str:
        return f"[복합기] 출력: {doc}"

    def scan_doc(self, doc: str) -> str:
        return f"[복합기] 스캔 파일: {doc}.pdf"

    def fax_doc(self, doc: str, number: str) -> str:
        return f"[복합기] 팩스 {number} 로 전송: {doc}"

    def staple_doc(self, doc: str) -> str:
        return f"[복합기] 스테이플 완료: {doc}"


# TODO(학생) 2: OldPrinter 를 정리하세요.
#   - 할 수 없는 기능을 억지로 '구현'한 메서드를 없앤다.
#   - 메서드를 없애면 Machine 을 상속한 채로는 객체를 만들 수 없다. 왜 그런지 생각해 보고 해결한다.
class OldPrinter(Machine):
    """동아리방 구석의 구형 흑백 프린터: 출력만 할 수 있다."""

    def print_doc(self, doc: str) -> str:
        return f"[구형 프린터] 출력: {doc}"

    def scan_doc(self, doc: str) -> str:
        raise NotImplementedError("구형 프린터는 스캔을 못 해요")

    def fax_doc(self, doc: str, number: str) -> str:
        raise NotImplementedError("구형 프린터는 팩스를 못 해요")

    def staple_doc(self, doc: str) -> str:
        raise NotImplementedError("구형 프린터는 스테이플을 못 해요")


# ---------------------------------------------------------------
# 기기를 '쓰는 쪽'(클라이언트) 함수들
# ---------------------------------------------------------------
# TODO(학생) 3: 각 함수가 실제로 부르는 메서드를 보고, 타입 힌트 Machine 을 알맞은 작은 Protocol 로 바꾸세요.
def print_report(m: Machine) -> str:
    """동아리 활동 보고서를 출력한다."""
    return m.print_doc("동아리 활동 보고서")


def archive_scan(m: Machine) -> str:
    """지난 실험 노트를 스캔해 보관한다."""
    return m.scan_doc("실험노트_3월")


def send_permission_fax(m: Machine) -> str:
    """대회 참가 동의서를 팩스로 보낸다."""
    return m.fax_doc("참가 동의서", "02-123-4567")


# ---------------------------------------------------------------
# 점검 (고치지 마세요)
# ---------------------------------------------------------------
def _try(label: str, fn) -> bool:
    try:
        ok, msg = fn()
    except Exception as e:  # 미완성 상태의 오류를 안내 메시지로 바꾼다
        ok, msg = False, f"{type(e).__name__}: {e}"
    print(f"  [{'통과' if ok else '미완성'}] {label}" + ("" if ok else f"  -> {msg}"))
    return ok


def check_protocols():
    names = [n for n in ("Printer", "Scanner", "Faxer") if n not in globals()]
    if names:
        return False, f"{', '.join(names)} 가 아직 없어요 (TODO 1)"
    if not isinstance(SmartMFP(), globals()["Scanner"]):
        return False, "isinstance(SmartMFP(), Scanner) 가 False 예요. @runtime_checkable 을 확인하세요"
    return True, ""


def check_old_printer():
    p = OldPrinter()  # Machine 을 상속한 채 메서드를 지우면 여기서 TypeError
    left = [n for n in ("scan_doc", "fax_doc", "staple_doc") if hasattr(p, n)]
    if left:
        return False, f"OldPrinter 에 아직 {', '.join(left)} 가 있어요 (TODO 2)"
    return print_report(p) == "[구형 프린터] 출력: 동아리 활동 보고서", "print_report 결과가 달라졌어요"


def check_hints():
    want = {print_report: "Printer", archive_scan: "Scanner", send_permission_fax: "Faxer"}
    for fn, proto in want.items():
        hint = get_type_hints(fn)["m"]
        if hint is not globals().get(proto):
            return False, f"{fn.__name__} 의 m 이 아직 {getattr(hint, '__name__', hint)} 예요 (TODO 3)"
    return True, ""


def check_smart_mfp_still_works():
    m = SmartMFP()
    got = (print_report(m), archive_scan(m), send_permission_fax(m))
    want = ("[복합기] 출력: 동아리 활동 보고서",
            "[복합기] 스캔 파일: 실험노트_3월.pdf",
            "[복합기] 팩스 02-123-4567 로 전송: 참가 동의서")
    return got == want, f"SmartMFP 결과가 달라졌어요: {got}"


if __name__ == "__main__":
    print("== 지금 상태 그대로 실행해 보기 ==")
    for client in (print_report, archive_scan, send_permission_fax):
        for cls in (SmartMFP, OldPrinter):
            try:
                machine = cls()  # 객체를 만들 수 없는 상태도 메시지로 보여 준다
            except Exception as e:
                print(f"  {cls.__name__}() 객체를 만들 수 없음 -> {type(e).__name__}: {e}")
                continue
            try:
                print(f"  {client.__name__}({cls.__name__}) -> {client(machine)}")
            except Exception as e:
                print(f"  {client.__name__}({cls.__name__}) -> 예외 {type(e).__name__}: {e}")

    print("\n== 점검 ==")
    results = [
        _try("TODO 1: Printer/Scanner/Faxer Protocol 정의", check_protocols),
        _try("TODO 2: OldPrinter 에 못 하는 기능이 남아 있지 않다", check_old_printer),
        _try("TODO 3: 클라이언트가 작은 Protocol 에만 의존한다", check_hints),
        _try("기존 기능 유지: SmartMFP 는 여전히 모든 클라이언트에 쓸 수 있다", check_smart_mfp_still_works),
    ]
    print(f"\n통과 {sum(results)} / {len(results)}")
    if all(results):
        print("모두 통과! 학습지 활동 2-4의 질문에 답하세요.")
