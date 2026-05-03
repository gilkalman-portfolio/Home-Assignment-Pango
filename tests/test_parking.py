import pytest
from playwright.sync_api import Page, expect


BASE_URL = "http://localhost:5000"
ADMIN_USER = "admin"
ADMIN_PASS = "password"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def login(page: Page) -> None:
    page.goto(f"{BASE_URL}/login")
    page.get_by_role("textbox", name="שם משתמש").fill(ADMIN_USER)
    page.get_by_role("textbox", name="סיסמה").fill(ADMIN_PASS)
    page.get_by_role("button", name="כניסה").click()
    page.wait_for_url(f"{BASE_URL}/")


def start_parking(page: Page, plate: str, slot: str) -> None:
    page.get_by_role("textbox", name="Car Plate").fill(plate)
    page.get_by_role("textbox", name="Slot").fill(slot)
    page.get_by_role("button", name="Start Parking").click()


def end_all_active(page: Page) -> None:
    """End all active sessions to prevent state bleed between tests."""
    page.goto(f"{BASE_URL}/")
    for btn in page.get_by_role("button", name="סיים").all():
        btn.click()
        page.wait_for_timeout(300)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def authenticated_page(page: Page):
    login(page)
    yield page
    end_all_active(page)


# ---------------------------------------------------------------------------
# Module 1 – Authentication
# ---------------------------------------------------------------------------

class TestAuthentication:

    def test_valid_login_redirects_to_dashboard(self, page: Page):
        """TC-01: Successful login lands on dashboard."""
        assert page.url == f"{BASE_URL}/"
        expect(page.locator("text=חניות פעילות נוכחיות")).to_be_visible()

    @pytest.mark.xfail(reason="BUG-05: error currently appears on Dashboard after redirect, not on login page")
    def test_invalid_credentials_error_shown_on_login_page(self, page: Page):
        """TC-02: Wrong credentials should show an error on the login page itself."""
        page.goto(f"{BASE_URL}/logout")
        page.get_by_role("textbox", name="שם משתמש").fill(ADMIN_USER)
        page.get_by_role("textbox", name="סיסמה").fill("wrongpassword")
        page.get_by_role("button", name="כניסה").click()
        # Must stay on login page
        assert "/login" in page.url
        error = (
            page.locator(".alert-danger")
            .or_(page.locator(".error"))
            .or_(page.locator("text=שגיאה"))
        )
        expect(error).to_be_visible()

    def test_protected_route_redirects_unauthenticated(self, page: Page):
        """TC-03: /users must redirect to login when not authenticated."""
        page.goto(f"{BASE_URL}/logout")
        page.goto(f"{BASE_URL}/users")
        expect(page).to_have_url(f"{BASE_URL}/login?next=%2Fusers")


# ---------------------------------------------------------------------------
# Module 2 – License Plate Validation
# ---------------------------------------------------------------------------

class TestLicensePlateValidation:

    def test_valid_non_sequential_plate_accepted(self, page: Page):
        """TC-06: Standard 8-digit plate accepted."""
        start_parking(page, "11223344", "10")
        expect(page.get_by_role("alert")).to_contain_text("Parking started for 11223344")

    @pytest.mark.xfail(reason="BUG-01: sequential plates incorrectly blocked")
    def test_sequential_ascending_plate_should_be_accepted(self, page: Page):
        """TC-07: 12345678 is a valid plate — should NOT be blocked."""
        start_parking(page, "12345678", "11")
        expect(page.get_by_role("alert")).to_contain_text("Parking started for 12345678")

    @pytest.mark.xfail(reason="BUG-01: sequential plates incorrectly blocked")
    def test_sequential_descending_plate_should_be_accepted(self, page: Page):
        """TC-08: 87654321 is a valid plate — should NOT be blocked."""
        start_parking(page, "87654321", "12")
        expect(page.get_by_role("alert")).to_contain_text("Parking started for 87654321")

    def test_seven_digit_plate_rejected(self, page: Page):
        """TC-09: 7-digit plate must be rejected."""
        start_parking(page, "1234567", "13")
        expect(page.locator("text=License plate must be exactly 8 digits")).to_be_visible()

    def test_nine_digit_plate_rejected(self, page: Page):
        """TC-10: 9-digit plate must be rejected."""
        start_parking(page, "123456789", "14")
        expect(page.get_by_role("alert")).not_to_contain_text("Parking started")

    @pytest.mark.xfail(reason="BUG-06: letters silently stripped without feedback")
    def test_letters_in_plate_show_clear_error(self, page: Page):
        """TC-11: Letters should be rejected with a clear error message."""
        start_parking(page, "ABCD1234", "15")
        error = page.locator(".invalid-feedback").or_(page.locator("text=digits only"))
        expect(error).to_be_visible()


