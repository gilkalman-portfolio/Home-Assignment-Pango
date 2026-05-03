# Parkly QA Assignment – Gil Kalman

## Repository Structure

```
├── test-plan.md          # Exploration findings, 28 test cases, bugs found
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

9 active bugs identified across desktop and mobile:

| ID | Bug | Severity |
|---|---|---|
| BUG-02 | "error" string exposed in billing confirmation message | Critical |
| BUG-05 | Login error shown on Dashboard, not on login page | High |
| BUG-07 | Two cars can share the same slot simultaneously | High |
| BUG-04 | "Forgot password" links to cat image site | High |
| BUG-11 | User deletion fails — false "parking sessions" error shown on Dashboard | High |
| BUG-03 | Start time shown with microseconds | Medium |
| BUG-06 | Letters in plate field silently stripped with misleading error message | Medium |
| BUG-09 | Active parking table overflows on mobile (390px) | Medium |
| BUG-10 | History data violates current validation rules (server-side gap) | Low-Medium |

See `test-plan.md` for full details.
