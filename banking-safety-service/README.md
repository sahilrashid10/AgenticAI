# Retail Banking Support Agent — Copilot Studio + Free PII/Safety Stack
![Alt text](Screenshot%202026-05-21%20152315.png)

A customer-support agent for a retail bank, built in **Microsoft Copilot Studio**, backed by a
**free, self-hosted safety + prompt-routing service**. It detects and redacts PII, identifies the
language, routes each query to the right scenario, and answers using a **versioned prompt library
stored as local JSON** — replacing paid Azure services (AI Content Safety, Blob Storage) at zero cost.

> Built as a Day-3 Agentic AI exercise. Use case: *Customer Support Agent for a Retail Banking Client.*

---

## What it demonstrates

| Concept | Where it lives |
|---|---|
| Query rewriting & routing | `route_intent()` in `app.py` matches the message to a scenario |
| Context-aware prompt enhancement | Returns the scenario's `system_prompt` + `required_slots` |
| PII detection (free alt. to Azure AI Content Safety) | Microsoft **Presidio** in `app.py` |
| Language detection | **langdetect** in `app.py` |
| Prompt library & versioning | 5 versioned JSON files; git history = audit trail |
| Local JSON storage (replaces Azure Blob) | `prompts/` folder read at runtime |
| Prompt injection defenses | `guardrails` baked into every scenario prompt |
| Prompt actions & fallback | Scenario prompt drives the reply; no-match → escalation |

---

## Architecture

```
User
 │
 ▼
Copilot Studio Agent  ── HTTP POST /handle ──►  ngrok tunnel  ──►  Local FastAPI service (app.py)
 ▲                                                                   │
 │                                                                   ├─ langdetect      → language
 │                                                                   ├─ Presidio        → detect + redact PII
 │                                                                   ├─ route_intent()  → pick scenario
 │                                                                   └─ load prompt      ← prompts/*.json
 │                                                                   │
 └───────────────  JSON: redacted_text + scenario + system_prompt + guardrails  ◄────────┘
```

- **Copilot Studio** = orchestration / response layer.
- **FastAPI service** = execution layer (PII, language, routing, prompt loading).
- **Prompt library (JSON)** = governance / storage layer, version-controlled in git.

No paid services and no LLM key are required by the backend — Copilot Studio's built-in
generative layer produces the final wording from the loaded prompt.

---

## Repository layout

```
banking-copilot-prompts/        # the versioned prompt library (local JSON; replaces Blob)
    index.json                  #   manifest of scenarios
    balance.json                #   account balance inquiry
    loan.json                   #   loan information & eligibility
    dispute.json                #   transaction dispute
    branch.json                 #   branch & ATM locator
    escalation.json             #   handoff to a human (also the fallback)
    README.md

banking-safety-service/         # the FastAPI backend
    app.py                      #   PII + language + routing + prompt loading
    requirements.txt
    prompts/                    #   a local copy of the JSON library, read at runtime
        index.json
        balance.json … escalation.json
```

> The backend reads prompts from its local `prompts/` folder. GitHub remains the version
> control / audit layer; the local copy is what `app.py` loads at runtime.

---

## Prompt library schema

Each scenario file is a self-describing, independently versioned record:

| Field | Purpose |
|---|---|
| `id`, `scenario`, `description` | Identity of the prompt |
| `version`, `last_updated`, `author` | Versioning + audit trail |
| `intent_triggers` | Phrases used to route a query to this scenario |
| `required_slots` | Info the agent must collect (slot filling) |
| `system_prompt` | Behavior given to the model |
| `few_shot_examples` | Demonstrations of desired responses |
| `guardrails` | Safety rules (PII, cross-customer, injection resistance) |
| `fallback_behavior` | What to do when the scenario can't resolve the request |

Versioning convention: semantic `MAJOR.MINOR.PATCH` per file; bump `version` + `last_updated`
in the same commit; `git log <file>` is the audit history.

---

## Backend setup (Windows)

> Requires Python 3.10–3.13. On Windows, use `py` instead of `python` if the
> Microsoft Store stub intercepts the `python` command.

```powershell
cd banking-safety-service
py -m venv safety-venv
.\safety-venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_lg     # or en_core_web_sm (then set SPACY_MODEL in app.py)
```

