"""
3차시 활동 3-1, 3-2 시작 코드: 한입카페 주문 완료 알림

상황:
    한입카페 주문 프로그램은 음료가 준비되면 고객에게 알림을 보낸다.
    지금은 OrderService(주문 완료 처리)가 EmailSender(이메일 발송)를 직접 만들어 쓴다.

    - 사장님: "손님들이 메일을 잘 안 봐요. 카카오톡 알림으로 바꿉시다."
    - 개발자: "테스트를 돌릴 때마다 진짜 메일이 나가요. 가짜 발송기로 시험하고 싶어요."

활동 3-1 (예측): 코드를 실행하지 말고 먼저 읽는다.
    누가 누구를 알고 있는지 화살표를 학습지에 그리고, 두 요구에서 고칠 위치를 예측한다.
    코드 안의 [A], [B], [C] 표시를 학습지에서 위치 이름으로 사용한다.

활동 3-2 (짝 프로그래밍): 아래 TODO(학생) 1~3을 채운 뒤 다시 실행한다.
    맨 아래 점검 결과가 모두 [통과]가 되면 완료.

실행 방법:
    python3 s3_notifier.py
"""

from typing import Protocol  # TODO(학생) 1에서 사용할 수 있다


# ---------------------------------------------------------------------
# 수단 쪽: 메시지를 "어떻게" 보내는가
# ---------------------------------------------------------------------
class EmailSender:
    """이메일 발송기(실제 발송 대신 print로 흉내 낸다)."""

    def send(self, to: str, msg: str) -> None:
        print(f"  [EMAIL -> {to}] {msg}")


# ---------------------------------------------------------------------
# TODO(학생) 1: OrderService가 필요로 하는 "보내기 약속"을 Protocol로 정의한다.
#   - 이름: MessageSender
#   - OrderService가 실제로 부르는 메서드 모양만 담는다.
#   - 이 자리(OrderService 위)에 쓴다. 아래 OrderService의 타입 힌트가
#     이 이름을 쓰므로, 먼저 정의되어 있어야 실행된다.
# ---------------------------------------------------------------------


# ---------------------------------------------------------------------
# 업무 규칙 쪽: 주문이 완료되면 "무엇을" 하는가
# ---------------------------------------------------------------------
class OrderService:
    """주문 완료 처리: 주문을 완료 상태로 바꾸고 고객에게 알린다."""

    def __init__(self) -> None:
        self.completed: list[int] = []
        self.sender = EmailSender()  # [A]

    def complete_order(self, order_id: int, customer: str) -> None:
        self.completed.append(order_id)  # [B] 업무 규칙: 완료 목록에 기록
        self.sender.send(customer, f"주문 {order_id}번 음료가 준비되었습니다.")  # [C]


# ---------------------------------------------------------------------
# TODO(학생) 2: 위의 OrderService를 직접 고친다.
#   - [A]에서 EmailSender를 직접 만들지 않고, 생성자 매개변수로 발송기를 받는다.
#   - 매개변수 타입 힌트는 구체 클래스가 아니라 TODO 1의 약속으로 쓴다.
#     (점검 5가 이 타입 힌트를 확인한다)
# ---------------------------------------------------------------------


# ---------------------------------------------------------------------
# TODO(학생) 3: 발송기 두 개를 추가한다. (OrderService 코드는 건드리지 않는다)
#   - FakeSender: 실제로 보내지 않고, 보낸 메시지를 self.sent 리스트에 기록한다.
#   - KakaoSender: "[KAKAO -> 받는사람] 메시지" 형태로 출력한다.
# ---------------------------------------------------------------------


# =====================================================================
# 실행 및 점검 (이 아래는 고치지 않는다)
# =====================================================================
def _check(name: str, fn) -> bool:
    try:
        fn()
        print(f"[통과] {name}")
        return True
    except AssertionError as e:
        print(f"[미완성] {name}\n        -> {e}")
    except TypeError as e:
        print(f"[미완성] {name}\n        -> 생성자 모양이 아직 맞지 않습니다 ({e})")
    except NameError as e:
        print(f"[미완성] {name}\n        -> 아직 정의되지 않은 이름을 쓰고 있습니다 ({e})")
    return False


