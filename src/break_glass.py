import getpass
from auth import User, RoleType

# In a production environment, these should be stored as hashed secrets, 
# not plain text in the source code.
MANAGER_PINS = {
    "alice": "1234",
    "bob": "5678"
}

def emergency_break_glass(log_callback) -> Optional[User]:
    """
    Implements a two-person authorization rule for emergency administrative access.
    """
    print("\n" + "=" * 50)
    print("           EMERGENCY BREAK-GLASS ACCESS         ")
    print("=" * 50)
    print("Requires validation from two managers to proceed.")
    
    manager1 = input("First manager username: ").strip().lower()
    pin1 = getpass.getpass("PIN: ")
    manager2 = input("Second manager username: ").strip().lower()
    pin2 = getpass.getpass("PIN: ")

    # Verify both credentials and ensure two distinct managers are provided
    if (manager1 in MANAGER_PINS and MANAGER_PINS[manager1] == pin1 and
        manager2 in MANAGER_PINS and MANAGER_PINS[manager2] == pin2 and
        manager1 != manager2):
        
        log_callback("BREAK_GLASS", f"{manager1},{manager2}", "Emergency administrator privileges authorized")
        print("\n✔ Emergency authorization verified. Privileges elevated to Admin (Mutti).")
        return User("emergency_admin", RoleType.ADMIN)
    
    else:
        log_callback("BREAK_GLASS_FAILED", f"{manager1},{manager2}", "Unauthorized dual-PIN attempt")
        print("\n❌ PIN validation failed. Incident logged to security logs.")
        return None