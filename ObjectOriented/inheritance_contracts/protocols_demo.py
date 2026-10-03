from typing import Protocol, runtime_checkable


class Notifier(Protocol):
    def send(self, user_id: int, message: str) -> bool: ...

    def close(self) -> None: ...


class EmailTransport:
    def send(self, user_id: int, message: str) -> bool:
        print(f"Email transport → user {user_id}: {message}")
        return True

    def close(self) -> None:
        print("Email transport closed")


class SlackTransport:
    def send(self, user_id: int, message: str) -> bool:
        print(f"Slack transport → channel {user_id}: {message}")
        return True

    def close(self) -> None:
        print("Slack transport closed")


def send_notification(transport: Notifier, user_id: int, message: str) -> bool:
    return transport.send(user_id, message)


@runtime_checkable
class Drawable(Protocol):
    def draw(self, x: int, y: int) -> None: ...

    def resize(self, factor: float) -> None: ...


class Circle:
    def draw(self, x: int, y: int) -> None:
        print(f"Circle drawn at {x}, {y}")

    def resize(self, factor: float) -> None:
        print(f"Circle resized by {factor:g}")


class Square:
    def draw(self, x: int, y: int) -> None:
        print(f"Square drawn at {x}, {y}")


def main() -> None:
    transports: tuple[Notifier, ...] = (EmailTransport(), SlackTransport())
    for transport in transports:
        print(f"Notification result: {send_notification(transport, 42, 'New scent release')}")
        transport.close()
    print(f"Circle satisfies Drawable: {isinstance(Circle(), Drawable)}")
    print(f"Square satisfies Drawable: {isinstance(Square(), Drawable)}")


if __name__ == "__main__":
    main()
