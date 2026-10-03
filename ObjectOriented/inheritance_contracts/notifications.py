from abc import ABC, abstractmethod


class BaseNotifier(ABC):
    @abstractmethod
    def send(self, user_id: int, message: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    def send_bulk(self, user_ids: list[int], message: str) -> dict[int, bool]:
        return {user_id: self.send(user_id, message) for user_id in user_ids}


class EmailNotifier(BaseNotifier):
    def __init__(self, transport: str) -> None:
        self.transport = transport
        self.closed = False

    def send(self, user_id: int, message: str) -> bool:
        if self.closed:
            raise RuntimeError("Notifier is closed")
        print(f"[EMAIL:{self.transport}] → user {user_id}: {message}")
        return True

    def close(self) -> None:
        self.closed = True


class SmsNotifier(BaseNotifier):
    def __init__(self, sender: str) -> None:
        self.sender = sender
        self.closed = False

    def send(self, user_id: int, message: str) -> bool:
        if self.closed:
            raise RuntimeError("Notifier is closed")
        print(f"[SMS:{self.sender}] → user {user_id}: {message}")
        return True

    def close(self) -> None:
        self.closed = True


class IncompleteNotifier(BaseNotifier):
    def send(self, user_id: int, message: str) -> bool:
        return True


def instantiation_error(class_type: type[object]) -> str:
    try:
        class_type()
    except TypeError as error:
        return str(error)
    raise RuntimeError("Abstract notifier unexpectedly instantiated")


def main() -> None:
    print(f"BaseNotifier protection: {instantiation_error(BaseNotifier)}")
    print(f"Incomplete protection: {instantiation_error(IncompleteNotifier)}")
    email_notifier = EmailNotifier("smtp")
    sms_notifier = SmsNotifier("Atelier")
    print(f"Nominal contract: {isinstance(email_notifier, BaseNotifier)}")
    print(f"Email bulk result: {email_notifier.send_bulk([101, 102], 'Your perfume is ready')}")
    print(f"SMS result: {sms_notifier.send(103, 'Your perfume has shipped')}")
    print(f"Base abstract methods: {sorted(BaseNotifier.__abstractmethods__)}")
    print(f"Email abstract methods: {sorted(EmailNotifier.__abstractmethods__)}")
    email_notifier.close()
    sms_notifier.close()


if __name__ == "__main__":
    main()
