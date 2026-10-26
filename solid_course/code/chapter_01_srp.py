"""01장. SRP 단일 책임 원칙 — 카페 주문서

목적
    주문 계산, 영수증 출력, 파일 저장을 모두 떠안은 클래스를
    '변경 이유' 기준으로 나누어 보고, 요구사항이 바뀔 때
    어느 클래스만 고치면 되는지 확인한다.

다루는 원칙
    SRP(Single Responsibility Principle):
    "클래스(모듈)는 변경 이유가 단 하나여야 한다."

실행 방법
    python3 chapter_01_srp.py
    (데모는 임시 폴더에 주문 파일을 저장했다가 지운다.)
"""
from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


# ===== 나쁜 코드: 계산·출력·저장을 한 클래스가 모두 담당 =====

class CafeOrder:
    """주문에 관한 모든 일을 혼자 하는 '만능' 클래스."""

    def __init__(self, customer: str) -> None:
        self.customer = customer
        self.items: list[tuple[str, int, int]] = []  # (메뉴, 단가, 수량)

    def add_item(self, name: str, price: int, qty: int = 1) -> None:
        self.items.append((name, price, qty))

    # [문제 1] 변경 이유 ①: 가격 정책(사장님/회계).
    #          "텀블러 지참 시 300원 할인"이 생기면 이 메서드를 고친다.
    def total(self) -> int:
        return sum(price * qty for _, price, qty in self.items)

    # [문제 2] 변경 이유 ②: 영수증 모양(디자이너/매장 직원).
    #          "영수증 끝에 와이파이 비밀번호 출력" 요구가 오면
    #          계산 로직과 같은 클래스를 열어 고쳐야 한다.
    def print_receipt(self) -> str:
        lines = [f"[영수증] {self.customer}님"]
        for name, price, qty in self.items:
            lines.append(f"  {name} x{qty}  {price * qty:,}원")
        lines.append(f"  합계: {self.total():,}원")
        return "\n".join(lines)

    # [문제 3] 변경 이유 ③: 저장 방식(개발/인프라).
    #          "파일 말고 DB에 저장" 요구가 오면 또 이 클래스를 고친다.
    #          게다가 저장 형식을 바꾸다 실수하면 계산·출력까지 망가질 위험이 있다.
    def save(self, path: Path) -> None:
        data = {"customer": self.customer, "items": self.items, "total": self.total()}
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    # [문제 4] 결과: 세 부서의 요구가 한 파일에서 충돌한다.
    #          계산만 테스트하고 싶어도 파일 저장 코드까지 함께 딸려 온다.


# ===== 개선 코드: 변경 이유별로 클래스를 분리 =====

# [해결 1] Order: 주문 '데이터와 가격 계산'만 책임진다.
#          변경 이유는 오직 "가격 정책이 바뀔 때" 하나.
@dataclass
class OrderItem:
    name: str
    price: int
    qty: int = 1


@dataclass
class Order:
    customer: str
    items: list[OrderItem] = field(default_factory=list)

    def add_item(self, name: str, price: int, qty: int = 1) -> None:
        self.items.append(OrderItem(name, price, qty))

    def total(self) -> int:
        return sum(item.price * item.qty for item in self.items)


# [해결 2] ReceiptPrinter: '영수증 모양'만 책임진다.
#          와이파이 비밀번호 줄을 추가하려면 여기만 고치면 되고,
#          Order의 계산 로직은 건드리지 않는다.
class ReceiptPrinter:
    def __init__(self, footer: str = "") -> None:
        self.footer = footer

    def render(self, order: Order) -> str:
        lines = [f"[영수증] {order.customer}님"]
        for item in order.items:
            lines.append(f"  {item.name} x{item.qty}  {item.price * item.qty:,}원")
        lines.append(f"  합계: {order.total():,}원")  # 계산은 Order에게 '맡긴다'
        if self.footer:
            lines.append(f"  {self.footer}")
        return "\n".join(lines)


# [해결 3] OrderRepository: '저장 방식'만 책임진다.
#          DB로 바꿔야 하면 이 클래스만 교체한다. Order와 ReceiptPrinter는 무사하다.
class OrderRepository:
    def __init__(self, folder: Path) -> None:
        self.folder = folder

    def save(self, order: Order) -> Path:
        path = self.folder / f"order_{order.customer}.json"
        data = {
            "customer": order.customer,
            "items": [vars(item) for item in order.items],
            "total": order.total(),
        }
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return path


# [해결 4] 관심사 분리의 효과: 각 클래스를 따로 테스트할 수 있다.
#          예) Order.total()은 파일 시스템 없이도 검증 가능하다.


# ===== 실행 데모 =====
if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)

        print("--- 나쁜 코드 ---")
        bad = CafeOrder("민수")
        bad.add_item("아메리카노", 4500, 2)
        bad.add_item("치즈케이크", 6000)
        print(bad.print_receipt())
        bad.save(folder / "bad_order.json")
        print("저장 완료(한 클래스가 계산·출력·저장을 모두 함)")

        print("--- 개선 코드 ---")
        order = Order("민수")
        order.add_item("아메리카노", 4500, 2)
        order.add_item("치즈케이크", 6000)

        # 요구 변경: "영수증에 와이파이 비밀번호 출력" → ReceiptPrinter만 설정/수정
        printer = ReceiptPrinter(footer="Wi-Fi: cafe1234")
        print(printer.render(order))

        saved = OrderRepository(folder).save(order)
        print("저장 파일:", saved.name)
        assert order.total() == 15000  # 계산만 독립적으로 검증
        print("계산 검증 통과: 15,000원")
