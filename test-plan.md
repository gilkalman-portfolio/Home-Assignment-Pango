# Test Plan – Parkly Parking Manager

## Overview

Parkly is a parking lot management system allowing admins to manage active parking sessions, view history, and manage users. This test plan is based on hands-on exploration of the running application — both desktop and mobile viewports — using Playwright browser automation.

---

## Testing Scope & Prioritization Rationale

### What I chose to test (and why)

| Area | Priority | Reason |
|---|---|---|
| Parking lifecycle (start → end → fee) | Critical | Core business logic; fee errors directly affect revenue and trust |
| License plate validation | High | Gate for all parking operations; bugs here block valid cars or allow garbage data |
| Slot validation & uniqueness | High | Two cars in one slot = physical-world collision; silent failures = data corruption |
| Authentication & access control | High | Security baseline; unauthenticated access is a serious risk |
| Mobile responsiveness | Medium | Parking lots are often managed from phones or tablets |
| User management | Medium | Admin-only; sensitive but lower exposure |
| History display | Low-Medium | Read-only, but data integrity matters for audits |

### What I chose NOT to test (and why)

- Image upload edge cases — low risk, purely cosmetic feature
- Full cross-browser testing — single browser sufficient for this scope
- Performance/load testing — not relevant for a single-lot management tool

---

## Testing Approach

1. **Exploratory first** — mapped the entire application before writing test cases; used browser automation to interact with every screen
2. **Risk-based prioritization** — focused on the parking flow since it involves money
3. **Boundary value analysis** — plate validation (7, 8, 9 digits; letters; sequential patterns), slot field (empty, duplicate)
4. **Negative testing emphasis** — most bugs were in validation and error handling, not happy paths
5. **Auth bypass checks** — verified all routes redirect unauthenticated users correctly
6. **Mobile viewport testing** — tested at 390×844px (iPhone 14 equivalent)

---

## Open Questions / Undefined Requirements

| Field | Question |
|---|---|
| Slot | No documented constraints — currently accepts numbers, letters, or any combination with no limit. Should slot be numeric only? Is there a max length? This needs product clarification before a bug can be filed. |

---

## Test Cases

### Module 1: Authentication

| TC ID | Title | Steps | Expected | Actual |
|---|---|---|---|---|
| TC-01 | Valid login | Enter admin/password, click כניסה | Redirect to Dashboard | ✅ Pass |
| TC-02 | Invalid credentials | Enter admin/wrongpass, click כניסה | Error shown on login page | ❌ Fail – error appears on Dashboard after redirect, not on login page |
| TC-03 | Access protected route without login | Navigate to /users directly | Redirect to login | ✅ Pass |
| TC-04 | Forgot password link | Click "אפשר לאפס כאן" | Password reset flow | ❌ Fail – redirects to https://cataas.com/cat |
| TC-05 | Empty credentials | Submit blank form | Validation error | ❌ Fail – no error shown |

### Module 2: License Plate Validation

| TC ID | Title | Input | Expected | Actual |
|---|---|---|---|---|
| TC-06 | Valid 8-digit plate | `11223344` | Accepted | ✅ Pass |
| TC-07 | Sequential ascending plate | `12345678` | Accepted (valid plate) | ❌ Fail – blocked as "sequential pattern" |
| TC-08 | Sequential descending plate | `87654321` | Accepted | ❌ Fail – blocked as "sequential pattern" |
| TC-09 | 7 digits | `1234567` | Rejected | ✅ Pass |
| TC-10 | 9 digits | `123456789` | Rejected | ✅ Pass |
| TC-11 | Letters in input | `ABCD1234` | Clear error message | ❌ Fail – letters silently stripped to `1234`, no feedback |

### Module 3: Parking Lifecycle

| TC ID | Title | Steps | Expected | Actual |
|---|---|---|---|---|
| TC-12 | Start parking – valid | Valid plate + slot → Start Parking | Success alert; row in table | ✅ Pass |
| TC-13 | End parking fee message | Click סיים | Fee shown cleanly, no "error" text | ❌ Fail – fee amount correct (e.g. ₪4.31) but shows `(חיוב: error)` alongside it; Hebrew label broken |
| TC-14 | Start time format | Start a session | Time shown as YYYY-MM-DD HH:MM | ❌ Fail – microseconds visible: `2026-05-03 09:10:51.733879` |
| TC-15 | Duplicate plate | Same plate twice | Rejected with clear message | ✅ Pass – "Duplicate parking prevented" |
| TC-16 | Empty slot | Valid plate, empty slot → Start | Validation error shown | ❌ Fail – fails silently, no feedback |
| TC-17 | Same slot for two cars | Two plates, same slot number | Rejected – slot occupied | ❌ Fail – both accepted |

### Module 4: User Management

