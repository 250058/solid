"""2차시 시작 코드: 스마트홈 앱의 기기 제어 (활동 2-7, 낯선 도메인 전이)

사용법
    python3 s2_transfer_smarthome.py

이 파일은 '읽고 실행하는' 활동이다. 코드를 고치지 말고,
# [A] ~ # [F] 표시가 붙은 곳을 학습지에서 판정한다.
(표시가 붙었다고 모두 문제가 있는 것은 아니다.)

표준 라이브러리만 사용, Python 3.12 이상.
"""
from abc import ABC, abstractmethod


class Device(ABC):
    """스마트홈 앱이 모든 기기에 기대하는 약속.

    turn_on()           : 끝나면 is_on 이 True 이고, 기기를 바로 쓸 수 있는 상태다.
    set_volume(level)   : level 은 0~100. 끝나면 volume == level.
    set_color(name)     : name 은 색 이름. 끝나면 color == name.
    lock()              : 끝나면 locked 가 True.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.is_on = False
        self.volume = 0
        self.color = "white"
        self.locked = False

    @abstractmethod
    def turn_on(self) -> None: ...

    @abstractmethod
    def set_volume(self, level: int) -> None: ...

    @abstractmethod
    def set_color(self, name: str) -> None: ...

    @abstractmethod
    def lock(self) -> None: ...


class SmartBulb(Device):
    """거실 전구"""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.brightness = 0

    def turn_on(self) -> None:          # [A]
        self.is_on = True
        self.brightness = 0             # 밝기는 사용자가 나중에 올린다

    def set_volume(self, level: int) -> None:   # [B]
        raise NotImplementedError("전구에는 스피커가 없어요")

    def set_color(self, name: str) -> None:
        self.color = name

    def lock(self) -> None:             # [C]
        pass                            # 전구는 잠글 게 없으니 아무것도 안 한다


class SmartSpeaker(Device):
    """방 스피커"""

    def turn_on(self) -> None:          # [D]
        self.is_on = True
        print(f"    (로그) {self.name} 전원 켜짐 - 부팅 음 재생")

    def set_volume(self, level: int) -> None:   # [E]
        if not 10 <= level <= 50:
            raise ValueError("이 스피커는 10~50 사이만 받아요")
        self.volume = level

    def set_color(self, name: str) -> None:
        raise NotImplementedError("스피커에는 조명이 없어요")

    def lock(self) -> None:
        raise NotImplementedError("스피커는 잠글 수 없어요")


class DoorLock(Device):
    """현관 도어락"""

    def turn_on(self) -> None:
        self.is_on = True

    def set_volume(self, level: int) -> None:   # [F]
        raise NotImplementedError("도어락에는 볼륨이 없어요")

    def set_color(self, name: str) -> None:
        raise NotImplementedError("도어락에는 조명이 없어요")

    def lock(self) -> None:
        self.locked = True


def run(device: Device, action: str, call) -> None:
    try:
        call()
        print(f"  {device.name:<8} {action:<16} -> 성공")
    except Exception as e:
        print(f"  {device.name:<8} {action:<16} -> 예외 {type(e).__name__}: {e}")


if __name__ == "__main__":
    # '외출 모드' 버튼: 앱은 모든 기기에 모든 명령을 보낸다.
    devices: list[Device] = [SmartBulb("거실전구"), SmartSpeaker("방스피커"), DoorLock("도어락")]
    print("== 외출 모드: 모든 기기에 모든 명령 보내기 ==")
    for d in devices:
        run(d, "turn_on()", d.turn_on)
        run(d, "set_volume(0)", lambda d=d: d.set_volume(0))
        run(d, "set_color('red')", lambda d=d: d.set_color("red"))
        run(d, "lock()", d.lock)

    print("\n== 명령 뒤 기기 상태 ==")
    for d in devices:
        extra = f", brightness={d.brightness}" if isinstance(d, SmartBulb) else ""
        print(f"  {d.name:<8} is_on={d.is_on}, volume={d.volume}, color={d.color}, locked={d.locked}{extra}")
