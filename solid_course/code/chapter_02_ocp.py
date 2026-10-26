"""02장. OCP 개방-폐쇄 원칙 — 온라인 쇼핑 할인 정책

목적
    할인 정책이 추가될 때마다 if-elif가 늘어나는 계산기를
    '전략 패턴'으로 바꾸어, 새 정책을 기존 코드 수정 없이
    '추가'만으로 붙이는 방법을 익힌다.

다루는 원칙
    OCP(Open-Closed Principle):
    "소프트웨어 요소는 확장에는 열려 있고, 수정에는 닫혀 있어야 한다."

실행 방법
    python3 chapter_02_ocp.py
"""
from __future__ import annotations

from abc import ABC, abstractmethod


# ===== 나쁜 코드: 할인 종류마다 if-elif가 늘어나는 계산기 =====

class PriceCalculator:
    # [문제 1] 할인 종류를 문자열로 받아 분기한다.
    #          새 할인(예: "생일 쿠폰")이 생길 때마다 이 메서드를 '열어서' 고쳐야 한다.
    def final_price(self, price: int, discount_type: str) -> int:
        if discount_type == "none":
            return price
        elif discount_type == "member":       # 회원 10% 할인
            return int(price * 0.9)
        elif discount_type == "vip":          # VIP 20% 할인
            return int(price * 0.8)
        elif discount_type == "coupon":       # 3,000원 쿠폰
            return max(price - 3000, 0)
        # [문제 2] 여기 아래로 elif가 계속 쌓인다(블랙프라이데이, 생일, 첫 구매...).
        #          고칠 때마다 이미 잘 돌던 member/vip 계산까지 다시 테스트해야 한다.
        # [문제 3] 오타("vlp")를 내도 실행 시점에야 발견된다.
        else:
            raise ValueError(f"알 수 없는 할인: {discount_type}")


# ===== 개선 코드: 전략 패턴으로 확장 지점 만들기 =====

# [해결 1] 변하는 부분(할인 계산 방식)을 추상화해 '약속'으로 고정한다.
#          계산기는 이 약속에만 의존하므로 수정에 '닫힌다'.
class DiscountPolicy(ABC):
    @abstractmethod
    def apply(self, price: int) -> int:
        """할인이 적용된 가격을 돌려준다(0 미만이 되면 안 된다)."""


# [해결 2] 정책 하나 = 클래스 하나(전략). 각 정책은 서로를 모른다.
class NoDiscount(DiscountPolicy):
    def apply(self, price: int) -> int:
        return price


class RateDiscount(DiscountPolicy):
    """회원 10%, VIP 20% 같은 '비율' 할인은 하나의 클래스로 재사용한다."""

    def __init__(self, rate: float) -> None:
        self.rate = rate

    def apply(self, price: int) -> int:
        return int(price * (1 - self.rate))


class CouponDiscount(DiscountPolicy):
    def __init__(self, amount: int) -> None:
        self.amount = amount

    def apply(self, price: int) -> int:
        return max(price - self.amount, 0)


# [해결 3] 계산기는 '어떤' 정책인지 묻지 않는다. 그냥 apply를 부른다(다형성).
#          새 정책이 몇 개 추가되어도 이 클래스는 한 줄도 바뀌지 않는다 → 수정에 닫힘.
class Checkout:
    def __init__(self, policy: DiscountPolicy) -> None:
        self.policy = policy

    def final_price(self, price: int) -> int:
        return self.policy.apply(price)


# [해결 4] 요구 변경: "블랙프라이데이: 5만원 이상 구매 시 30% 할인" 추가.
#          → 새 클래스를 '추가'만 했다. 기존 Checkout/다른 정책은 그대로다 → 확장에 열림.
class BlackFridayDiscount(DiscountPolicy):
    def __init__(self, threshold: int = 50_000, rate: float = 0.3) -> None:
        self.threshold = threshold
        self.rate = rate

    def apply(self, price: int) -> int:
        if price >= self.threshold:
            return int(price * (1 - self.rate))
        return price


# ===== 실행 데모 =====
if __name__ == "__main__":
    price = 60_000

    print("--- 나쁜 코드 ---")
    calc = PriceCalculator()
    for kind in ["none", "member", "vip", "coupon"]:
        print(f"{kind:>8}: {calc.final_price(price, kind):,}원")
    try:
        calc.final_price(price, "blackfriday")
    except ValueError as e:
        # 새 할인을 쓰려면 PriceCalculator를 열어 elif를 추가해야 한다
        print("블랙프라이데이 실패 →", e)

    print("--- 개선 코드 ---")
    policies: dict[str, DiscountPolicy] = {
        "none": NoDiscount(),
        "member": RateDiscount(0.1),
        "vip": RateDiscount(0.2),
        "coupon": CouponDiscount(3000),
        "blackfriday": BlackFridayDiscount(),  # 기존 코드 수정 없이 추가
    }
    for kind, policy in policies.items():
        print(f"{kind:>11}: {Checkout(policy).final_price(price):,}원")
