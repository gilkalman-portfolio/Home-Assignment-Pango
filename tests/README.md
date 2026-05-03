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
| ✅ Pass | 8 | Currently working correctly |
| ⚠️ xfail | 9 | Known bugs — will auto-pass once bugs are fixed |

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
| Empty slot → should show validation error (BUG-08) | ⚠️ xfail |
| Same slot, two cars → should be rejected (BUG-07) | ⚠️ xfail |

### Scenario 2 – License Plate Validation
**Why:** Multiple bugs in validation logic affect legitimate input. These tests create a regression suite for when the logic is corrected.

| Test | Status |
|---|---|
| Valid non-sequential plate → accepted | ✅ passes |
| Sequential ascending/descending → should be accepted (BUG-01) | ⚠️ xfail |
| 7-digit plate → rejected | ✅ passes |
| 9-digit plate → rejected | ✅ passes |
| Letters in plate → should show clear error (BUG-06) | ⚠️ xfail |

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

- `get_by_role` selectors throughout — resistant to CSS/class changes, based on accessible semantics
- `autouse` fixture handles login and teardown (ends all active sessions after each test)
- `page.wait_for_url()` after login instead of arbitrary `sleep`
- `xfail` markers keep known-failing tests visible in CI output without polluting pass/fail counts
