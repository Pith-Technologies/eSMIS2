from odoo import Command
from odoo.tests.common import TransactionCase


class TestSecurityGroups(TransactionCase):
    """Tests for esmis_security group hierarchy."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_officer = cls.env["res.users"].create(
            {
                "name": "Security Officer",
                "login": "test_security_officer",
                "password": "test_security_officer",
                "group_ids": [
                    Command.set(
                        [
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("esmis_security.group_esmis_security_officer").id,
                        ]
                    )
                ],
            }
        )
        cls.user_dpo = cls.env["res.users"].create(
            {
                "name": "DPO User",
                "login": "test_dpo_user",
                "password": "test_dpo_user",
                "group_ids": [
                    Command.set(
                        [
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("esmis_security.group_esmis_dpo").id,
                        ]
                    )
                ],
            }
        )

    def test_group_hierarchy_viewer_implied_by_officer(self):
        """Security Officer implies Security Viewer."""
        self.assertTrue(self.user_officer.has_group("esmis_security.group_esmis_security_viewer"))

    def test_group_hierarchy_officer_implied_by_manager(self):
        """Security Manager implies Security Officer and Viewer."""
        user_manager = self.env["res.users"].create(
            {
                "name": "Security Manager",
                "login": "test_security_manager_grp",
                "password": "test_security_manager_grp",
                "group_ids": [
                    Command.set(
                        [
                            self.env.ref("base.group_user").id,
                            self.env.ref("esmis_security.group_esmis_security_manager").id,
                        ]
                    )
                ],
            }
        )
        self.assertTrue(user_manager.has_group("esmis_security.group_esmis_security_officer"))
        self.assertTrue(user_manager.has_group("esmis_security.group_esmis_security_viewer"))

    def test_dpo_implies_security_viewer(self):
        """DPO implies Security Viewer."""
        self.assertTrue(self.user_dpo.has_group("esmis_security.group_esmis_security_viewer"))

    def test_system_admin_group_implies_base_system(self):
        """eSMIS System Admin implies base.group_system."""
        user_admin = self.env["res.users"].create(
            {
                "name": "System Admin",
                "login": "test_system_admin_grp",
                "password": "test_system_admin_grp",
                "group_ids": [
                    Command.set(
                        [
                            self.env.ref("base.group_user").id,
                            self.env.ref("esmis_security.group_esmis_system_admin").id,
                        ]
                    )
                ],
            }
        )
        self.assertTrue(user_admin.has_group("base.group_system"))

    def test_audit_viewer_implied_by_audit_officer(self):
        """Audit Officer implies Audit Viewer."""
        user_audit_officer = self.env["res.users"].create(
            {
                "name": "Audit Officer",
                "login": "test_audit_officer_grp",
                "password": "test_audit_officer_grp",
                "group_ids": [
                    Command.set(
                        [
                            self.env.ref("base.group_user").id,
                            self.env.ref("esmis_security.group_esmis_audit_officer").id,
                        ]
                    )
                ],
            }
        )
        self.assertTrue(user_audit_officer.has_group("esmis_security.group_esmis_audit_viewer"))
