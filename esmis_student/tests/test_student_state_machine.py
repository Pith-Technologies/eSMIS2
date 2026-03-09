from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestStudentStateMachine(TransactionCase):
    """Tests for the student lifecycle state machine.

    Covers all valid transitions and verifies that invalid transitions
    raise UserError with a descriptive message.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"].with_context(tracking_disable=True)

    def _make_student(self, state="applicant"):
        return self.Partner.create(
            {
                "name": "State Test Student",
                "is_student": True,
                "first_name": "State",
                "last_name": "Test",
                "birthdate": "2000-01-01",
                "student_state": state,
            }
        )

    # --- Valid transitions ---

    def test_applicant_to_admitted(self):
        """applicant → admitted is a valid transition."""
        s = self._make_student("applicant")
        s.write({"student_state": "admitted"})
        self.assertEqual(s.student_state, "admitted")

    def test_applicant_to_denied(self):
        """applicant → denied is a valid transition."""
        s = self._make_student("applicant")
        s.write({"student_state": "denied"})
        self.assertEqual(s.student_state, "denied")

    def test_admitted_to_enrolled(self):
        """admitted → enrolled is a valid transition."""
        s = self._make_student("admitted")
        s.write({"student_state": "enrolled"})
        self.assertEqual(s.student_state, "enrolled")

    def test_admitted_to_denied(self):
        """admitted → denied is a valid transition."""
        s = self._make_student("admitted")
        s.write({"student_state": "denied"})
        self.assertEqual(s.student_state, "denied")

    def test_enrolled_to_active(self):
        """enrolled → active is a valid transition."""
        s = self._make_student("enrolled")
        s.write({"student_state": "active"})
        self.assertEqual(s.student_state, "active")

    def test_active_to_enrolled(self):
        """active → enrolled (re-enroll next term) is a valid transition."""
        s = self._make_student("active")
        s.write({"student_state": "enrolled"})
        self.assertEqual(s.student_state, "enrolled")

    def test_active_to_loa(self):
        """active → loa is a valid transition."""
        s = self._make_student("active")
        s.write({"student_state": "loa"})
        self.assertEqual(s.student_state, "loa")

    def test_active_to_graduated(self):
        """active → graduated is a valid transition."""
        s = self._make_student("active")
        s.write({"student_state": "graduated"})
        self.assertEqual(s.student_state, "graduated")

    def test_active_to_dismissed(self):
        """active → dismissed is a valid transition."""
        s = self._make_student("active")
        s.write({"student_state": "dismissed"})
        self.assertEqual(s.student_state, "dismissed")

    def test_active_to_transferred_out(self):
        """active → transferred_out is a valid transition."""
        s = self._make_student("active")
        s.write({"student_state": "transferred_out"})
        self.assertEqual(s.student_state, "transferred_out")

    def test_loa_to_enrolled(self):
        """loa → enrolled (re-enroll) is a valid transition."""
        s = self._make_student("loa")
        s.write({"student_state": "enrolled"})
        self.assertEqual(s.student_state, "enrolled")

    def test_loa_to_dismissed(self):
        """loa → dismissed is a valid transition."""
        s = self._make_student("loa")
        s.write({"student_state": "dismissed"})
        self.assertEqual(s.student_state, "dismissed")

    def test_graduated_to_alumni(self):
        """graduated → alumni is a valid transition."""
        s = self._make_student("graduated")
        s.write({"student_state": "alumni"})
        self.assertEqual(s.student_state, "alumni")

    # --- Invalid transitions ---

    def test_applicant_cannot_go_to_enrolled(self):
        """applicant → enrolled is an invalid transition."""
        s = self._make_student("applicant")
        with self.assertRaises(UserError):
            s.write({"student_state": "enrolled"})

    def test_applicant_cannot_go_to_active(self):
        """applicant → active is an invalid transition."""
        s = self._make_student("applicant")
        with self.assertRaises(UserError):
            s.write({"student_state": "active"})

    def test_enrolled_cannot_go_to_graduated(self):
        """enrolled → graduated is an invalid transition (must pass through active)."""
        s = self._make_student("enrolled")
        with self.assertRaises(UserError):
            s.write({"student_state": "graduated"})

    def test_graduated_cannot_go_to_enrolled(self):
        """graduated → enrolled is an invalid transition."""
        s = self._make_student("graduated")
        with self.assertRaises(UserError):
            s.write({"student_state": "enrolled"})

    def test_alumni_cannot_transition(self):
        """alumni is a terminal state — no further transitions allowed."""
        s = self._make_student("alumni")
        with self.assertRaises(UserError):
            s.write({"student_state": "graduated"})

    def test_dismissed_cannot_transition(self):
        """dismissed is a terminal state — no further transitions allowed."""
        s = self._make_student("dismissed")
        with self.assertRaises(UserError):
            s.write({"student_state": "enrolled"})

    def test_transferred_out_cannot_transition(self):
        """transferred_out is a terminal state — no further transitions allowed."""
        s = self._make_student("transferred_out")
        with self.assertRaises(UserError):
            s.write({"student_state": "applicant"})

    def test_denied_cannot_transition(self):
        """denied is a terminal state — no further transitions allowed."""
        s = self._make_student("denied")
        with self.assertRaises(UserError):
            s.write({"student_state": "applicant"})

    def test_same_state_write_no_error(self):
        """Writing the same state value does not raise an error."""
        s = self._make_student("applicant")
        s.write({"student_state": "applicant"})
        self.assertEqual(s.student_state, "applicant")

    def test_non_student_state_change_no_restriction(self):
        """State transitions are only enforced when is_student=True."""
        partner = self.Partner.create(
            {
                "name": "Not A Student",
                "is_student": False,
                "student_state": "applicant",
            }
        )
        # No UserError — non-student partners bypass the state machine guard.
        partner.write({"student_state": "enrolled"})
        self.assertEqual(partner.student_state, "enrolled")
