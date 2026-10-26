"""
chapter_03_lsp.py — LSP(리스코프 치환 원칙) 예제: 새(Bird)와 펭귄

목적
    "펭귄은 새다(is-a)"라는 현실의 분류를 그대로 상속으로 옮기면
    부모 타입의 '계약(사전조건·사후조건·불변식)'이 깨지는 과정을 보고,
    계약을 지킬 수 있는 타입 계층으로 다시 설계한다.

다루는 원칙
    LSP: 상위 타입 T를 쓰는 코드는, T 자리에 어떤 하위 타입 S를 넣어도
         '계약이 약속한 그대로' 올바르게 동작해야 한다.
         - 하위 타입은 사전조건을 강화하면 안 된다 (더 까다롭게 받으면 안 됨)
         - 하위 타입은 사후조건을 약화하면 안 된다 (약속한 결과를 덜 주면 안 됨)
         - 하위 타입은 상위 타입의 불변식을 유지해야 한다

실행 방법
    python3 chapter_03_lsp.py
"""

from abc import ABC, abstractmethod


# ======================================================================
# 나쁜 코드: "모든 새는 난다"는 계약을 가진 Bird 를 펭귄이 상속한다
# ======================================================================

class BadBird(ABC):
    """모든 새의 상위 타입. fly() 의 계약을 문서로 약속한다.

    fly(altitude) 의 계약
        사전조건: altitude 는 0 보다 큰 정수이기만 하면 된다.
        사후조건: 호출이 끝나면 self.altitude == altitude 이다 (요청한 고도에 도달).
        불변식  : self.altitude 는 언제나 0 이상이다.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.altitude = 0  # 불변식: 0 이상

    @abstractmethod
    def fly(self, altitude: int) -> None: ...


class BadSparrow(BadBird):
    """참새: 계약을 그대로 지킨다. 이것이 '정상적인 하위 타입'의 모습."""

    def fly(self, altitude: int) -> None:
        if altitude <= 0:
            raise ValueError("고도는 0보다 커야 합니다")  # 부모와 같은 사전조건
        self.altitude = altitude                           # 사후조건 충족


class BadPenguin(BadBird):
    # [문제 1] 펭귄은 날 수 없으니 예외를 던진다.
    #   → 부모는 "altitude > 0 이면 된다"고 약속했는데, 펭귄은 사실상
    #     "어떤 값도 받지 않는다"로 사전조건을 무한히 '강화'했다.
    #   → Bird 를 믿고 fly() 를 부른 클라이언트는 아무 잘못 없이 터진다.
    def fly(self, altitude: int) -> None:
        raise NotImplementedError(f"{self.name}: 펭귄은 날 수 없습니다")


class BadOstrich(BadBird):
    # [문제 2] 타조는 예외 대신 '조용히 아무것도 안 한다'.
    #   → 에러가 안 나니 더 위험하다. 호출 후 altitude 가 여전히 0 이므로
    #     "요청 고도에 도달한다"는 사후조건을 '약화'한 것이다.
    #   → 버그가 호출 지점이 아니라 한참 뒤(고도 계산, 통계 등)에서 드러난다.
    def fly(self, altitude: int) -> None:
        pass


class BadHummingbird(BadBird):
    # [문제 3] 벌새는 날지만 "10m 이하만 가능"이라는 조건을 추가했다.
    #   → 부모보다 '더 까다로운 입력'을 요구 = 사전조건 강화.
    #   → 날 수 있는 새라도 계약을 바꾸면 LSP 위반이다. (날기 여부만의 문제가 아님!)
    def fly(self, altitude: int) -> None:
        if not 0 < altitude <= 10:
            raise ValueError(f"{self.name}: 10m 이하로만 날 수 있습니다")
        self.altitude = altitude


def bad_migrate(birds: list[BadBird], altitude: int) -> list[str]:
    """철새 이동 시뮬레이션: Bird 타입만 보고 모두 fly(altitude) 를 부른다."""
    report: list[str] = []
    for bird in birds:
        # [문제 4] 하위 타입이 계약을 깨니, 클라이언트가 '타입 검사'로 방어하기 시작한다.
        #   → 새로운 '못 나는 새'(키위, 도도…)가 추가될 때마다 이 줄을 고쳐야 한다.
        #   → 이 isinstance 사다리는 LSP 위반의 대표적인 냄새이며, OCP 까지 함께 깨뜨린다.
        if isinstance(bird, BadPenguin):
            report.append(f"{bird.name}: (펭귄은 건너뜀)")
            continue
        try:
            bird.fly(altitude)
        except (NotImplementedError, ValueError) as e:
            report.append(f"[예외] {e}")
            continue
        # [문제 2]의 결과: 예외가 없어도 사후조건이 깨졌는지 확인해야 하는 처지가 된다.
        ok = bird.altitude == altitude
        report.append(f"{bird.name}: 고도 {bird.altitude}m {'OK' if ok else '<- 사후조건 위반!'}")
    return report


# ======================================================================
# 개선 코드: '날 수 있음'을 별도 타입으로 분리해 계약을 지킬 수 있는 자만 약속한다
# ======================================================================

class Bird(ABC):
    """모든 새가 '정말로' 지킬 수 있는 것만 약속하는 상위 타입.

    [해결 1] '난다'는 약속을 여기서 뺐다.
        모든 새가 지킬 수 있는 계약(먹기, 이동하기)만 남기면
        어떤 하위 타입도 계약을 깰 이유가 사라진다.

    move() 의 계약
        사전조건: distance 는 0 보다 크다.
        사후조건: 반환값은 '어떻게 이동했는지'를 설명하는 비어 있지 않은 문자열이다.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    def eat(self) -> str:
        return f"{self.name}: 먹이를 먹는다"

    @abstractmethod
    def move(self, distance: int) -> str: ...


