"""2차시 시작 코드: 생물 시뮬레이션 동아리의 '새 날리기' 프로그램 (활동 2-1, 2-2)

사용법
    python3 s2_birds.py

순서
    1. 실행하기 전에 학습지 활동 2-1 예측표를 먼저 채운다.
    2. 실행해서 출력을 학습지 활동 2-2 관찰 칸에 옮겨 적는다.
    3. 이 파일의 클래스 구조는 고치지 않는다. (읽고 실행하는 활동)

표준 라이브러리만 사용, Python 3.12 이상.
"""
from abc import ABC, abstractmethod


class Bird(ABC):
    """동아리 프로그램의 모든 새가 따라야 하는 '쓰는 쪽과의 약속'.

    fly(altitude) 의 약속
        - 받는 조건  : altitude 는 0보다 큰 정수이면 된다.
        - 끝난 뒤 보장: 호출이 끝나면 self.altitude == altitude 이다.
        - 항상 참    : self.altitude 는 언제나 0 이상이다.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.altitude = 0          # 처음에는 땅 위(고도 0)

    @abstractmethod
    def fly(self, altitude: int) -> None:
        """altitude 높이까지 날아오른다."""


class Sparrow(Bird):
    """참새: 낮게, 빠르게 난다."""

    def fly(self, altitude: int) -> None:
        self.altitude = altitude
        print(f"  {self.name}: 파닥파닥 {altitude}m")


class Eagle(Bird):
    """독수리: 높이 올라가며 날개를 크게 편다."""

    def fly(self, altitude: int) -> None:
        print(f"  {self.name}: 날개를 활짝 편다")
        self.altitude = altitude
        print(f"  {self.name}: 활공하며 {altitude}m")


class Penguin(Bird):
    """펭귄: 현실에서도 분명히 새다."""

    def fly(self, altitude: int) -> None:
        # 펭귄은 날 수 없으니 그냥 넘어간다.
        print(f"  {self.name}: (뒤뚱뒤뚱 걷기만 한다)")


class RubberDuckToy(Bird):
    """동아리 부원이 만든 오리 모양 장난감 드론.
    프로펠러가 커서 너무 낮게 뜨면 바닥에 부딪힌다.
    """

    def fly(self, altitude: int) -> None:
        if altitude <= 10:
            raise ValueError("장난감 드론은 10m보다 높게만 뜰 수 있어요")
        self.altitude = altitude
        print(f"  {self.name}: 위이잉 {altitude}m")


def launch_all(birds: list[Bird], altitude: int = 5) -> None:
    """동아리 프로그램의 핵심 기능: 모든 새를 같은 높이로 날리고 고도를 기록한다.

    이 함수는 어떤 새가 들어오는지 모른다. Bird 의 약속만 믿는다.
    """
    print(f"[launch_all] 모두 {altitude}m 로 날린다")
    for bird in birds:
        try:
            bird.fly(altitude)
        except Exception as e:  # 예외도 결과로 기록한다
            print(f"  -> {bird.name}: 예외 발생 ({type(e).__name__}: {e})")
            continue
        kept = bird.altitude == altitude and bird.altitude >= 0
        mark = "약속 지킴" if kept else "약속 깨짐"
        print(f"  -> {bird.name}: 기록된 고도 {bird.altitude}m  [{mark}]")


if __name__ == "__main__":
    # TODO(학생) 실행 전에 학습지 활동 2-1 예측표를 먼저 채웠는지 확인하세요.
    birds = [Sparrow("참새"), Eagle("독수리"), Penguin("펭귄"), RubberDuckToy("오리드론")]
    launch_all(birds)

    # TODO(학생) 아래 줄의 주석(#)을 지우고 높이를 바꿔 다시 실행해 보세요. (활동 2-2 질문 ④)
    # launch_all([Sparrow("참새2"), RubberDuckToy("오리드론2")], altitude=20)
