# Parkly QA Assignment – Gil Kalman

## Repository Structure

```
├── test-plan.md          # Exploration findings, 28 test cases, 10 bugs
├── ai-reflection.md      # Approach, trade-offs, and AI tool usage
└── tests/
    ├── README.md         # How to run + reasoning behind choices
    └── test_parking.py   # Automated test suite (Playwright + pytest)
```

## Quick Start

### 1. Run the application

```bash
docker pull --platform linux/amd64 doringber/parking-manager:3.1.0
docker run --platform linux/amd64 -d -p 5000:5000 --name parking-manager doringber/parking-manager:3.1.0
```

Open: http://localhost:5000  
Credentials: `admin` / `password`

### 2. Run the tests

```bash
pip install pytest playwright pytest-playwright
playwright install chromium
pytest tests/test_parking.py -v
```

---

## Bugs Summary

10 bugs identified across desktop and mobile:

| ID | Bug | Severity |
|---|---|---|
| BUG-02 | Fee message shows raw `error` text alongside correct amount | High |
| ~~BUG-01~~ | Sequential plate rejection — reclassified as Open Question (explicit UI rule, not a bug) | — |
| BUG-07 | Two cars can share the same slot | High |
| ~~BUG-08~~ | Empty slot — closed; HTML5 native validation blocks form with "זהו שדה חובה." | — |
| BUG-05 | Login error shown on Dashboard, not on login page | High |
| BUG-04 | "Forgot password" links to cat image site | High |
| BUG-03 | Start time shown with microseconds | Medium |
| ~~BUG-06~~ | Letters in plate field — closed; error message shown ("must be exactly 8 digits") | — |
| BUG-09 | Active table overflows on mobile (390px) | Medium |
| BUG-11 | User deletion fails — false "parking sessions" error + shown on Dashboard instead of Users page | High |
| BUG-10 | History data violates current validation (server-side gap) | Low-Medium |

See `test-plan.md` for full details.
