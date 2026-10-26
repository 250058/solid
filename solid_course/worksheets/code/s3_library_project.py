"""
3차시 활동 3-4 시작 코드: 종합 설계 프로젝트 - 학교 도서관 대출 시스템

상황:
    학교 도서관 프로그램은 LibrarySystem 한 클래스가 대출 규칙, 연체료 계산,
    이메일 알림, JSON 파일 저장을 모두 맡고 있다. 이번 학기에 요구 변경 카드 3장이 들어왔다.

    요구 변경 카드 ① (도서관 운영위원회)
        교직원(staff) 회원을 새로 만든다. 교직원은 최대 10권, 30일 대출, 연체료는 면제(0원).
    요구 변경 카드 ② (학생회)
        이메일 대신 문자(SMS) 알림을 받을 수 있게 해 달라.
        문자 발송기 클래스 이름은 SmsNotifier, 출력은 "[SMS -> 받는사람] 메시지" 형태.
    요구 변경 카드 ③ (정보부 선생님)
        테스트할 때 loans.json 파일이 생기지 않도록, 메모리에만 저장하는 저장소로 바꿔 끼우고 싶다.
        메모리 저장소 클래스 이름은 MemoryRepository.

모둠 활동 순서:
    1) 학습지에 원칙-근거 표(카드 -> 원칙 -> 새 클래스/Protocol)와 의존 화살표를 먼저 그린다.
    2) 카드 1장 이상을 골라 실제로 구현한다. 구조는 모둠이 정한다.
    3) 실행해서 구현한 카드의 점검이 [통과]인지 확인한다. 점검 3개는 서로 독립이다.

규칙:
    - 맨 아래 "점검" 구역과 build_library의 매개변수 이름(data_dir, notifier, repository)은 바꾸지 않는다.
    - build_library 함수 몸통과 그 위의 코드는 자유롭게 바꾸고 나눠도 된다.

실행 방법:
    python3 s3_library_project.py
"""

import json
import tempfile
from datetime import date, timedelta
from pathlib import Path
from typing import Protocol  # 필요하면 사용한다


class LibrarySystem:
    """대출 규칙 + 연체료 + 알림 + 저장을 모두 혼자 맡은 클래스."""

    def __init__(self, data_path: Path) -> None:
        self.data_path = data_path
        # 대출 기록: {"member": 회원ID, "book": 책ID, "due": "YYYY-MM-DD"}
        self.loans: list[dict] = []

    # ----- 대출 규칙 ---------------------------------------------------
    def borrow(self, member_id: str, member_type: str, book_id: str, today: date) -> bool:
        if member_type == "student":
            limit, days = 3, 14
        elif member_type == "teacher":
            limit, days = 5, 30
        else:
            raise ValueError(f"알 수 없는 회원 유형: {member_type}")
        # TODO(학생) 카드①: 교직원(staff) 규칙이 들어갈 곳은 어디가 좋을까?

        current = sum(1 for loan in self.loans if loan["member"] == member_id)
        if current >= limit:
            print(f"  [거절] {member_id}: 대출 한도 {limit}권 초과")
            return False

        due = today + timedelta(days=days)
        self.loans.append({"member": member_id, "book": book_id, "due": due.isoformat()})
        self._save_json()  # TODO(학생) 카드③: 저장 방법이 이 클래스에 묶여 있다
        self._send_email(member_id, f"'{book_id}' 반납일은 {due}입니다.")  # TODO(학생) 카드②
        return True

    def return_book(self, member_id: str, member_type: str, book_id: str, today: date) -> int:
        """반납 처리 후 연체료(원)를 돌려준다."""
        for loan in self.loans:
            if loan["member"] == member_id and loan["book"] == book_id:
                self.loans.remove(loan)
                self._save_json()
                days_late = (today - date.fromisoformat(loan["due"])).days
                fee = self.late_fee(member_type, days_late)
                if fee > 0:
                    self._send_email(member_id, f"연체료 {fee}원이 부과되었습니다.")
                return fee
        raise ValueError(f"{member_id}의 '{book_id}' 대출 기록이 없습니다.")

    # ----- 연체료 ------------------------------------------------------
    def late_fee(self, member_type: str, days_late: int) -> int:
        if days_late <= 0:
            return 0
        if member_type == "student":
            return days_late * 100
        elif member_type == "teacher":
            return days_late * 50
        raise ValueError(f"알 수 없는 회원 유형: {member_type}")

    # ----- 알림 --------------------------------------------------------
    def _send_email(self, member_id: str, msg: str) -> None:
        print(f"  [EMAIL -> {member_id}] {msg}")

    # ----- 저장 --------------------------------------------------------
    def _save_json(self) -> None:
        self.data_path.write_text(json.dumps(self.loans, ensure_ascii=False), encoding="utf-8")