# ---------------------------------------------------------------------------
# Module 3 – Parking Lifecycle
# ---------------------------------------------------------------------------

class TestParkingLifecycle:

    PLATE = "33445566"
    SLOT = "99"

    def test_start_parking_creates_active_row(self, page: Page):
        """TC-12: Starting a valid session adds a row to the active table."""
        start_parking(page, self.PLATE, self.SLOT)
        expect(page.get_by_role("alert")).to_contain_text(f"Parking started for {self.PLATE}")
        expect(page.get_by_role("row", name=self.PLATE)).to_be_visible()

    @pytest.mark.xfail(reason="BUG-02: fee message contains raw 'error' text")
    def test_end_parking_fee_message_has_no_error_string(self, page: Page):
        """TC-13: Fee message must not contain the word 'error'."""
        start_parking(page, self.PLATE, self.SLOT)
        page.get_by_role("button", name="סיים").click()
        alert = page.get_by_role("alert")
        expect(alert).to_contain_text(f"Parking ended for {self.PLATE}")
        expect(alert).not_to_contain_text("error")

    @pytest.mark.xfail(reason="BUG-03: start time includes microseconds")
    def test_start_time_has_no_microseconds(self, page: Page):
        """TC-14: Start time in active table must not include microseconds."""
        start_parking(page, self.PLATE, self.SLOT)
        row = page.get_by_role("row", name=self.PLATE)
        start_time_text = row.get_by_role("cell").all()[2].inner_text()
        assert "." not in start_time_text, (
            f"Start time contains microseconds: {start_time_text}"
        )

    def test_duplicate_plate_is_rejected(self, page: Page):
        """TC-15: Same plate started twice must be rejected."""
        start_parking(page, self.PLATE, self.SLOT)
        page.get_by_role("button", name="Close").click()
        start_parking(page, self.PLATE, "88")
        expect(page.get_by_role("alert")).to_contain_text("Duplicate parking prevented")

    @pytest.mark.xfail(reason="BUG-08: empty slot fails silently with no feedback")
    def test_empty_slot_shows_validation_error(self, page: Page):
        """TC-16: Empty slot must show a validation error, not fail silently."""
        page.get_by_role("textbox", name="Car Plate").fill(self.PLATE)
        page.get_by_role("textbox", name="Slot").fill("")
        page.get_by_role("button", name="Start Parking").click()
        expect(page.get_by_role("alert")).to_be_visible()
        expect(page.get_by_role("alert")).not_to_contain_text("Parking started")

    @pytest.mark.xfail(reason="BUG-07: same slot accepted for two different cars")
    def test_same_slot_two_cars_rejected(self, page: Page):
        """TC-17: Two cars cannot occupy the same slot simultaneously."""
        start_parking(page, self.PLATE, self.SLOT)
        page.get_by_role("button", name="Close").click()
        start_parking(page, "44556677", self.SLOT)
        expect(page.get_by_role("alert")).not_to_contain_text("Parking started for 44556677")


# ---------------------------------------------------------------------------
# Module 4 – Mobile Responsiveness
# ---------------------------------------------------------------------------

class TestMobileResponsiveness:

    def test_login_page_usable_on_mobile(self, page: Page):
        """TC-26: Login form must be visible and functional at 390px width."""
        page.set_viewport_size({"width": 390, "height": 844})
        page.goto(f"{BASE_URL}/logout")
        expect(page.get_by_role("textbox", name="שם משתמש")).to_be_visible()
        expect(page.get_by_role("textbox", name="סיסמה")).to_be_visible()
        expect(page.get_by_role("button", name="כניסה")).to_be_visible()
        page.set_viewport_size({"width": 1280, "height": 800})

    @pytest.mark.xfail(reason="BUG-09: active table overflows at 390px viewport")
    def test_active_table_no_overflow_on_mobile(self, page: Page):
        """TC-28: Active parking table must not overflow at 390px width."""
        page.set_viewport_size({"width": 390, "height": 844})
        start_parking(page, "33445566", "5")
        table = page.get_by_role("table")
        table_box = table.bounding_box()
        assert table_box["width"] <= 390, (
            f"Table width {table_box['width']}px exceeds viewport 390px"
        )
        page.set_viewport_size({"width": 1280, "height": 800})
