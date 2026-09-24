#!/usr/bin/env python3

def safety_net(action, law, privacy, consent):
    checks = {
        "Law": law,
        "Privacy": privacy,
        "Consent": consent,
    }

    print(f"\nSafety Net → {action}")

    for principle, result in checks.items():
        print(f"{principle}: {result}")

        # Anything other than explicit YES is a denial.
        if result != "YES":
            print(f"DECISION: NO")
            print(f"REASON: {principle} is not confirmed.")
            return False

    print("DECISION: YES")
    print("All three requirements confirmed.")
    return True


def main():
    action = input("Action: ")

    law = input("Law [YES/NO/UNKNOWN]: ").upper()
    privacy = input("Privacy [YES/NO/UNKNOWN]: ").upper()
    consent = input("Consent [YES/NO/UNKNOWN]: ").upper()

    if safety_net(action, law, privacy, consent):
        print(f"Executing: {action}")
        # Put the actual operation here.
    else:
        print("Action blocked.")


if __name__ == "__main__":
    main()
