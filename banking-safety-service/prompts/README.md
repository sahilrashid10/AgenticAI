# Retail Banking Support — Versioned Prompt Library

A versioned prompt library for a Copilot Studio retail-banking customer-support agent.
Each scenario is an independently versioned JSON file. **Git history is the version
control** (rollback, diffs, audit trail), replacing a paid blob store at zero cost.

## Files

| File | Scenario | Purpose |
|------|----------|---------|
| `index.json` | — | Manifest of all scenarios (used for discovery/routing) |
| `balance.json` | Account Balance Inquiry | Balance / available funds for a verified customer |
| `loan.json` | Loan Information & Eligibility | Loan products, indicative eligibility, how to apply |
| `dispute.json` | Transaction Dispute | Report duplicate / unauthorized / fraudulent charges |
| `branch.json` | Branch & ATM Locator | Find branches/ATMs, hours, services |
| `escalation.json` | Escalation to Human Agent | Fallback / handoff to a human |

## Schema (per scenario file)

| Field | Why it exists |
|-------|---------------|
| `id`, `scenario`, `description` | Identity of the prompt |
| `version`, `last_updated`, `author` | **Versioning + audit trail** |
| `intent_triggers` | Phrases that route a query to this scenario |
| `required_slots` | Info the agent must collect before acting (slot filling) |
| `system_prompt` | The behavior given to the model |
| `few_shot_examples` | Demonstrations of desired responses |
| `guardrails` | Safety rules, enforced as output checks |
| `fallback_behavior` | What to do when the scenario can't resolve the request |

## Versioning convention

- Semantic versioning per file: `MAJOR.MINOR.PATCH`.
  - PATCH: wording tweak, no behavior change.
  - MINOR: new examples / slots / guardrails.
  - MAJOR: behavior or scope change.
- Bump the file's `version` **and** `last_updated` in the same commit.
- The commit message is the change log; `git log <file>` is the audit history.

## How it's consumed

Copilot Studio fetches the raw JSON of a scenario over HTTPS (Send HTTP request node),
then uses `system_prompt`, `required_slots`, and `guardrails` at runtime.
