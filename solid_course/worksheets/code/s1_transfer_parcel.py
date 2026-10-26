"""1차시 활동 1-7 시작 코드 — 택배 요금 프로그램 (읽기 중심)

상황
    학교 앞 문구점이 택배 접수 프로그램을 쓴다. 택배사는 세 곳이다.
        fast   : 빠른택배
        cheap  : 알뜰택배
        island : 섬택배(제주·도서 지역 전용)
    문구점 주인은 요금표를 자주 바꾸고, 내년에는 새 택배사도 늘릴 예정이다.
    송장 모양은 택배사 직원이, 접수 기록 저장 방식은 학교 정보 선생님이 관리한다.

활동 방법
    # TODO(학생) 코드는 고치지 않는다. 실행해서 결과를 보고, 코드를 읽으며
    #            주석의 위치 표시 [A]~[F]와 줄 번호를 학습지에 적어 근거를 쓴다.

실행 방법
    python3 s1_transfer_parcel.py
    (접수 기록 파일은 임시 폴더에 만들었다가 지운다.)
"""
from __future__ import annotations

import tempfile
from pathlib import Path


class ParcelService:  # [A]
    """택배 접수 한 건을 처리한다."""

    def __init__(self, sender: str, receiver: str, carrier: str, weight_kg: float) -> None:
        self.sender = sender
        self.receiver = receiver
        self.carrier = carrier
        self.weight_kg = weight_kg

    def fee(self) -> int:  # [B]
        """택배 요금(원)."""
        if self.carrier == "fast":
            return 4000 + int(self.weight_kg * 500)
        elif self.carrier == "cheap":
            return 2500 + int(self.weight_kg * 300)
        elif self.carrier == "island":  # [C]
            return 6000 + int(self.weight_kg * 800)
        else:
            raise ValueError(f"모르는 택배사: {self.carrier}")

    def label_text(self) -> str:  # [D]
        """송장에 찍을 글자."""
        if self.carrier == "fast":  # [E]
            name = "빠른택배"
        elif self.carrier == "cheap":
            name = "알뜰택배"
        else:
            name = "섬택배"
        return (
            f"[{name} 송장]\n"
            f"  보내는 사람: {self.sender}\n"
            f"  받는 사람: {self.receiver}\n"
            f"  무게: {self.weight_kg}kg  요금: {self.fee():,}원"
        )

    def save_log(self, folder: Path) -> Path:  # [F]
        """접수 기록을 파일 끝에 한 줄 덧붙인다."""
        path = folder / "parcel_log.txt"  # Path의 / 는 경로를 이어 붙인다
        with path.open("a", encoding="utf-8") as f:
            f.write(f"{self.sender},{self.receiver},{self.carrier},{self.weight_kg},{self.fee()}\n")
        return path


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        parcels = [
            ParcelService("문구점", "김하늘", "fast", 2.0),
            ParcelService("문구점", "이바다", "cheap", 1.5),
            ParcelService("문구점", "고한라", "island", 3.0),
        ]
        for p in parcels:
            print(p.label_text())
            log = p.save_log(folder)
        print("\n[접수 기록 파일]")
        print(log.read_text(encoding="utf-8"), end="")
