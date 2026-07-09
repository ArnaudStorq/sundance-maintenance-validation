# 12. Cursor & Miro tooling

The meta-workstream: improving the day-to-day tooling used to *do* and *document* the
work.

---

## Cursor AI skills

The engineering workflow was improved using **Cursor's AI Skills** — reusable,
on-demand capabilities the agent reads and follows for specific tasks (creating rules,
hooks, automations, canvases, splitting work into PRs, etc.). In practice this means:

- Codifying repeatable chores (report generation, changelist history extraction,
  documentation like this `Reference/` folder) as skills/prompts rather than ad-hoc
  requests.
- Using the agent to cross-reference the Perforce changelist history
  (`Reports/P4-History/`) against the actual implementation under `D:\Sun` when writing
  documentation — the same method used to produce these reference files.

This documentation repo itself is one output of that workflow: everything is written in
English, grounded in code, and cross-linked to changelists.

---

## Miro

Miro is used for diagrams/boards and is accessed through the **Miro MCP plugin**
(server `plugin-miro-miro`), which exposes tools for boards, diagrams, tables, docs,
images, and comments directly from the agent.

Access notes:

- Boards can be shared **view-only** (embed) for stakeholders who shouldn't edit.
- Editing/creating content requires a **Miro account invitation** to the board.
- Via MCP, the agent can read board context (`context_get` / `context_explore`), create
  diagrams (`diagram_create`), tables (`table_create`), and docs (`doc_create`), and
  read/write comments — useful for turning a design discussion into a durable artifact.

---

## Why this is a "reference" topic

Tooling choices shape how fast the World Partition cleanup can proceed and how well it
is documented. Recording *how* the work is done (skills, MCP access, board sharing)
means the process is reproducible by whoever picks it up next.

## See also

- [`WorkByTopic/README.md`](../WorkByTopic/README.md) — narrative companion to this folder.
- [Reference index](README.md)
