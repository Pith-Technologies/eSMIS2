# eSMIS Research

Research documents compiled for the eSMIS (Student Management Information System) project.
These inform architectural decisions and implementation planning.

## Documents

| Document | Scope | Key Findings |
|----------|-------|--------------|
| [Philippine Regulatory Landscape](philippine-smis-regulatory-landscape.md) | Laws, CHED CMOs, Data Privacy Act, accreditation | 20+ laws/regulations mapped; compliance checklist; HEMIS reporting requirements |
| [External System Integrations](external-system-integrations.md) | PhilSys, CHED, UniFAST, payments, LMS, gov't agencies | PhilSys + payment gateways have real APIs; most gov't systems are portal/file-based |
| [SIS Best Practices](sis-best-practices.md) | Architecture, data models, security, UX, API standards | 14 core modules; 18 custom Odoo models; 6-phase implementation roadmap |

## Key Takeaways

### Regulatory Compliance (Philippine)

- **20+ laws and regulations** govern student data, enrollment, grading, and financial aid
- **RA 10173 (Data Privacy Act)** requires PIA, DPO, breach notification, consent management
- **RA 10931 (Free Tuition Law)** requires citizenship verification, prior degree tracking, subsidy reporting
- **CHED HEMIS** requires annual data submission (Excel-based, 4-7 forms depending on institution type)
- **Accreditation** (AACCUP/PACUCOA/PAASCU) requires trend data, grade distributions, retention rates

### Integration Landscape

- **Real APIs available**: PhilSys (QR + biometric), PayMongo/Maya/Dragonpay, LMS via LTI 1.3/OneRoster
- **Portal/file-based only**: CHED HEMIS, eCAV, UniFAST/TES, DOST-SEI, BIR, SSS, GSIS, PhilHealth, Pag-IBIG
- **Watch**: eGov PH Super App planned to unify SSS/PhilHealth/Pag-IBIG APIs by Q4 2025
- **Strategy**: Build file export modules for government systems; real API integration for PhilSys and payments

### Architecture

- **14 core functional modules** covering full student lifecycle
- **18 custom Odoo models** needed (no Odoo equivalent)
- **Multi-campus**: Use Odoo's native multi-company (`res.company` per campus)
- **Country-specific**: `esmis_*_ph` modules for Philippine grading, CHED codes, government scholarships
- **6-phase implementation**: Foundation → Core Operations → Financial → Extended → Portals → Integrations

### Research Gaps

See Appendix C in the regulatory document for 8 areas needing further investigation,
primarily around CHED API specifications and accreditation manual details that require
direct agency engagement.
