# Employee Leave Approval Workflow Agent

> **Planning & Reasoning Patterns — Week 1 Assignment**
> A working HR leave-approval agent built on Microsoft Copilot Studio that reasons through requests step by step, applies company policy, and routes long requests to a human approver before finalizing a decision.

![Platform](https://img.shields.io/badge/Platform-Microsoft%20Copilot%20Studio-0078D4)
![Data](https://img.shields.io/badge/Data-Dataverse-742774)
![Calendar](https://img.shields.io/badge/Calendar-Microsoft%20Graph-0078D4)
![HITL](https://img.shields.io/badge/Approval-Teams%20Adaptive%20Card-6264A7)
![Model](https://img.shields.io/badge/Model-Claude%20Sonnet%204.6-D97757)
![Status](https://img.shields.io/badge/Status-Tested%20%E2%9C%93-2E7D32)

---

## Overview
![Alt text](/Screenshot 2026-05-21 152315.png)
![Alt text](/Screenshot 2026-05-21 152259.png)

This project implements an **HR Leave Approval agent** in Microsoft Copilot Studio. An employee submits a leave request in natural language, and the agent:

1. **Checks the leave balance** in Dataverse
2. **Checks calendar availability** via Microsoft Graph (Outlook Calendar)
3. **Applies the leave policy**
4. **Drafts a decision**

Requests of **5 days or fewer** are decided **autonomously**. Requests **longer than 5 days** trigger an **Adaptive Card approval in Teams** that pauses until an HR Manager taps **Approve** or **Reject**.

It is a working implementation of the Week 1 reasoning patterns: **Chain-of-Thought, Least-to-Most decomposition, Policy-Constrained Reasoning, Workflow Decomposition, and Human-in-the-Loop checkpoints.**

---

## Architecture at a Glance

The agent orchestrates four components, each mapping to one stage of the reasoning chain.

| Component | Role in the workflow |
|---|---|
| **Copilot Studio agent** | The orchestrator. Holds the instructions that encode the four-step Chain-of-Thought and the leave policy. Model: Claude Sonnet 4.6. |
| **Dataverse** (`Leave Balances` table) | Source of truth for each employee's leave balance. Queried by email to retrieve total, taken, and remaining days. |
| **Office 365 Outlook** (Graph Calendar) | Queried for events in the requested date window to assess availability and surface conflicts. |
| **Power Automate flow + Teams** | The human-in-the-loop mechanism. Posts an Adaptive Card to the HR Manager and pauses until a person taps Approve or Reject. |

```
Employee request
      │
      ▼
┌─────────────────────────────────────────────┐
│  Copilot Studio Agent  (Chain-of-Thought)    │
│                                              │
│  Step 1  Balance   ──►  Dataverse            │
│  Step 2  Calendar  ──►  Graph / Outlook      │
│  Step 3  Policy    ──►  ≤5 days?             │
│  Step 4  Decision                            │
└───────────────┬──────────────┬───────────────┘
                │              │
        ≤ 5 days│              │ > 5 days
                ▼              ▼
          Auto-decide   Power Automate flow
                          │
                          ▼
                  Teams Adaptive Card  ──►  waits for HR Manager
                          │
                   Approve / Reject
                          │
                          ▼
                  Final decision to employee
```

---

## Reasoning Patterns → Implementation Mapping

This is the core of the assignment: how each theoretical pattern shows up as a concrete, working part of the agent.

| Pattern | Where it lives | Why it matters here |
|---|---|---|
| **Chain-of-Thought (CoT)** | Ordered instructions: balance → calendar → policy → decision | The agent reasons through four explicit steps in sequence rather than jumping to an answer, producing an auditable trail for every decision. |
| **Least-to-Most** | Simplest check first (balance), then availability, then the combined policy judgment | Decomposes the decision into progressively harder sub-questions; each answer feeds the next. |
| **Policy-Constrained Reasoning** | The 5-day rule encoded in instructions | The model cannot auto-approve a request over 5 days. The constraint is enforced as reasoning, not hard-coded branching. |
| **Workflow Decomposition** | Separate tools: Get Leave Balance, Check Calendar Availability, Leave Approval flow | The task is split into discrete, independently testable stages the orchestrator calls in order. |
| **Human-in-the-Loop (HITL)** | Teams Adaptive Card that waits for a response | For requests over 5 days, the decision is suspended until a human taps Approve or Reject. The tap determines the outcome. |
| **Chunking** | Per-employee balance lookup; per-window calendar query | Data is retrieved in targeted slices (one employee, one date range) rather than ingesting everything at once. |

---

## Build Walkthrough (What / With What / Why)

| Step | With what | What & why |
|---|---|---|
| **0 — Environment check** | Copilot Studio, work account | Confirmed a work/school M365 account, agent-creation access, and connector availability — determining that the full Dataverse + Graph + Teams build was possible rather than a simulated fallback. |
| **1 — Data model** | Design (Dataverse) | Designed a single `Leave Balances` table keyed by **employee email**, with total / taken / remaining columns. Email was chosen as the key so the balance lookup, calendar query, and Teams card all reference the same identifier — keeping reasoning consistent across steps. |
| **2 — Create table + agent** | Dataverse, Copilot Studio | Created the table with sample rows and provisioned the blank agent. Two test rows: one with a full balance, one fully exhausted — to exercise both approve and deny paths. |
| **3 — Agent instructions** | Copilot Studio instructions | Wrote the reasoning backbone: the four ordered CoT steps plus the policy rule. This is where Chain-of-Thought and Policy-Constrained Reasoning become actual behavior. |
| **4 — Balance lookup** | Dataverse `List rows` tool | Wired a tool that filters the table by email and returns the balance, making CoT Step 1 a real data lookup. Required resolving Dataverse logical names (see [Implementation Notes](#implementation-notes-gotchas)). |
| **5 — Calendar check** | Office 365 Outlook `Get calendar view of events` | Added a tool querying the calendar for the requested window, turning CoT Step 2 from a narrated guess into a verified query. Confirmed real by having it detect an actual scheduled event. |
| **6 — Policy branch** | Instructions (reasoning) | Verified the agent splits requests at the 5-day threshold. No imperative branching code was needed — the model honored the policy constraint natively. |
| **7 — Teams Adaptive Card** | Power Automate flow + Teams `Post adaptive card and wait for a response` | Built the human-in-the-loop checkpoint. The flow posts a card with Approve / Reject buttons and suspends until a person responds, then returns the decision to the agent. |
| **8 — Decision + notify** | Agent instructions | The agent composes the final message — approved, denied, or approved-by-HR-Manager — and reports the reasoning behind it. |

---

## Agent Instructions (Reasoning Backbone)

These instructions encode the Chain-of-Thought sequence and the policy. They are the heart of the "Planning & Reasoning" portion of the assignment.

```text
You are an HR Leave Approval assistant. When an employee requests leave, reason
through the request step by step, in this exact order, before making any decision:

Step 1 — Identify the employee by their email address and look up their current
leave balance from the Leave Balances table. If they do not have enough remaining
leave to cover the request, deny it and explain the shortfall.

Step 2 — Check the team's calendar availability for the requested dates to see
whether coverage is adequate. Note any conflicts.

Step 3 — Apply the company leave policy: a request of 5 days or fewer may be
decided automatically. A request of more than 5 days must NOT be auto-approved —
it must be escalated to the HR Manager for human sign-off before any approval is given.

Step 4 — Draft a clear decision. State whether the leave is approved, denied, or
pending manager approval, and give the reason based on the balance, the
availability, and the policy.

When a leave request exceeds 5 days, do not state a final decision yourself.
Instead, call the Leave Approval flow to send an Adaptive Card to the HR Manager
in Teams, and wait for the returned decision.

Always explain your reasoning in plain language. Never approve leave that exceeds
the remaining balance. Never auto-approve a request longer than 5 days.
```

---

## The Human-in-the-Loop Flow

When a request exceeds 5 days, the agent calls a Power Automate flow:

1. **Trigger** — `When an agent calls the flow`, receiving three inputs: `EmployeeName`, `LeaveDates`, `NumberOfDays`.
2. **Post adaptive card and wait for a response** — posts a card to the HR Manager's Teams chat with **Approve** and **Reject** buttons, then **suspends the flow until a button is tapped**. *This suspension is the checkpoint.*
3. **Condition** — reads the tapped value from the card response and checks whether it equals `Approve`.
4. **Respond to the agent** — returns `Decision = Approved` (True branch) or `Decision = Rejected` (False branch), which the agent then delivers to the employee.

> Because the flow genuinely pauses, the agent's decision is **not finalized until a human acts** — distinguishing a real HITL checkpoint from one that merely narrates "pending approval."

### Adaptive Card (submit payload)

```json
{
  "type": "AdaptiveCard",
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "version": "1.4",
  "body": [
    { "type": "TextBlock", "text": "Leave Approval Request", "weight": "Bolder", "size": "Large" },
    { "type": "FactSet", "facts": [
      { "title": "Employee:", "value": "<EmployeeName>" },
      { "title": "Dates:", "value": "<LeaveDates>" },
      { "title": "Days:", "value": "<NumberOfDays>" }
    ]},
    { "type": "TextBlock", "text": "This request exceeds 5 days and needs HR Manager sign-off.", "wrap": true }
  ],
  "actions": [
    { "type": "Action.Submit", "title": "Approve", "data": { "decision": "Approve" } },
    { "type": "Action.Submit", "title": "Reject",  "data": { "decision": "Reject" } }
  ]
}
```

---

## Test Scenarios & Results

The assignment specifies two tests — a 3-day request (autonomous) and a 10-day request (human sign-off). Both were run, plus the Reject path to prove the checkpoint is decisive.

| Scenario | Path | Result |
|---|---|---|
| **3-day request** (≤ 5 days) | Autonomous | Balance read from Dataverse, calendar checked, policy passed. Agent auto-approved with no card. CoT Steps 1–4 all fired on real data. |
| **10-day request — Approve** | Human-in-the-loop | Agent declined to auto-decide, called the flow, posted the card to Teams, and waited. On tapping **Approve**, the agent returned "Approved by HR Manager." |
| **10-day request — Reject** | Human-in-the-loop | Same path; on tapping **Reject**, the False branch returned Rejected and the agent delivered a declined outcome. Confirms the tap determines the result. |
| **Calendar conflict detection** | Verification | A request overlapping a real calendar event caused the agent to surface that exact event as an advisory warning — proving Step 2 queries live data rather than guessing. |

---

## Implementation Notes (Gotchas)

Real-world details encountered during the build, recorded for anyone reproducing this:

- **Dataverse naming layers.** Display name, schema name, and logical name differ. OData filters and the `List rows` table input require the **lowercase logical names**, not the friendly display names.
- **Entity set pluralization.** A table whose logical name ends in `s` pluralizes to a double-plural form (`…balances` → `…balanceses`). The **entity set name** — not the logical name — is what the connector's table input expects.
- **Filter field casing.** The email column resolved to a lowercase logical name in the OData filter (`crb3f_employeeemail`), even though its display/schema name was capitalized.
- **Card response parsing.** The `Post adaptive card and wait for a response` action returns the tapped value nested inside its `Body`; the condition reads it via an expression rather than a top-level field.
- **Agent-called flows can't be tested standalone.** Because the trigger expects invocation by the agent, the flow is tested **end-to-end through the agent's test panel**, not the Power Automate Test button.

---

## Possible Extensions

- **Write-back:** add a Dataverse `Update row` action to decrement the balance after approval (currently the post-leave balance is computed in conversation but not persisted).
- **Multi-person availability:** query several team members' calendars and weight team coverage more heavily than a personal event.
- **Tree-of-Thought branching** for borderline cases: explore approve-shorter / propose-alternate-dates / escalate options and select the best.
- **Audit logging:** persist each request and its decision to a Dataverse table for an HR audit trail.

---

## Status

**All assignment requirements implemented and tested** — autonomous (3-day) and human-sign-off (10-day) paths both verified, including Reject.

> **Note on persistence:** the post-approval balance is computed in conversation but not yet written back to Dataverse, so the table value is unchanged after an approval. See [Possible Extensions](#possible-extensions).
