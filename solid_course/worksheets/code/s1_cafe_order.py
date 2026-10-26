"""1차시 활동 1-1, 1-2 시작 코드 — 한입카페 주문 프로그램

상황
    동네 카페 "한입카페"의 주문 프로그램이다. 지금은 CafeOrder 클래스
    하나가 주문의 모든 일을 처리한다. 오늘 아래 세 장의 변경 요청이 들어왔다.

    # TODO(학생) 요청 가 (사장님):
    #     "텀블러를 가져온 손님은 주문 합계에서 300원을 빼 주세요."
    #     -> 주문을 CafeOrder("민지", tumbler=True) 처럼 만들 수 있게 하고,
    #        이 주문의 합계는 300원 적게 나와야 한다.
    # TODO(학생) 요청 나 (매장 디자이너):
    #     "영수증 맨 아래에 와이파이 비밀번호(hanip1234)를 넣어 주세요."
    # TODO(학생) 요청 다 (외주 개발자):
    #     "주문 저장 파일을 JSON 대신 CSV로 바꿔 주세요(확장자 .csv)."
    #     -> 저장한 파일을 다시 불러왔을 때(load) 주문 내용이 같아야 한다.

활동 방법
    1) (활동 1-1) 코드를 읽기만 하고, 요청마다 고칠 메서드를 학습지에 예측한다.
    2) (활동 1-2) 요청 가 -> 나 -> 다 순서로 코드를 직접 고친다.
       고친 줄 끝에는 요청 기호 주석을 붙인다.  예)  return total - 300  # 가
       새로 추가한 줄도 똑같이 표시한다.
    3) 고칠 때마다 다시 실행해 맨 아래 "변경 요청 반영 점검" 결과를 확인한다.

실행 방법
    python3 s1_cafe_order.py
    (저장 파일은 임시 폴더에 만들었다가 프로그램이 끝나면 지운다.)
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path


class CafeOrder:
    """한입카페의 주문 한 건."""

    def __init__(self, customer: str) -> None:
        self.customer = customer
        self.items: list[tuple[str, int, int]] = []  # (메뉴 이름, 단가, 수량)

    def add_item(self, name: str, price: int, qty: int = 1) -> None:
        """메뉴를 주문에 담는다."""
        self.items.append((name, price, qty))

    def total(self) -> int:
        """주문 합계(원)를 계산한다."""
        return sum(price * qty for _, price, qty in self.items)

    def receipt_text(self) -> str:
        """영수증에 찍을 글자를 만든다."""
        lines = ["===== 한입카페 =====", f"손님: {self.customer}"]
        for name, price, qty in self.items:
            lines.append(f"  {name} x{qty}  {price * qty:,}원")
        lines.append(f"  합계: {self.total():,}원")
        lines.append("====================")
        return "\n".join(lines)

    def print_receipt(self) -> None:
        """영수증을 화면(프린터)으로 내보낸다."""
        print(self.receipt_text())

    def to_json(self) -> str:
        """주문을 저장용 글자(JSON)로 바꾼다."""
        data = {"customer": self.customer, "items": self.items, "total": self.total()}
        return json.dumps(data, ensure_ascii=False)

    def save(self, folder: Path) -> Path:
        """주문을 파일로 저장하고, 저장한 파일 경로를 돌려준다."""
        path = folder / f"order_{self.customer}.json"
        path.write_text(self.to_json(), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: Path) -> "CafeOrder":
        """저장된 파일을 읽어 주문을 다시 만든다."""
        data = json.loads(path.read_text(encoding="utf-8"))
        order = cls(data["customer"])
        for name, price, qty in data["items"]:
            order.add_item(name, price, qty)
        return order


# ===== 실행 데모 (이 아래는 고치지 않아도 된다) =====

def make_sample(customer: str, **options) -> CafeOrder:
    """점검에 쓰는 주문 하나를 만든다. options는 요청 가를 반영한 뒤에 쓰인다."""
    order = CafeOrder(customer, **options)
    order.add_item("아메리카노", 3000, 2)
    order.add_item("치즈케이크", 4500)
    return order


def check_requests(folder: Path) -> None:
    """세 변경 요청이 반영되었는지 점검해 출력한다(정답을 알려 주지는 않는다)."""
    print("\n----- 변경 요청 반영 점검 -----")

    # 요청 가: 텀블러 할인
    try:
        plain = make_sample("하준")
        tumbler = make_sample("민지", tumbler=True)
        ok = tumbler.total() == plain.total() - 300
        print(f"[요청 가] {'반영됨' if ok else '아직: 텀블러 주문 합계가 300원 적지 않다'}"
              f"  (일반 {plain.total():,}원 / 텀블러 {tumbler.total():,}원)")
    except TypeError:
        print("[요청 가] 아직: CafeOrder(이름, tumbler=True) 로 주문을 만들 수 없다")

    # 요청 나: 영수증 와이파이 비밀번호
    receipt = make_sample("하준").receipt_text()
    ok = "hanip1234" in receipt
    print(f"[요청 나] {'반영됨' if ok else '아직: 영수증에 와이파이 비밀번호가 없다'}")

    # 요청 다: CSV 저장 + 다시 불러오기
    original = make_sample("서연")
    path = original.save(folder)
    try:
        loaded = CafeOrder.load(path)
        same = loaded.items == original.items and loaded.total() == original.total()
    except Exception as e:  # 형식을 바꾸다 load가 깨질 수도 있다
        same = False
        print(f"  (load 중 오류: {type(e).__name__}: {e})")
    if path.suffix == ".csv" and same:
        print("[요청 다] 반영됨")
    elif path.suffix != ".csv":
        print(f"[요청 다] 아직: 저장 파일 확장자가 {path.suffix} 이다")
    else:
        print("[요청 다] 아직: CSV로 저장했지만 다시 불러온 주문이 원래 주문과 다르다")
    print(f"  저장된 파일 내용 -> {path.read_text(encoding='utf-8')!r}")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        order = make_sample("하준")
        order.print_receipt()
        check_requests(folder)

    # TODO(학생) 활동 1-2: 다 고친 뒤 생각해 보기
    #   이 파일에서 고친 줄에 붙은 기호(가/나/다)를 세어 학습지 표에 적는다.