def _need(class_name: str):
    obj = globals().get(class_name)
    assert obj is not None, f"{class_name}이(가) 아직 없습니다. TODO를 확인하세요."
    return obj


def check_protocol() -> None:
    import abc

    sender_cls = _need("MessageSender")
    assert isinstance(sender_cls, type), "MessageSender는 클래스(약속)로 만들어야 합니다."
    is_promise = getattr(sender_cls, "_is_protocol", False) or isinstance(sender_cls, abc.ABCMeta)
    assert is_promise, (
        "MessageSender가 보통 클래스입니다. 2차시처럼 Protocol(또는 ABC)을 상속해 '약속'으로 만드세요."
    )
    assert hasattr(sender_cls, "send"), (
        "MessageSender에 OrderService가 부르는 메서드 모양이 아직 없습니다. [C] 줄을 보세요."
    )


def check_hint() -> None:
    import typing

    sender_cls = _need("MessageSender")
    hints = typing.get_type_hints(OrderService.__init__)
    hints.pop("return", None)
    assert hints, "OrderService.__init__에 발송기 매개변수(와 타입 힌트)가 아직 없습니다."
    for name, hint in hints.items():
        allowed = (hint,) + typing.get_args(hint)  # 'X | None' 같은 경우도 살핀다
        assert sender_cls in allowed, (
            f"매개변수 '{name}'의 타입 힌트가 {getattr(hint, '__name__', hint)}입니다. "
            "구체 클래스가 아니라 약속(MessageSender)으로 써야 의존 방향이 바뀝니다."
        )


def check_fake() -> None:
    fake_cls = _need("FakeSender")
    fake = fake_cls()
    service = OrderService(fake)  # 발송기를 바깥에서 넣어 준다
    service.complete_order(7, "minji@example.com")
    assert hasattr(fake, "sent"), "FakeSender에 sent 리스트가 필요합니다."
    assert len(fake.sent) == 1, f"메시지가 1건 기록되어야 하는데 {len(fake.sent)}건입니다."
    assert "7" in str(fake.sent[0]), "기록된 메시지에 주문 번호 7이 보이지 않습니다."
    assert service.completed == [7], "업무 규칙(완료 목록 기록)이 사라졌습니다."


def check_kakao() -> None:
    kakao_cls = _need("KakaoSender")
    service = OrderService(kakao_cls())
    service.complete_order(8, "010-1234-5678")
    assert service.completed == [8], "카카오 발송기로도 주문 완료가 기록되어야 합니다."


def check_no_direct_creation() -> None:
    import inspect

    src = inspect.getsource(OrderService)
    assert "EmailSender(" not in src, "OrderService 안에서 아직 EmailSender를 직접 만들고 있습니다."


if __name__ == "__main__":
    print("== 현재 동작 ==")
    try:
        service = OrderService()  # 처음 코드: 인자 없이 만든다
    except TypeError:
        service = OrderService(EmailSender())  # TODO 2 이후: 발송기를 바깥에서 넣는다
    service.complete_order(1, "minji@example.com")

    print("\n== 점검 ==")
    results = [
        _check("TODO 1: MessageSender 약속(Protocol/ABC, 보내기 메서드)이 있다", check_protocol),
        _check("TODO 2+3: FakeSender를 주입하면 메시지 1건이 기록된다", check_fake),
        _check("TODO 3: KakaoSender를 주입해도 OrderService는 그대로 동작한다", check_kakao),
        _check("TODO 2: OrderService가 구체 발송기를 직접 만들지 않는다", check_no_direct_creation),
        _check("TODO 2: 발송기 매개변수의 타입 힌트가 약속(MessageSender)이다", check_hint),
    ]
    print(f"\n{sum(results)}/{len(results)} 통과")
