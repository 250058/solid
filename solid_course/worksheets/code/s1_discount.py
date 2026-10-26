"""1차시 활동 1-4, 1-5 시작 코드 — 한입카페 할인 계산기

상황
    한입카페 사장님은 매달 새 할인을 만든다. 이번 달 요구는 다음과 같다.

        "생일인 손님은 15% 할인해 주세요."   (20,000원 -> 17,000원)

    같은 요구를 두 가지 방식으로 구현해 보고, 각 방식에서
    '기존 코드를 몇 줄 고쳤는지'와 '새 코드를 몇 줄 추가했는지'를 세어 비교한다.

활동 방법
    0) 먼저 그대로 실행해 본다. 아직 생일 할인이 없어서 안내 메시지가 나온다.
    1) TODO(학생) ① : 방식 1 - PriceCalculator.final_price 의 if-elif에 "birthday"를 추가한다.
    2) TODO(학생) ② : 방식 2 - Discount를 상속한 새 클래스 BirthdayDiscount를 추가한다.
       (Discount, MemberDiscount, checkout 은 고치지 않고 해결해 보자.)
    3) 고친 줄에는 # ①, # ② 처럼 방식 기호 주석을 붙이면 줄 수를 세기 쉽다.
    4) 맨 아래 점검이 모두 "통과"가 될 때까지 실행한다.

실행 방법
    python3 s1_discount.py
"""
from __future__ import annotations

from abc import ABC, abstractmethod


# ===== 방식 1: 할인 종류를 문자열로 받아 if-elif로 나누는 계산기 =====

class PriceCalculator:
    def final_price(self, price: int, discount_type: str) -> int:
        """할인 종류 이름에 따라 최종 가격(원)을 돌려준다."""
        if discount_type == "none":
            return price
        elif discount_type == "member":      # 회원 10% 할인
            return int(price * 0.9)
        elif discount_type == "vip":         # VIP 20% 할인
            return int(price * 0.8)
        elif discount_type == "coupon":      # 2,000원 쿠폰
            return max(price - 2000, 0)
        # TODO(학생) ① 여기에 생일 할인("birthday", 15%)을 추가한다.
        elif discount_type == "birthday":
            return int(price * 0.85)
        else:
            raise ValueError(f"알 수 없는 할인: {discount_type}")


# ===== 방식 2: 할인 하나를 클래스 하나로 만드는 구조 =====

class Discount(ABC):
    """모든 할인이 지키는 약속: 원래 가격을 받아 할인된 가격(0 이상)을 돌려준다."""

    @abstractmethod
    def apply(self, price: int) -> int:
        ...


class MemberDiscount(Discount):
    """예시: 회원 10% 할인."""

    def apply(self, price: int) -> int:
        return int(price * 0.9)


# TODO(학생) ② 여기에 생일 할인 클래스 BirthdayDiscount를 추가한다.
#              위의 MemberDiscount가 어떻게 생겼는지 참고하자.
class BirthdayDiscount(Discount):
    def apply(self, price: int) -> int:
        return int(price*0.85)


def checkout(price: int, discount: Discount) -> int:
    """결제 화면: 어떤 할인인지 묻지 않고 약속(apply)대로 계산만 맡긴다."""
    return discount.apply(price)


# ===== 점검 (이 아래는 고치지 않는다) =====

def run_checks() -> None:
    calc = PriceCalculator()
    failed = 0

    def check(label: str, got, expected) -> None:
        nonlocal failed
        ok = got == expected
        failed += not ok
        print(f"  {'통과' if ok else '실패'}  {label}: 결과 {got} / 기대 {expected}")

    print("[기존 할인] 새 할인을 넣은 뒤에도 그대로여야 한다")
    check("none", calc.final_price(20000, "none"), 20000)
    check("member", calc.final_price(20000, "member"), 18000)
    check("vip", calc.final_price(20000, "vip"), 16000)
    check("coupon", calc.final_price(20000, "coupon"), 18000)
    check("checkout(MemberDiscount)", checkout(20000, MemberDiscount()), 18000)

    print("[방식 1] if-elif에 생일 할인 추가")
    try:
        check("final_price(20000, 'birthday')", calc.final_price(20000, "birthday"), 17000)
    except ValueError as e:
        failed += 1
        print(f"  아직  {e} -> TODO(학생) ①을 완성하세요.")

    print("[방식 2] 새 클래스로 생일 할인 추가")
    birthday_cls = globals().get("BirthdayDiscount")
    if birthday_cls is None:
        failed += 1
        print("  아직  BirthdayDiscount 클래스가 없습니다 -> TODO(학생) ②를 완성하세요.")
    else:
        if not issubclass(birthday_cls, Discount):
            failed += 1
            print("  실패  BirthdayDiscount가 Discount를 상속하지 않았습니다.")
        else:
            try:
                discount = birthday_cls()
            except TypeError:
                discount = None
                failed += 1
                print("  아직  BirthdayDiscount 객체를 만들 수 없습니다.")
                print("        -> apply 메서드를 이름 그대로 만들었는지 확인하세요(활동 1-1 워밍업 참고).")
            if discount is not None:
                check("checkout(20000, BirthdayDiscount())", checkout(20000, discount), 17000)

    print()
    if failed:
        print(f"[미완성] 남은 항목 {failed}개. 위 안내를 보고 이어서 고쳐 보세요.")
        return
    print("모든 점검 통과! 이제 두 방식에서 고친 줄 수를 세어 학습지에 적으세요.")


if __name__ == "__main__":
    run_checks()
