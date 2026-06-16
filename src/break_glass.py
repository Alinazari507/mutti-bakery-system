import getpass
from auth import RoleType, User

MANAGER_PINS = {
    "alice": "1234",
    "bob": "5678"
}

def emergency_break_glass() -> User | None:
    print("🚨 EMERGENCY BREAK-GLASS ACCESS 🚨")
    print("Requires two managers' PINs to proceed.")
    manager1 = input("First manager username: ")
    pin1 = getpass.getpass("PIN: ")
    manager2 = input("Second manager username: ")
    pin2 = getpass.getpass("PIN: ")

    if (manager1 in MANAGER_PINS and MANAGER_PINS[manager1] == pin1 and
        manager2 in MANAGER_PINS and MANAGER_PINS[manager2] == pin2 and
        manager1 != manager2):
        print("✅ Emergency access granted. You are now temporarily Mutti (admin).")
        return User("emergency_admin", RoleType.ADMIN)
    else:
        print("❌ Invalid PINs. Access denied. Incident logged.")
        return None