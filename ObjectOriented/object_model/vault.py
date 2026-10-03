class SecureVault:
    def __init__(self, owner: str) -> None:
        self.owner = owner
        self._location = "Swiss archive"
        self.__passcode = "1234-5678-super-secret"


def main() -> None:
    vault = SecureVault("Alexander")
    print(f"Public owner: {vault.owner}")
    print(f"Protected location: {vault._location}")
    try:
        print(getattr(vault, "__passcode"))
    except AttributeError as error:
        print(f"Direct private access: {error}")
    mangled_name = "_SecureVault__passcode"
    print(f"Name-mangled access: {getattr(vault, mangled_name)}")
    setattr(vault, mangled_name, "updated-secret")
    print(f"Updated through mangled name: {getattr(vault, mangled_name)}")


if __name__ == "__main__":
    main()
