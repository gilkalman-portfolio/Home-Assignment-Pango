# Tests – Parkly Parking Manager

## Prerequisites

- Python 3.10+
- Parking Manager running locally on port 5000 (see root README)

## Setup

```bash
pip install pytest playwright pytest-playwright
playwright install chromium
```

## Run

```bash
# All tests
pytest tests/test_parking.py -v

# Headed mode (see the browser)
pytest tests/test_parking.py -v --headed
```

## Test Results at Time of Writing

| Status | Count | Meaning |
|---|---|---|
| ✅ Pass | 11 | Currently working correctly |
| ⚠️ xfail | 6 | Known bugs — will auto-pass once bugs are fixed |

Tests marked `@pytest.mark.xfail` are intentional. They document expected behavior and serve as regression tests — no code change needed when bugs are fixed.

---

## What's Automated & Why

### Scenario 1 – Parking Lifecycle
**Why:** Core business flow — a bug here means incorrect billing or untracked vehicles.

| Test | Status |
|---|---|
| Start parking → success alert and table row | ✅ passes |
| End parking → fee message must not contain "error" (BUG-02) | ⚠️ xfail |
| Start time format → no microseconds (BUG-03) | ⚠️ xfail |
| Duplicate plate → rejected correctly | ✅ passes |
| Empty slot → blocked by HTML5 native validation (not a bug) | ✅ passes |
| Same slot, two cars → should be rejected (BUG-07) | ⚠️ xfail |

### Scenario 2 – License Plate Validation
**Why:** Validation is the gate for all parking operations. Tests cover boundary values (7, 8, 9 digits), character types (letters), and deliberate rules (sequential patterns) — documenting both bugs and confirmed behavior.

| Test | Status |
|---|---|
| Valid non-sequential plate → accepted | ✅ passes |
| Sequential ascending/descending → blocked with explicit message (open product question) | ✅ passes |
| 7-digit plate → rejected | ✅ passes |
| 9-digit plate → rejected | ✅ passes |
| Letters in plate → stripped silently, error message misleading (BUG-06) | ⚠️ xfail |

### Scenario 3 – Authentication
**Why:** Security baseline — access control must always work.

| Test | Status |
|---|---|
| Valid login → dashboard redirect | ✅ passes |
| Invalid credentials → error on login page (BUG-05) | ⚠️ xfail |
| Protected route without auth → redirect to login | ✅ passes |

### Scenario 4 – Mobile Responsiveness
**Why:** Parking attendants commonly use mobile devices.

| Test | Status |
|---|---|
| Login page functional at 390px | ✅ passes |
| Active table no overflow at 390px (BUG-09) | ⚠️ xfail |

---

## Stability Choices

- `get_by_role` / `get_by_text` selectors throughout — resistant to CSS/class changes, based on accessible semantics
- `autouse` fixture handles login and teardown (ends all active sessions after each test)
- `mobile_page` fixture guarantees viewport reset even if a test fails midway
- `xfail` markers keep known-failing tests visible in CI output without polluting pass/fail counts
