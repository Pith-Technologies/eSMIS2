from odoo import Command
from odoo.tests.common import TransactionCase


class TestCampusIsolation(TransactionCase):
    """Tests for campus isolation record rules on student partners and related models.

    Record rules only apply to non-superuser accounts, so these tests create
    dedicated users scoped to specific campuses.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"].with_context(tracking_disable=True)
        cls.EducationHistory = cls.env["esmis.education.history"]
        cls.VocabCode = cls.env["esmis.vocabulary.code"]

        cls.campus_a = cls.env.company
        cls.campus_b = cls.env["res.company"].create({"name": "Campus B Test"})

        cls.level_elementary = cls.VocabCode.get_code("urn:esmis:education-level", "elementary")

        # Create a user at campus A (registrar viewer so they have ACL but are bound by record rules).
        # base.group_user is required for res.partner read access.
        viewer_group = cls.env.ref("esmis_student.group_esmis_registrar_viewer")
        internal_group = cls.env.ref("base.group_user")
        cls.user_campus_a = cls.env["res.users"].create(
            {
                "name": "User Campus A",
                "login": "user_campus_a",
                "company_id": cls.campus_a.id,
                "company_ids": [Command.set([cls.campus_a.id])],
                "group_ids": [Command.set([viewer_group.id, internal_group.id])],
            }
        )
        cls.user_campus_b = cls.env["res.users"].create(
            {
                "name": "User Campus B",
                "login": "user_campus_b",
                "company_id": cls.campus_b.id,
                "company_ids": [Command.set([cls.campus_b.id])],
                "group_ids": [Command.set([viewer_group.id, internal_group.id])],
            }
        )

        # Student at campus A
        cls.student_a = cls.Partner.create(
            {
                "name": "Campus A Student",
                "is_student": True,
                "first_name": "A",
                "last_name": "Student",
                "birthdate": "2000-01-01",
                "company_id": cls.campus_a.id,
            }
        )

        # Student at campus B
        cls.student_b = cls.Partner.create(
            {
                "name": "Campus B Student",
                "is_student": True,
                "first_name": "B",
                "last_name": "Student",
                "birthdate": "2000-01-01",
                "company_id": cls.campus_b.id,
            }
        )

    def test_education_history_campus_isolation(self):
        """Education history at campus A is not visible to a user at campus B."""
        history_a = self.EducationHistory.create(
            {
                "partner_id": self.student_a.id,
                "education_level_id": self.level_elementary.id,
                "school_name": "Campus A School",
            }
        )
        results = (
            self.EducationHistory.with_user(self.user_campus_b)
            .search([("id", "=", history_a.id)])
        )
        self.assertFalse(results, "Campus A education history should not be visible to campus B user")

    def test_student_non_student_partner_always_visible(self):
        """Non-student partners are always visible regardless of campus context."""
        non_student = self.Partner.create({"name": "Vendor Contact", "is_student": False})
        results = (
            self.Partner.with_user(self.user_campus_b)
            .search([("id", "=", non_student.id)])
        )
        self.assertTrue(results, "Non-student partners must be visible across campuses")

    def test_student_at_own_campus_visible(self):
        """A student at campus A is visible to a user at campus A."""
        results = (
            self.Partner.with_user(self.user_campus_a)
            .search([("id", "=", self.student_a.id)])
        )
        self.assertTrue(results, "Student should be visible at their own campus")

    def test_student_at_other_campus_not_visible(self):
        """A student at campus A is not visible to a user at campus B."""
        results = (
            self.Partner.with_user(self.user_campus_b)
            .search([("id", "=", self.student_a.id)])
        )
        self.assertFalse(results, "Campus A student should not be visible to campus B user")