def build_library(data_dir: Path, notifier=None, repository=None):
    """조립 지점: 도서관 객체를 만들어 돌려준다.

    TODO(학생) 카드②③: notifier, repository를 받아 쓰도록 바꾼다.
    지금은 두 값을 무시하고 항상 이메일 + JSON 파일 저장으로 만든다.
    """
    return LibrarySystem(data_dir / "loans.json")


# =====================================================================
# 점검 (이 아래는 고치지 않는다) - 카드마다 독립적으로 결과를 출력한다
# =====================================================================
import contextlib
import io

D = date(2026, 3, 2)


def _need(class_name: str):
    obj = globals().get(class_name)
    assert obj is not None, f"{class_name} 클래스가 아직 없습니다."
    return obj


def check_card1(tmp: Path) -> None:
    lib = build_library(tmp)
    try:
        for i in range(10):
            assert lib.borrow("T01", "staff", f"B{i}", D), f"교직원의 {i + 1}번째 대출이 거절되었습니다."
    except ValueError as e:
        raise AssertionError(f"교직원(staff) 회원을 아직 처리하지 못합니다 ({e})")
    assert not lib.borrow("T01", "staff", "B10", D), "교직원의 11번째 대출은 거절되어야 합니다."
    fee = lib.return_book("T01", "staff", "B0", D + timedelta(days=35))
    assert fee == 0, f"교직원 연체료는 0원이어야 하는데 {fee}원입니다."
    fee = lib.return_book("T01", "staff", "B1", D + timedelta(days=30))
    assert fee == 0, "30일째 반납은 연체가 아닙니다."
    # 기존 회원 규칙이 그대로인지
    assert lib.borrow("S01", "student", "B20", D)
    assert lib.return_book("S01", "student", "B20", D + timedelta(days=16)) == 200, "학생 연체료 규칙이 바뀌었습니다."


def check_card2(tmp: Path) -> None:
    sms_cls = _need("SmsNotifier")
    lib = build_library(tmp, notifier=sms_cls())
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        lib.borrow("S02", "student", "B1", D)
    out = buf.getvalue()
    assert "[SMS" in out, "대출할 때 [SMS ...] 알림이 출력되지 않았습니다. build_library가 notifier를 쓰나요?"
    assert "[EMAIL" not in out, "SMS를 넣었는데 이메일도 함께 나갔습니다."


def check_card3(tmp: Path) -> None:
    repo_cls = _need("MemoryRepository")
    lib = build_library(tmp, repository=repo_cls())
    with contextlib.redirect_stdout(io.StringIO()):
        for i in range(3):
            lib.borrow("S03", "student", f"B{i}", D)
        fourth = lib.borrow("S03", "student", "B3", D)
    assert not fourth, "메모리 저장소에서도 학생 한도 3권이 지켜져야 합니다(대출 기록이 유지되나요?)."
    files = list(tmp.iterdir())
    assert not files, f"메모리 저장소를 넣었는데 파일이 생겼습니다: {[f.name for f in files]}"


def _run(name: str, fn) -> bool:
    with tempfile.TemporaryDirectory() as d:
        try:
            with contextlib.redirect_stdout(io.StringIO()):  # 점검 중 출력은 숨긴다
                fn(Path(d))
            print(f"[통과] {name}")
            return True
        except AssertionError as e:
            print(f"[미완성] {name}\n        -> {e}")
        except Exception as e:  # 구조를 바꾸는 중 생긴 오류도 카드별로만 보여 준다
            print(f"[오류] {name}\n        -> {type(e).__name__}: {e}")
    return False


if __name__ == "__main__":
    print("== 현재 동작 ==")
    with tempfile.TemporaryDirectory() as d:
        lib = build_library(Path(d))
        lib.borrow("S01", "student", "파이썬 입문", D)
        fee = lib.return_book("S01", "student", "파이썬 입문", D + timedelta(days=17))
        print(f"  연체료: {fee}원")
        print(f"  임시 폴더 파일: {[p.name for p in Path(d).iterdir()]}")

    print("\n== 카드별 점검 (구현한 카드만 통과하면 된다) ==")
    passed = [
        _run("카드 ① 교직원 10권, 연체료 면제", check_card1),
        _run("카드 ② 문자(SMS) 알림", check_card2),
        _run("카드 ③ 메모리 저장소로 바꿔 끼우기", check_card3),
    ]
    print(f"\n{sum(passed)}/3 카드 통과")
    print("통과 방법을 다시 보자: 기존 클래스를 고쳤는가, 새 코드를 추가했는가? 학습지 원칙-근거 표에 근거를 적는다.")