class FlyingBird(Bird):
    """'날 수 있는 새'만의 상위 타입. fly() 계약은 여기서 약속한다.

    [해결 2] fly() 계약을 '지킬 수 있는 새들'에게만 요구한다.
    fly(altitude) 의 계약
        사전조건: altitude > 0  (하위 타입이 이보다 까다롭게 받으면 안 된다)
        사후조건: 호출 후 self.altitude == altitude
        불변식  : self.altitude >= 0
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.altitude = 0

    def fly(self, altitude: int) -> None:
        # [해결 3] 사전조건 검사를 상위 타입에 한 번만 둔다.
        #   하위 타입은 _ascend() 만 구현하므로, 실수로 사전조건을 강화할 여지가 줄어든다.
        if altitude <= 0:
            raise ValueError("고도는 0보다 커야 합니다")
        self._ascend(altitude)
        # 사후조건을 코드로 확인(assert)해 두면, 계약을 깨는 하위 타입이 즉시 드러난다.
        assert self.altitude == altitude, f"{self.name}: fly 사후조건 위반"

    def _ascend(self, altitude: int) -> None:
        """기본 구현: 요청 고도로 올라간다. 하위 타입은 '방법'만 바꿀 수 있다."""
        self.altitude = altitude

    def move(self, distance: int) -> str:
        return f"{self.name}: {distance}km 를 날아서 이동"


class Sparrow(FlyingBird):
    pass  # 부모 계약을 그대로 따른다.


class Eagle(FlyingBird):
    # [해결 4] 사후조건을 '강화'하는 것은 허용된다.
    #   요청 고도에 도달한다는 약속은 지키면서, 추가로 '활공 로그'를 남긴다.
    #   (더 많이 주는 것은 괜찮고, 덜 주는 것이 위반이다.)
    def _ascend(self, altitude: int) -> None:
        self.altitude = altitude
        self.glide_log = f"{altitude}m 에서 활공 중"


class Hummingbird(FlyingBird):
    # ([문제 3]의 벌새) "10m 이하만" 같은 사전조건을 더하지 않는다.
    #   날갯짓 방식(정지 비행)은 _ascend() 안에서 바꾸되, 요청 고도에는 도달한다.
    #   고도 제한이 '진짜 요구'라면 하위 타입이 몰래 거절할 것이 아니라
    #   FlyingBird 계약 자체에 최대 고도를 명시해야 한다(모든 클라이언트가 알도록).
    def _ascend(self, altitude: int) -> None:
        self.altitude = altitude
        self.hover = True  # 방법은 달라도 계약(사후조건)은 그대로 지킨다


class Penguin(Bird):
    # [해결 5] 펭귄은 FlyingBird 가 아니므로 fly() 자체가 없다.
    #   '못 하는 일을 예외로 거절'하는 대신, 애초에 약속하지 않는다.
    def move(self, distance: int) -> str:
        return f"{self.name}: {distance}km 를 헤엄쳐서 이동"

    def swim(self) -> str:
        return f"{self.name}: 물속을 헤엄친다"


class Ostrich(Bird):
    def move(self, distance: int) -> str:
        return f"{self.name}: {distance}km 를 달려서 이동"


def migrate(birds: list[FlyingBird], altitude: int) -> list[str]:
    # [해결 6] 클라이언트는 FlyingBird 만 받는다. isinstance 사다리가 사라졌다.
    #   어떤 FlyingBird 하위 타입이 들어와도 fly() 계약이 지켜지므로 그냥 믿고 부른다.
    report: list[str] = []
    for bird in birds:
        bird.fly(altitude)
        report.append(f"{bird.name}: 고도 {bird.altitude}m OK")
    return report


def travel(birds: list[Bird], distance: int) -> list[str]:
    # [해결 7] 모든 새에게 공통으로 시킬 일은 Bird 의 계약(move)만 사용한다.
    #   펭귄·타조·참새 무엇이 와도 치환 가능하다.
    return [bird.move(distance) for bird in birds]


# ----------------------------------------------------------------------
# 요구 변경: "키위(못 남)와 매(남)를 추가해 주세요"
#   - 나쁜 코드: bad_migrate 의 isinstance 검사에 키위를 추가해야 한다(클라이언트 수정).
#   - 개선 코드: 아래 두 클래스만 추가하면 끝. migrate/travel 은 한 줄도 안 바뀐다.
# ----------------------------------------------------------------------

class Kiwi(Bird):
    def move(self, distance: int) -> str:
        return f"{self.name}: {distance}km 를 종종걸음으로 이동"


class Falcon(FlyingBird):
    pass


if __name__ == "__main__":
    print("=== 나쁜 코드: Bird 자리에 하위 타입을 넣으면 ===")
    bad_birds: list[BadBird] = [
        BadSparrow("참새"),
        BadPenguin("펭귄"),
        BadOstrich("타조"),
        BadHummingbird("벌새"),
    ]
    for line in bad_migrate(bad_birds, altitude=100):
        print(" ", line)

    # isinstance 로 펭귄만 막았기 때문에, 펭귄을 직접 부르면 여전히 터진다.
    try:
        BadPenguin("황제펭귄").fly(100)
    except NotImplementedError as e:
        print("  [직접 호출 시 예외]", e)

    print()
    print("=== 개선 코드: 계약을 지킬 수 있는 타입끼리 묶기 ===")
    flyers: list[FlyingBird] = [Sparrow("참새"), Eagle("독수리"), Hummingbird("벌새"), Falcon("매")]
    for line in migrate(flyers, altitude=100):
        print(" ", line)

    everyone: list[Bird] = [Sparrow("참새"), Penguin("펭귄"), Ostrich("타조"), Kiwi("키위")]
    for line in travel(everyone, distance=5):
        print(" ", line)

    # 정적 타입 검사기(mypy 등)라면 migrate([Penguin("펭귄")], 100) 을
    # '실행 전에' 타입 오류로 잡아 준다. 계약 위반이 런타임 사고가 아니라 설계 단계에서 막힌다.
    print("  펭귄에게 fly 가 있나?", hasattr(Penguin("펭귄"), "fly"))
