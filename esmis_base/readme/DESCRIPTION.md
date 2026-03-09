Common infrastructure for all eSMIS modules. Provides the root eSMIS
configuration menu under Odoo Settings and shared utilities used across
the project.

All eSMIS modules must include `esmis_base` in their dependencies.
Modules requiring a configuration interface should add their menus
under `esmis_base.menu_esmis_root`.
