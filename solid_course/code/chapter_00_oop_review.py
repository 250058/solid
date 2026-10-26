"""00장. OOP 복습: SOLID를 배우기 전에 — 도형 클래스 계층

목적
    SOLID 5원칙을 이해하는 데 꼭 필요한 객체지향 기초 도구
    (추상화, 상속, 다형성, 추상 클래스(ABC), 결합도/응집도)를
    '도형 넓이 계산'이라는 작은 예제로 복습한다.

다루는 원칙
    아직 특정 SOLID 원칙은 아니다. 다만 나쁜 코드에서 보이는 문제들
    (if-elif 분기 폭증, 데이터와 행동의 분리)이 이후 SRP·OCP·LSP의 출발점이 된다.

실행 방법
    python3 chapter_00_oop_review.py
"""
from __future__ import annotations

import math
from abc import ABC, abstractmethod


# ===== 나쁜 코드: 도형 '종류' 문자열로 분기하는 절차적 설계 =====

# [문제 1] 도형이 그냥 딕셔너리(데이터 덩어리)다.
#          "원은 반지름이 필요하다" 같은 규칙을 아무도 지켜 주지 않는다.
#          오타("radius" → "radious")가 나도 실행해 보기 전엔 모른다.
def make_shape(kind: str, **data: float) -> dict:
    return {"kind": kind, **data}


# [문제 2] 넓이 계산 지식이 도형 바깥 함수에 모여 있다(낮은 응집도).
#          원의 정보는 make_shape에, 원의 계산은 여기에 흩어져 있다.
def area(shape: dict) -> float:
    # [문제 3] 도형 종류마다 if-elif가 늘어난다.
    #          '삼각형'을 추가하려면 이 함수를 열어 고쳐야 한다.
    if shape["kind"] == "circle":
        return math.pi * shape["radius"] ** 2
    elif shape["kind"] == "rect":
        return shape["width"] * shape["height"]
    else:
        raise ValueError(f"모르는 도형: {shape['kind']}")


# [문제 4] 둘레 계산에도 '똑같은 분기'가 또 등장한다(높은 결합도).
#          area, perimeter, draw ... 기능이 늘수록 도형 종류 문자열에
#          의존하는 곳이 늘어나, 새 도형 하나에 여러 함수를 함께 고쳐야 한다.
def perimeter(shape: dict) -> float:
    if shape["kind"] == "circle":
        return 2 * math.pi * shape["radius"]
    elif shape["kind"] == "rect":
        return 2 * (shape["width"] + shape["height"])
    else:
        raise ValueError(f"모르는 도형: {shape['kind']}")


# ===== 개선 코드: 추상 클래스 + 상속 + 다형성 =====

# [해결 1] 추상화: "도형이라면 넓이와 둘레를 계산할 수 있다"는 공통 약속만
#          뽑아낸다. 어떻게 계산하는지는 감춘다.
# [해결 2] 추상 클래스(ABC): @abstractmethod로 그 약속을 코드로 못 박는다.
#          Shape()를 직접 만들 수 없고, 하위 클래스가 area/perimeter를
#          빠뜨리면 인스턴스화(Square(...) 호출) 때 __init__이 실행되기
#          전에 TypeError가 난다.
class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        """도형의 넓이를 돌려준다."""

    @abstractmethod
    def perimeter(self) -> float:
        """도형의 둘레를 돌려준다."""

    # 공통 행동은 부모에 한 번만 둔다. 하위 클래스는 자동으로 물려받는다.
    def describe(self) -> str:
        return f"{type(self).__name__}: 넓이={self.area():.2f}, 둘레={self.perimeter():.2f}"


# [해결 3] 상속 + 높은 응집도: 원에 관한 데이터(radius)와 계산(area, perimeter)이
#          Circle 한 곳에 모인다. 원의 공식이 바뀌면 이 클래스만 고친다.
class Circle(Shape):
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        return 2 * math.pi * self.radius


class Rectangle(Shape):
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


# [해결 4] 새 도형 추가 = 새 클래스 하나 추가. 기존 코드는 한 줄도 안 고친다.
#          (나쁜 코드에선 area, perimeter 두 함수를 모두 열어야 했다.)
class Triangle(Shape):
    def __init__(self, a: float, b: float, c: float) -> None:
        self.a, self.b, self.c = a, b, c

    def area(self) -> float:
        s = self.perimeter() / 2  # 헤론의 공식
        return math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))

    def perimeter(self) -> float:
        return self.a + self.b + self.c


# [해결 5] 다형성 + 낮은 결합도: 이 함수는 Shape라는 '약속'에만 의존한다.
#          실제 객체가 원이든 삼각형이든 shape.area()를 부르면
#          각자 자기 방식으로 계산한다. 그래서 if-elif가 사라진다.
def total_area(shapes: list[Shape]) -> float:
    return sum(shape.area() for shape in shapes)


# ===== 실행 데모 =====
if __name__ == "__main__":
    print("--- 나쁜 코드 ---")
    old_shapes = [make_shape("circle", radius=1), make_shape("rect", width=2, height=3)]
    for s in old_shapes:
        print(s["kind"], f"넓이={area(s):.2f}", f"둘레={perimeter(s):.2f}")
    try:
        area(make_shape("triangle", a=3, b=4, c=5))
    except ValueError as e:
        # 새 도형을 지원하려면 area/perimeter를 모두 고쳐야 한다는 신호
        print("삼각형 추가 실패 →", e)

    print("--- 개선 코드 ---")
    shapes: list[Shape] = [Circle(1), Rectangle(2, 3), Triangle(3, 4, 5)]
    for s in shapes:
        print(s.describe())  # 같은 호출, 다른 동작 = 다형성
    print(f"전체 넓이 합계: {total_area(shapes):.2f}")

    try:
        Shape()  # type: ignore[abstract]
    except TypeError as e:
        # 추상 클래스는 직접 만들 수 없다: '약속'일 뿐 실체가 아니기 때문
        print("Shape() 생성 실패 →", type(e).__name__)
