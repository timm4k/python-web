from typing import ClassVar


class BrokenTeam:
    members: ClassVar[list[str]] = []

    def __init__(self, name: str) -> None:
        self.name = name

    def add_member(self, member_name: str) -> None:
        self.members.append(member_name)


class CorrectTeam:
    def __init__(self, name: str) -> None:
        self.name = name
        self.members: list[str] = []

    def add_member(self, member_name: str) -> None:
        self.members.append(member_name)


def main() -> None:
    BrokenTeam.members.clear()
    broken_a = BrokenTeam("Perfumers")
    broken_b = BrokenTeam("Designers")
    broken_a.add_member("Elena")
    print(f"Broken shared members: {broken_b.members}")

    correct_a = CorrectTeam("Perfumers")
    correct_b = CorrectTeam("Designers")
    correct_a.add_member("Elena")
    print(f"Correct Perfumers members: {correct_a.members}")
    print(f"Correct Designers members: {correct_b.members}")


if __name__ == "__main__":
    main()
