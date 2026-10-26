"""
3차시 활동 3-6 시작 코드: 기상 관측소 (읽기 중심, 코드를 고치지 않는다)

상황 (판단 근거로 사용):
    - 학교 옥상 기상 관측소 프로그램이다. 매시간 기온을 읽어 기록한다.
    - 센서: 지금은 ThermoSensorV2. 다음 학기에 ThermoSensorV3로 교체할 예정이다.
      V3는 read() 대신 measure_celsius()라는 이름의 메서드를 제공한다고 한다.
    - 저장: CSV 파일. 과학부 선생님이 엑셀로 열어 보며, CSV 외 저장 방식은 계획이 없다.
    - 시험: 센서가 옥상에 있어서 교실에서는 실제 기온을 읽을 수 없다.

활동:
    학습지에 의존 화살표를 그리고, [A]~[E] 표시를 근거로
    "역전할 의존 1개"와 "지금은 역전하지 않을 의존 1개"를 고른다.

실행 방법:
    python3 s3_transfer_weather.py
"""


class ThermoSensorV2:  # [A]
    """옥상 온도 센서 2세대(실제 장치 대신 고정 값을 돌려준다)."""

    def read(self) -> float:
        return 18.5


class CsvWriter:  # [B]
    """한 줄씩 CSV 형식으로 기록한다(실제 파일 대신 리스트에 모은다)."""

    def __init__(self) -> None:
        self.rows: list[str] = []

    def write(self, row: list) -> None:
        line = ",".join(str(v) for v in row)
        self.rows.append(line)
        print(f"  CSV 기록: {line}")


class WeatherStation:
    """관측 정책: 정해진 시각에 기온을 읽어, 기준을 넘으면 '경고'를 붙여 기록한다."""

    HOT = 30.0

    def __init__(self) -> None:
        self.sensor = ThermoSensorV2()  # [C]
        self.writer = CsvWriter()  # [D]

    def record(self, hour: int) -> None:
        temp = self.sensor.read()  # [E]
        status = "경고" if temp >= self.HOT else "정상"
        self.writer.write([hour, temp, status])


if __name__ == "__main__":
    station = WeatherStation()
    for h in (9, 10, 11):
        station.record(h)
