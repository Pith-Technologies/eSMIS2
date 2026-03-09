# ADR-008: Unified API Audit Log

## Status

Accepted

## Context

The `esmis_api_v2` module (planned) will have two separate audit mechanisms:

1. **esmis.consent.access.log** - Logs read operations (read, search, export) with consent context
2. **esmis.audit.log** (from `esmis_audit`, planned) - Logs data modifications (create, write, unlink) via decorator

This creates several problems:
- Write operations via API don't capture API client context (only Odoo user_id)
- No unified view of all API activity
- Consent information not linked to write operations
- Duplicate/inconsistent logging approaches

## Decision

Create a **unified esmis.api.audit.log** model (planned) that:

1. **Captures all API operations** (read, search, export, create, update, patch)
2. **Records API context** (api_client_id, request_id, ip_address)
3. **Links consent** (via `esmis_consent`, planned) when applicable
4. **Links to esmis.audit.log** (via `esmis_audit`, planned) for field-level change details on write operations
5. **Replaces esmis.consent.access.log** (deprecated, kept for backwards compatibility)

### Model Design

```
esmis.api.audit.log
├── API Context
│   ├── api_client_id → esmis.api.client
│   ├── request_id (correlation ID)
│   ├── ip_address
│   └── user_agent
├── Operation
│   ├── operation: read|search|export|create|update|patch|delete
│   ├── resource_type: individual|group|program|program_membership
│   └── resource_identifier (stable identifier, never DB ID)
├── Consent (optional)
│   ├── consent_id → esmis.consent
│   └── purpose
├── Request Details
│   ├── search_parameters (JSON, for search ops)
│   ├── result_count (for search ops)
│   ├── fields_returned (JSON, for reads with _elements)
│   └── extensions_returned (JSON)
├── Change Tracking (for writes)
│   └── audit_log_id → esmis.audit.log (links to field changes)
├── Result
│   ├── status: success|access_denied|not_found|error
│   └── error_detail
└── Timestamps
    └── timestamp
```

### Integration Points

1. **Read operations**: Log via ApiAuditService from ConsentService.filter_response()
2. **Write operations**: Log from services (IndividualService, GroupService) after successful write
3. **Link to esmis.audit.log**: After create/update, find matching audit log entry by model+res_id+timestamp

### Benefits

- Single source of truth for all API activity
- Complete audit trail: WHO (api_client) accessed/modified WHAT (resource), WHEN, HOW (operation), WHY (consent/purpose)
- Links to detailed field-level changes via esmis.audit.log
- Supports GDPR Article 30 (records of processing) and Article 15 (data subject access requests)

## Consequences

### Positive
- Unified audit view for compliance reporting
- API-specific context preserved for all operations
- Can correlate read and write activity by request_id
- Better security analysis (who accessed what before modifying)

### Negative
- Additional logging overhead (mitigated by async/non-blocking)
- Migration needed for existing esmis.consent.access.log data
- Slight increase in storage requirements

### Migration Path
1. Keep esmis.consent.access.log working (deprecated)
2. New operations use esmis.api.audit.log
3. Provide migration script for historical data (optional)
