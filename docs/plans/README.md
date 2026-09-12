# eSMIS Build Plans

A plan says what we intend to build and how. It is time-bound and owned, and
once the work ships it becomes history: nobody returns to tick the boxes. That
is why plans live here rather than in [architecture](../architecture), which
has to stay true.

## Naming

**Name a plan after its subject, not its position in a sequence.**

```
academic-term-plan.md          good
phase-1c-plan.md               avoid
```

A sequence position is a slot, and slots are guessable. Two people working in
separate worktrees will both reach for "the 1c plan", write different documents
at the same path, and collide when the second one opens a pull request. Nothing
is lost, git reports it as a conflict, but resolving two unrelated documents at
one path is miserable and entirely avoidable.

A subject cannot collide unless two people are genuinely planning the same
thing. In that case the collision is doing its job: it has found duplicated
effort that needed finding.

Sequence positions go stale for a second reason. Phases get split, reordered
and renumbered. A file called `phase-1c-plan.md` for work that ends up in
phase 2 is wrong and cannot be renamed without breaking every link to it.

**The phase belongs inside the document**, on the status line, where it can be
corrected without renaming anything.

## Status line

Every plan carries a status on the second line, so a reader knows in one glance
whether they are reading intent, a commitment, or history.

```
Status: DRAFT — awaiting sign-off on the decisions in section 3
Status: ACCEPTED — Phase 1C. Building now
Status: COMPLETE. Shipped as esmis_academic_term; the unticked boxes below are
a record of intent, not a backlog
```

A finished plan says so at the top. Leaving a hundred unticked boxes with no
status is how a plan gets mistaken for a backlog.

## Existing files

`phase-1-plan.md` and `phase-1b-plan.md` predate this convention. Both are
COMPLETE, so they are history and renaming them would break links for no gain.
New plans use subject names.

| Plan | Covers | Status |
| --- | --- | --- |
| [implementation-plan.md](implementation-plan.md) | Pre-implementation improvements | Complete |
| [phase-1-plan.md](phase-1-plan.md) | Foundation layer, Phase 1A | Complete |
| [phase-1b-plan.md](phase-1b-plan.md) | Student profile and address modules | Complete |
