# AI Reflection – Parkly QA Assignment

## Overall Approach & Key Decisions

I started with exploration before planning. Rather than writing test cases from assumptions, I ran the application and interacted with every screen using Playwright — filling forms, clicking buttons, testing boundaries, and reading the actual UI responses. This revealed bugs that only appear through real usage: the fee message showing raw "error" text, the slot uniqueness gap, the silent failure on empty slot, and the login error appearing on the wrong screen.

I then structured the test plan around risk. The parking lifecycle is where money changes hands — I went deepest there. Authentication is a security baseline. Mobile was a deliberate addition because parking management is often done on-site with a phone, not a desktop.

**Key decisions:**

- **Negative testing over happy paths.** Every significant bug I found was in validation or error handling, not in successful flows. I deliberately spent more time on boundaries and failure states.
- **xfail over skip.** Tests for known bugs are marked `@pytest.mark.xfail` rather than skipped. They stay in CI output, document expected behavior, and automatically become passing tests once the bug is fixed — no code change required.
- **Cleanup in fixtures.** The `autouse` fixture ends all active sessions after each test. Without this, tests bleed state into each other and become order-dependent.
- **Open questions flagged explicitly.** Where a behavior is ambiguous (e.g., slot field format), I documented it as an undefined requirement rather than filing it as a bug. QA's job is to surface unknowns, not invent requirements.

## Trade-offs Made

| Decision | Trade-off |
|---|---|
| Focused automation on 4 modules | Didn't automate user management CRUD — lower risk, manual coverage sufficient |
| `get_by_role` selectors | More resilient to HTML changes; requires the app to have reasonable accessibility attributes |
| xfail for known bugs | Tests "fail" in a controlled, documented way; CI dashboards need to understand xfail semantics |
| No API-level testing | App doesn't expose a documented API; focused on the UI layer only |
| Skipped image upload | Low business impact; not worth automation investment in a 24-hour window |
| Mobile tested via viewport resize | Not a true device test; real device emulation with touch events would be more thorough |

## AI Tools & Technologies Used

### Claude (Anthropic) – via Playwright MCP
The most significant tool in this assignment. Claude accessed the running application directly through Playwright browser automation — navigating pages, filling forms, clicking buttons, and reading accessibility snapshots in real time. This meant:

- Bugs were discovered through actual interaction, not described assumptions
- Selectors were extracted from real page structure, not guessed
- Edge cases (duplicate slot, empty slot, mobile overflow, login error placement) were tested against the live app before any test code was written

**What it helped with:** Systematic exploration, real-time bug discovery, test code generation, all markdown documentation.

**Limitations:** Cannot execute `pytest` itself — test runs must be done locally. Cannot observe server logs or network layer directly. Mobile testing was viewport simulation, not real device emulation.

### Playwright (Python)
Chosen for automation because:
- Auto-waiting eliminates the need for manual `sleep` calls — more reliable tests
- `get_by_role` API produces accessible, semantics-based selectors that survive HTML refactors
- Aligns with existing tooling and Python background

### pytest
Standard Python test runner. `autouse` fixtures provided clean setup/teardown with minimal boilerplate. `xfail` markers allowed known-failing tests to remain in the suite without polluting pass/fail counts.

## What I Would Do With More Time

1. **API-level validation** — intercept network requests to confirm server-side validation isn't bypassable (BUG-10 strongly suggests it isn't enforced)
2. **Fee calculation verification** — confirm the billing formula is correct, not just that no error text appears
3. **Real mobile device testing** — test with actual touch events, not just viewport resize
4. **Concurrent session testing** — two browsers simultaneously booking the same slot
5. **Slot format clarification** — once product defines the requirement, add validation tests accordingly

## Most Significant Finding

The most significant finding is a pattern, not a single bug: **error messages consistently appear on the wrong screen**. Both failed login (BUG-05) and failed user deletion (BUG-11) surface their errors on the Dashboard rather than the page where the action occurred. This suggests a systemic issue in how the app handles server responses and redirects — not isolated mistakes.

The second notable finding is BUG-11: user deletion returns `"Cannot delete user with parking sessions."` even when no sessions exist. Combined with BUG-10 (history containing plates that violate current client-side validation), this strongly suggests server-side logic operates independently of the UI's validation rules and may be unreliable. Client-side validation can be bypassed with a direct HTTP request, and the server appears to have its own — incorrect — state assumptions.