| TC ID | Title | Steps | Expected | Actual |
|---|---|---|---|---|
| TC-18 | Add user – valid | Username + password → Save | User appears in list | ✅ Pass |
| TC-19 | Add user – empty fields | Submit blank form | Validation error | ✅ Pass – HTML5 validation blocks it |
| TC-20 | Add duplicate username | Username = "admin" | Rejected with error | ✅ Pass – silently blocked |
| TC-21 | Delete admin user | Click Delete on admin | Blocked | ✅ Pass |
| TC-22 | Delete non-admin user | Click Delete | User removed | ✅ Pass |
| TC-23 | No confirmation on delete | Click Delete | Confirm dialog shown | ❌ Fail – instant deletion, no confirmation |

### Module 5: History

| TC ID | Title | Expected | Actual |
|---|---|---|---|
| TC-24 | Completed sessions appear | All ended sessions visible | ✅ Pass |
| TC-25 | Data consistent with validation | All plates follow 8-digit rule | ❌ Fail – plates like `dvdsvd`, `453`, `9999` exist in history |

### Module 6: Mobile (390×844px)

| TC ID | Title | Expected | Actual |
|---|---|---|---|
| TC-26 | Login page on mobile | Readable and functional | ✅ Pass |
| TC-27 | Dashboard form on mobile | Fields and buttons accessible | ✅ Pass |
| TC-28 | Active parking table on mobile | Table readable, no overflow | ❌ Fail – 4-column table overflows at 289px content width |

---

## Bugs Found

### BUG-01 – Valid sequential plates incorrectly rejected
**Severity:** High
**Description:** Plates like `12345678` and `87654321` are blocked with "License plate cannot be a sequential pattern." Sequential digits are common in real license plates. The validation logic is overly aggressive and based on an incorrect assumption.
**Impact:** Real vehicles cannot be registered. The system is unusable for a significant category of valid plates.

---

### BUG-02 – Raw "error" string shown alongside fee message
**Severity:** High
**Description:** Ending a parking session shows: `"Parking ended for 99887766. Fee: ₪4.31 (חיוב: error)"`. The fee amount is calculated and displayed correctly in English. However, a secondary Hebrew label (`חיוב`) fails to render and exposes a raw internal `error` string in parentheses.
**Impact:** The fee calculation itself works and revenue is trackable. However, users see the word "error" in a billing context, which damages trust and is confusing. The bug is a broken Hebrew localization/translation component, not a billing logic failure. Downgraded from Critical — the core flow is intact.

---

### BUG-03 – Start time displayed with microseconds
**Severity:** Medium
**Description:** Active parking table shows `2026-05-03 09:10:51.733879` instead of a clean format like `2026-05-03 09:10`.
**Impact:** Poor UX; unreadable in the table, especially on mobile.

---

### BUG-04 – "Forgot password" links to a cat image website
**Severity:** High
**Description:** "אפשר לאפס כאן" navigates to `https://cataas.com/cat`. No password reset flow exists.
**Impact:** Users who forget credentials have no recovery path. Placeholder left in production.

---

### BUG-05 – Login error displayed on wrong screen
**Severity:** High
**Description:** When entering invalid credentials, the app redirects to the Dashboard and shows the error message there instead of on the login page. The user is briefly authenticated (or appears to be) before the error is surfaced.
**Impact:** Confusing and incorrect UX flow. Error context is lost — the user lands on a different page before seeing what went wrong. Could also indicate a session/auth handling issue.

---

### BUG-06 – Letters in plate field silently stripped
**Severity:** Medium
**Description:** Entering `ABCD1234` results in `1234` with no warning. The stripping is silent.
**Impact:** Confusing UX; user doesn't understand why their input changed.

---

### BUG-07 – Two vehicles can occupy the same slot simultaneously
**Severity:** High
**Description:** Starting parking for two different plates with the same slot number succeeds for both. No slot uniqueness validation exists.
**Impact:** In a real parking lot, two cars are directed to the same physical space. Data integrity is violated; slot management is unreliable.

---

### BUG-08 – Empty slot field fails silently
**Severity:** High
**Description:** Submitting Start Parking with an empty Slot field produces no alert and no new row. The failure is completely invisible to the user.
**Impact:** User cannot tell if parking started. Cars may go untracked.

---

### BUG-09 – Active parking table overflows on mobile
**Severity:** Medium
**Description:** At 390px viewport width, the 4-column active table (מספר רכב, מספר חניה, שעת התחלה, פעולה) overflows with no responsive layout or horizontal scroll.
**Impact:** Staff using phones cannot read active sessions or end parking.

---

### BUG-10 – History data violates current validation rules (server-side gap)
**Severity:** Low-Medium
**Description:** History contains plates like `dvdsvd`, `dor123`, `453` — all rejected by current client-side validation. This indicates server-side validation is missing or was added after the data was seeded.
**Impact:** Client-side-only validation can be bypassed via direct API calls. Data integrity is not guaranteed.
