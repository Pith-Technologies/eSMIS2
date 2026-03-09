{
    "name": "Consent Management",
    "version": "19.0.1.0.0",
    "category": "eSMIS/Core",
    "summary": "RA 10173 consent management with per-partner, per-purpose tracking",
    "author": "Your Organization",
    "website": "",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": [],
    "depends": ["base", "mail", "esmis_security"],
    "data": [
        "security/ir.model.access.csv",
        "views/consent_views.xml",
        "views/menus.xml",
    ],
    "demo": [
        "demo/demo_consent.xml",
    ],
    "auto_install": False,
    "application": False,
    "installable": True,
}
