# eSMIS Runbooks

Operational procedures. A runbook is followed, not read: someone opens it while
something is happening, often with a regulatory clock running. That is why these
are separate from [guides](../guides), which you read to learn how to build
something.

Each runbook states its trigger, the deadline if one applies, and the steps in
the order they must happen.

| Runbook | Trigger | Deadline |
| --- | --- | --- |
| [Data Breach Response](breach-response.md) | A personal data breach is discovered | Notify the NPC within 72 hours (RA 10173) |
| [Government Export](government-export.md) | A CHED HEMIS, eCAV or UniFAST submission is due | Per the reporting calendar |
| [Security Audit](security-audit.md) | Before declaring a module complete, and on a schedule | None, but it gates module completion |
| [Multi-Campus Setup](multi-campus-setup.md) | Onboarding an institution with more than one campus | None |

## Writing a new runbook

State the trigger in the first line. Number the steps. Put the deadline and who
must be told near the top, not buried at the end. Anything that needs a
decision from a person should say who decides.

If a document explains how something works rather than what to do about it, it
belongs in [guides](../guides) or [principles](../principles).