Make sure `app.py` has a `prompts\` subfolder beside it containing the 5 scenario JSONs +
`index.json`. Then run:

```powershell
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Python 3.13 note
Presidio supports 3.13, but spaCy's compiled dependency (`thinc`) has occasionally lagged
on new Python releases. If `pip install` or the model download fails with a build/wheel error,
recreate the venv with Python 3.12 (`py -3.12 -m venv safety-venv`) — that only affects the
local Python running the service.

---

## Expose to Copilot Studio (ngrok)

```powershell
ngrok config add-authtoken YOUR_TOKEN   # one-time
ngrok http 8000
```

ngrok prints a public HTTPS URL (e.g. `https://<id>.ngrok-free.dev`). The endpoint Copilot
Studio calls is that URL + `/handle`.

> Free ngrok URLs change on each restart — update the URL in the Copilot Studio HTTP node
> each session.

---

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness → `{"status":"ok"}` |
| GET | `/scenarios` | Lists the loaded prompt library (proves local JSON is read) |
| POST | `/process` | PII redaction + language only (useful for isolated testing) |
| POST | `/handle` | **Full pipeline** — redact → language → route → load prompt (used by the agent) |

Request body for `/process` and `/handle`:
```json
{ "text": "user message here" }
```

Sample `/handle` response:
```json
{
  "language": "en",
  "pii_found": true,
  "entity_count": 1,
  "entities": [{ "type": "IN_AADHAAR", "start": 22, "end": 36, "score": 0.95 }],
  "redacted_text": "I was charged twice, my Aadhaar is <IN_AADHAAR>",
  "scenario": "dispute",
  "scenario_title": "Transaction Dispute",
  "prompt_version": "1.0.0",
  "routed_by_fallback": false,
  "matched_triggers": ["charged twice"],
  "required_slots": [{ "name": "transaction_date", "ask": "What date did the transaction happen?" }],
  "guardrails": ["Never request a full card number, CVV, OTP, or PIN to process a dispute."],
  "system_prompt": "You are a customer-support assistant for the bank..."
}
```

---

## Copilot Studio wiring (summary)

A single topic ("PII Processing") runs on each message:

1. **Set a variable** `Topic.UserText = System.Activity.Text`.
2. **HTTP Request** node:
   - Method: `POST`
   - URL: `https://<ngrok>.ngrok-free.dev/handle`
   - Header: `Content-Type: application/json`
   - Body (formula): `={ text: Topic.UserText }`
   - Response saved as `httpResponse` (schema loaded from a sample `/handle` response)
3. **Message / generative answer** node using `Topic.httpResponse.scenario`,
   `Topic.httpResponse.redacted_text`, and `Topic.httpResponse.system_prompt`.

---

## Example run

Input:
```
I was charged twice, my Aadhaar is 1234 5678 9012
```
Result:
- PII redacted → `... my Aadhaar is <IN_AADHAAR>`
- Routed → `scenario: dispute`
- Agent responds as a dispute handler, asking for the dispute slots (date, amount, merchant)
  and warning against sharing OTP/PIN/CVV (from the scenario's guardrails).

---

## Custom PII recognizers (India)

Beyond Presidio's built-ins (credit card with Luhn check, email, phone), the service adds
`PatternRecognizer`s for `IN_AADHAAR`, `IN_PAN`, `IN_IFSC`, and `IN_PHONE`.

---

## Implemented vs. future work

**Implemented:** versioned prompt library, local JSON storage, PII detection + redaction,
language detection, intent routing, dynamic prompt loading at runtime, prompt guardrails,
fallback to escalation, Copilot Studio integration end-to-end.

**Future work:** persistent storage / database, real identity verification & authentication,
automated ticket creation on escalation, constraining the generative layer so it doesn't
embellish specifics (e.g. invented helpline hours), and multilingual responses driven by the
detected language.

---

## Tech stack

Microsoft Copilot Studio · Python · FastAPI · uvicorn · Microsoft Presidio
(analyzer + anonymizer) · spaCy · langdetect · ngrok · GitHub (versioning)

## Notes

This is a learning/demo project. The generated banking guidance is illustrative and not
real financial advice; the agent intentionally refuses to handle real PII, transactions, or
authentication in chat.
