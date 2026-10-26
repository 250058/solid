"""
5장. DIP(Dependency Inversion Principle, 의존 역전 원칙) 예제

목적:
    알림 서비스(OrderNotifier)가 이메일 발송 '구현'에 직접 묶여 있을 때 생기는 문제를 보고,
    '추상(MessageSender)'에 의존하도록 뒤집어 문제를 해결하는 과정을 보여 준다.

다루는 원칙:
    - 고수준 모듈(업무 규칙: "주문이 완료되면 고객에게 알린다")은
      저수준 모듈(세부 구현: SMTP 이메일, SMS 게이트웨이)에 의존하면 안 된다.
      둘 다 '추상'에 의존해야 한다.
    - 의존성 주입(DI)은 이 원칙을 달성하는 '기법'이다. (원칙 그 자체가 아님)

실행 방법:
    python3 code/chapter_05_dip.py
"""

from abc import ABC, abstractmethod


# =====================================================================
# 나쁜 코드: 고수준 모듈이 저수준 구현(EmailSender)을 직접 만들고 직접 의존한다
# =====================================================================

class SmtpEmailSender:
    """저수준 모듈: '어떻게' 보내는지(SMTP 이메일)라는 세부 사항을 담당한다."""

    def __init__(self, smtp_host: str) -> None:
        self.smtp_host = smtp_host

    def send_email(self, to_address: str, subject: str, body: str) -> None:
        # 실제 SMTP 연결 대신 출력으로 흉내 낸다(외부 라이브러리/네트워크 없이 실행 가능하게).
        print(f"[EMAIL via {self.smtp_host}] to={to_address} | {subject} | {body}")


class BadOrderNotifier:
    """고수준 모듈: '주문 완료 시 고객에게 알린다'는 업무 규칙을 담당한다."""

    def __init__(self) -> None:
        # [문제 1] 고수준 모듈이 저수준 '구현 클래스'를 직접 생성한다.
        #          → SMS로 바꾸거나 서버 주소가 바뀌면 이 업무 클래스를 열어 고쳐야 한다.
        #          → 의존 화살표: BadOrderNotifier ──▶ SmtpEmailSender (구현)
        self.sender = SmtpEmailSender("smtp.cafe-shop.kr")

    def notify_order_completed(self, customer_email: str, order_id: int) -> None:
        # [문제 2] 메서드 이름·인자 형식(send_email, to_address, subject)까지 이메일 전용이다.
        #          → 업무 규칙이 '이메일'이라는 세부 사항의 모양에 오염되어 있다.
        #          → SMS는 제목(subject)이 없고 받는 사람이 전화번호이므로 그대로 갈아끼울 수 없다.
        self.sender.send_email(
            to_address=customer_email,
            subject="주문 완료",
            body=f"주문 #{order_id} 이(가) 완료되었습니다.",
        )
        # [문제 3] 테스트할 때도 진짜 SmtpEmailSender가 만들어진다.
        #          → 실제 메일 서버 없이 '알림이 1번 보내졌는지'를 확인할 방법이 없다.


# =====================================================================
# 개선 코드: 고수준 모듈이 소유한 '추상'에 양쪽 모두 의존한다
# =====================================================================

class MessageSender(ABC):
    """[해결 1] 추상(인터페이스).

    왜 이름이 EmailSender가 아니라 MessageSender인가?
    → 이 추상은 '고수준 모듈이 필요로 하는 것'(누군가에게 메시지를 전달)을 기준으로 정의한다.
      저수준 구현의 모양(SMTP, 제목 등)을 그대로 옮겨 오면 이름만 추상일 뿐 다시 이메일에 묶인다.
    """

    @abstractmethod
    def send(self, recipient: str, message: str) -> None:
        """recipient에게 message를 전달한다. 전달 수단은 구현 클래스가 결정한다."""


class EmailSender(MessageSender):
    """저수준 모듈 1: 추상(MessageSender)을 '구현'한다 → 의존 화살표가 추상 쪽을 향한다(역전)."""

    def __init__(self, smtp_host: str) -> None:
        self.smtp_host = smtp_host

    def send(self, recipient: str, message: str) -> None:
        # 이메일에만 필요한 '제목'은 저수준 모듈 내부 사정으로 숨긴다.
        print(f"[EMAIL via {self.smtp_host}] to={recipient} | 알림 | {message}")


class SmsSender(MessageSender):
    """저수준 모듈 2: 요구 변경('SMS로도 보내 주세요')을 새 클래스 추가만으로 흡수한다."""

    def send(self, recipient: str, message: str) -> None:
        print(f"[SMS] to={recipient} | {message}")


class FakeSender(MessageSender):
    """테스트용 가짜 구현: 실제로 보내지 않고 '보낸 기록'만 남긴다.

    [해결 3] 추상에 의존하기 때문에 테스트에서 이 가짜를 꽂아 넣을 수 있다.
    """

    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    def send(self, recipient: str, message: str) -> None:
        self.sent.append((recipient, message))


class OrderNotifier:
    """고수준 모듈: 업무 규칙만 남고, '어떻게 보내는지'는 전혀 모른다."""

    def __init__(self, sender: MessageSender) -> None:
        # [해결 2] 의존성 주입(DI, 생성자 주입): 필요한 부품을 스스로 만들지 않고 밖에서 받는다.
        #          → 타입 힌트도 구현(EmailSender)이 아니라 추상(MessageSender)이다.
        #          → 이메일↔SMS 교체, 서버 주소 변경 시 이 클래스는 한 줄도 고치지 않는다.
        self.sender = sender

    def notify_order_completed(self, recipient: str, order_id: int) -> None:
        self.sender.send(recipient, f"주문 #{order_id} 이(가) 완료되었습니다.")


def build_notifier(channel: str) -> OrderNotifier:
    """조립 지점(Composition Root): 어떤 구현을 쓸지는 프로그램 '가장자리' 한 곳에서만 결정한다.

    요구가 바뀌어 채널을 추가해도 여기와 새 Sender 클래스만 손대면 된다.
    """
    if channel == "sms":
        return OrderNotifier(SmsSender())
    return OrderNotifier(EmailSender("smtp.cafe-shop.kr"))


if __name__ == "__main__":
    print("=== 나쁜 코드: 이메일에 고정 ===")
    BadOrderNotifier().notify_order_completed("kim@example.com", 101)

    print("\n=== 개선 코드: 같은 OrderNotifier에 구현만 바꿔 끼우기 ===")
    build_notifier("email").notify_order_completed("kim@example.com", 102)
    build_notifier("sms").notify_order_completed("010-1234-5678", 103)

    print("\n=== 개선 코드: 가짜 구현으로 테스트 ===")
    fake = FakeSender()
    OrderNotifier(fake).notify_order_completed("test-user", 104)
    assert fake.sent == [("test-user", "주문 #104 이(가) 완료되었습니다.")]
    print(f"보낸 기록: {fake.sent}")
    print("테스트 통과: 실제 메일 서버 없이 알림 동작을 확인했습니다.")
