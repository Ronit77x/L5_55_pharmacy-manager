# Lab 5: Static Code Analysis — Issue Documentation

**Project:** Pharmacy Management System  
**File analyzed:** `pharmacy_manager.py`  
**Tools:** Pylint, Bandit, Flake8

## Issues Identified and Fixes Applied

| Issue | Type | Original line(s) | Description | Fix approach |
|---|---|---:|---|---|
| Mutable default argument | Code quality / bug | 13 | The `audit=[]` default list could be shared across function calls. | Changed the default to `None` and initialized a new list inside the function. |
| Missing docstrings | Code quality | Multiple | Module and functions lacked documentation. | Added a module docstring and descriptive function docstrings. |
| Invalid function naming | Style | Multiple | Function names used camelCase instead of snake_case. | Renamed functions and updated their calls. |
| Bare exception handler | Code quality / security | 27 | A bare `except` could hide unexpected errors. | Replaced it with explicit handling of the expected missing-key condition. |
| Hardcoded password | Security | 11 | A password was stored directly in source code. | Read the configured password from an environment variable. |
| Unsafe `eval()` | Security | 48 | Arbitrary expression evaluation could execute unintended code. | Replaced it with a restricted arithmetic expression evaluator. |
| Weak MD5 hash | Security | 51 | MD5 is unsuitable for security-sensitive hashing. | Replaced MD5 with SHA-256 for the patient identifier. |
| Unsafe pickle deserialization | Security | 64 | Loading pickle data can execute malicious code if the file is untrusted. | Replaced pickle storage with JSON serialization and deserialization. |
| Shell command execution | Security | 68 | `os.system()` invoked a shell using a string containing the medicine name. | Replaced shell execution with direct output using `print()`. |
| Insecure random number generation | Security | 54 | The standard pseudo-random generator is not intended for security-sensitive identifiers. | Used the `secrets` module for prescription number generation. |
| File resource management | Code quality | 57, 62 | Files were opened and closed manually. | Used `with open(...)` to manage file resources automatically. |
| Formatting violations | Style | Multiple | Unused imports, long lines, and spacing violations were reported. | Removed unused imports and corrected formatting and spacing. |

## Verification

- **Pylint:** Final score of 10.00/10.
- **Bandit:** No issues identified in the final scan.
- **Flake8:** No output in the final scan, indicating no reported violations.

The final version was executed to verify that it could calculate the dosage, generate identifiers, display dispensing labels, save and reload inventory, and print the pharmacy stock report.