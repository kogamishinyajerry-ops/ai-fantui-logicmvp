# Engineer-in-the-Loop Streamed Logic Authoring Target

Date: 2026-05-22
Status: strategic product requirement, not current closeout claim

## Target

The generalized logic circuit control panel should not be generated as one
large opaque AI output. The target interaction is an engineer-in-the-loop,
streamed authoring flow where the model proposes one small graph edit at a
time and the user can verify every step.

Acceptance anchor: the model proposes one small graph edit at a time.

This is a trust mechanism. The system should make the model's interpretation
visible before a node, wire, or requirements edit becomes part of the candidate
logic chain.

## Interaction Loop

The future system should run this loop:

1. Read the requirements document and current candidate graph.
2. Propose the next atomic edit: add node, add wire, adjust node, adjust wire,
   group subsystem, or mark ambiguity.
3. Highlight the active node or wire being edited.
4. Show the related requirements document excerpt, interpreted logic, upstream
   and downstream links, and evidence or assumption behind the proposal.
5. Ask the user to confirm whether the node or wire is understood correctly.
6. If the user confirms, commit the edit into the candidate logic graph and
   continue to the next proposed edit.
7. If the user rejects or comments, revise the proposal using both the source
   document and the user's feedback.
8. If the feedback implies that the requirements document itself should change,
   show a separate requirements-document edit proposal.
9. Edit the requirements document only after explicit user authorization.

## Required UI States

The panel should make these states visible:

- reading source document;
- proposing next edit;
- awaiting user confirmation;
- accepted and committed;
- rejected with user feedback;
- revised proposal ready;
- requirements update proposed;
- requirements update authorized;
- requirements update declined;
- blocked by ambiguity.

## Required Provenance

Every pending edit should carry:

- source document section or quote;
- interpreted requirement;
- proposed node or wire id;
- affected upstream and downstream graph context;
- model rationale;
- confidence or ambiguity note;
- user decision record;
- final candidate graph diff.

## Acceptance Shape

A future milestone for this requirement should pass only when:

- a new requirements document can drive at least several streamed graph-edit
  proposals;
- each proposed node or wire is visibly highlighted before commit;
- source text and interpreted logic are shown next to the active edit;
- user confirm commits exactly one candidate graph edit;
- user feedback triggers a revised proposal without losing provenance;
- requirements document edits require explicit authorization;
- the final graph can be replayed as an ordered sequence of confirmed edits.

## Non-Claims

This target does not currently claim:

- fully autonomous logic graph generation;
- automatic requirements document mutation;
- controller truth promotion;
- certification or DAL readiness;
- C919 ETRAS correctness;
- equivalence to aircraft OEM control laws.
