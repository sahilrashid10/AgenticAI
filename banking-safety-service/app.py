"""
Banking Safety Service
=======================
A free, self-hosted replacement for Azure AI Content Safety (PII) plus a language
detector, for the Retail Banking Support agent built in Copilot Studio.

What it does
------------
- PII detection & redaction via Microsoft Presidio (presidio-analyzer + presidio-anonymizer)
- Language detection via langdetect
- Custom recognizers for India-specific identifiers: Aadhaar, PAN, IFSC, Indian mobile

How it's used
-------------
Copilot Studio calls POST /process (over an ngrok HTTPS tunnel) at the top of every
conversation turn. The agent sends the raw user message; the service returns the
detected language and a PII-redacted version of the text, which is what then gets
logged and passed to the LLM. Raw PII never leaves this trust boundary.

Run locally
-----------
    pip install -r requirements.txt
    python -m spacy download en_core_web_lg     # or en_core_web_sm (see SPACY_MODEL)
    uvicorn app:app --host 0.0.0.0 --port 8000
"""

import os
import json
import glob
import re
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from langdetect import detect, DetectorFactory

# Make language detection deterministic (langdetect is randomized by default).
DetectorFactory.seed = 0

# Which spaCy model Presidio loads for NER + tokenization.
#   en_core_web_lg  -> best accuracy, Presidio's default (~560 MB download)
#   en_core_web_sm  -> much smaller/faster (~12 MB); change this AND the spacy download
SPACY_MODEL = "en_core_web_lg"

# Only detect entities relevant to a retail-banking conversation. This both reduces
# false positives (e.g. an Indian phone matching a UK/US recognizer) and avoids running
# irrelevant recognizers. PERSON/LOCATION require the spaCy NER model at runtime.
ALLOWED_ENTITIES = [
    "CREDIT_CARD", "EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "LOCATION",
    "IBAN_CODE", "IP_ADDRESS",
    "IN_AADHAAR", "IN_PAN", "IN_IFSC", "IN_PHONE",
]


# ---------------------------------------------------------------------------
# Prompt library (local JSON) — the zero-cost replacement for Azure Blob Storage.
# index.json lists the scenarios; each scenario file holds its prompt + metadata.
# ---------------------------------------------------------------------------
PROMPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")
DEFAULT_SCENARIO = "escalation"   # fallback when nothing else matches

_library = {}      # {scenario_id: full prompt dict}
_index = {}        # parsed index.json


def load_library():
    """Read index.json + every scenario file from the local prompts folder once.
    This is the 'read from storage' step — local files standing in for Blob."""
    global _library, _index
    _library, _index = {}, {}
    index_path = os.path.join(PROMPTS_DIR, "index.json")
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as f:
            _index = json.load(f)
    for path in glob.glob(os.path.join(PROMPTS_DIR, "*.json")):
        if os.path.basename(path) == "index.json":
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if "id" in data:
            _library[data["id"]] = data
    return _library


def route_intent(text):
    """Pick the best scenario by counting intent_trigger matches in the message.
    Deterministic and explainable: returns (scenario_id, score, matched_phrases)."""
    t = (text or "").lower()
    best_id, best_hits = None, []
    for sid, data in _library.items():
        hits = [p for p in data.get("intent_triggers", []) if p.lower() in t]
        # Prefer the scenario with the most matched phrases; ties broken by
        # longest matched phrase (more specific wins, e.g. 'charged twice' > 'card').
        if hits and (
            len(hits) > len(best_hits)
            or (len(hits) == len(best_hits) and max(map(len, hits)) > (max(map(len, best_hits)) if best_hits else 0))
        ):
            best_id, best_hits = sid, hits
    if best_id is None:
        return DEFAULT_SCENARIO, 0, []
    return best_id, len(best_hits), best_hits


def build_custom_recognizers():
    """India-specific PII patterns Presidio does not ship by default.

    Note: the built-in CREDIT_CARD recognizer already validates card numbers with the
    Luhn checksum, and EMAIL_ADDRESS / PHONE_NUMBER / PERSON / LOCATION come for free.
    These add the local identifiers a retail-banking customer is likely to type.
    """
    return [
        # Aadhaar: 12 digits, optionally grouped 4-4-4  (e.g. 1234 5678 9012)
        PatternRecognizer(
            supported_entity="IN_AADHAAR",
            patterns=[Pattern(name="aadhaar", regex=r"\b\d{4}\s?\d{4}\s?\d{4}\b", score=0.6)],
            context=["aadhaar", "aadhar", "uid"],
        ),
        # PAN: 5 letters + 4 digits + 1 letter  (e.g. ABCDE1234F)
        PatternRecognizer(
            supported_entity="IN_PAN",
            patterns=[Pattern(name="pan", regex=r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", score=0.85)],
            context=["pan"],
        ),
        # IFSC: 4 letters + '0' + 6 alphanumerics  (e.g. HDFC0001234)
        PatternRecognizer(
            supported_entity="IN_IFSC",
            patterns=[Pattern(name="ifsc", regex=r"\b[A-Z]{4}0[A-Z0-9]{6}\b", score=0.85)],
            context=["ifsc", "branch"],
        ),
        # Indian mobile: optional +91, then a 10-digit number starting 6-9
        PatternRecognizer(
            supported_entity="IN_PHONE",
            patterns=[Pattern(name="in_phone", regex=r"(?<![\w+])(?:\+?91[\s\-]?)?[6-9]\d{9}(?!\d)", score=0.5)],
            context=["phone", "mobile", "contact", "call", "number"],
        ),
    ]


def build_analyzer(nlp_engine=None):
    """Construct a Presidio AnalyzerEngine with the built-in + custom recognizers.

    If nlp_engine is provided (e.g. a blank pipeline in tests), it is used as-is;
    otherwise SPACY_MODEL is loaded via NlpEngineProvider.
    """
    if nlp_engine is None:
        provider = NlpEngineProvider(nlp_configuration={
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": SPACY_MODEL}],
        })
        nlp_engine = provider.create_engine()

    engine = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])
    for recognizer in build_custom_recognizers():
        engine.registry.add_recognizer(recognizer)
    return engine


# Lazy singletons so importing this module never triggers a model load
# (the server warms them at startup; tests can inject their own).
_analyzer = None
_anonymizer = None


def get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = build_analyzer()
    return _analyzer


def get_anonymizer():
    global _anonymizer
    if _anonymizer is None:
        _anonymizer = AnonymizerEngine()
    return _anonymizer


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm the engines + load the prompt library at startup.
    get_analyzer()
    get_anonymizer()
    load_library()
    yield


app = FastAPI(title="Banking Safety Service", version="1.0.0", lifespan=lifespan)


class ProcessRequest(BaseModel):
    text: str


def _dedupe_overlaps(results):
    """Keep the highest-confidence entity for any overlapping span; drop the rest.
    This makes the reported entity list match what actually gets redacted."""
    ordered = sorted(results, key=lambda r: (-r.score, r.start))
    kept = []
    for r in ordered:
        overlaps = any(not (r.end <= k.start or r.start >= k.end) for k in kept)
        if not overlaps:
            kept.append(r)
    return sorted(kept, key=lambda r: r.start)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/process")
def process(req: ProcessRequest):
    text = req.text or ""

    # 1) Language detection — reported for routing; the PII scan still runs in English
    #    because regex-based identifiers (card, Aadhaar, PAN, IFSC, phone) are
    #    language-independent.
    try:
        language = detect(text) if text.strip() else "unknown"
    except Exception:
        language = "unknown"

    # 2) PII detection — restricted to banking-relevant entities
    raw_results = get_analyzer().analyze(text=text, language="en", entities=ALLOWED_ENTITIES)
    results = _dedupe_overlaps(raw_results)

    # 3) Redaction — each entity span is replaced with <ENTITY_TYPE>
    redacted = get_anonymizer().anonymize(text=text, analyzer_results=results).text

    entities = [
        {"type": r.entity_type, "start": r.start, "end": r.end, "score": round(r.score, 2)}
        for r in results
    ]

    return {
        "language": language,
        "pii_found": len(results) > 0,
        "entity_count": len(results),
        "entities": entities,
        "redacted_text": redacted,
    }


@app.get("/scenarios")
def scenarios():
    """List the loaded prompt library — proof the local JSON 'storage' is read."""
    return {
        "library_version": _index.get("library_version"),
        "scenarios": [
            {"id": sid, "scenario": d.get("scenario"), "version": d.get("version")}
            for sid, d in _library.items()
        ],
    }


@app.post("/handle")
def handle(req: ProcessRequest):
    """Full pipeline for Copilot Studio in one call:
        redact PII -> detect language -> route to a scenario -> load that prompt.
    Returns the redacted text plus the selected scenario's prompt + guardrails,
    which Copilot Studio uses to generate the reply. No LLM call here (stays free)."""
    text = req.text or ""

    # 1) language
    try:
        language = detect(text) if text.strip() else "unknown"
    except Exception:
        language = "unknown"

    # 2) PII detect + redact (same engines as /process)
    raw_results = get_analyzer().analyze(text=text, language="en", entities=ALLOWED_ENTITIES)
    results = _dedupe_overlaps(raw_results)
    redacted = get_anonymizer().anonymize(text=text, analyzer_results=results).text
    entities = [
        {"type": r.entity_type, "start": r.start, "end": r.end, "score": round(r.score, 2)}
        for r in results
    ]

    # 3) route on the REDACTED text (never route using raw PII)
    scenario_id, score, matched = route_intent(redacted)
    prompt = _library.get(scenario_id, {})

    # 4) return redacted text + the loaded scenario prompt/metadata
    return {
        "language": language,
        "pii_found": len(results) > 0,
        "entity_count": len(results),
        "entities": entities,
        "redacted_text": redacted,
        "scenario": scenario_id,
        "scenario_title": prompt.get("scenario"),
        "prompt_version": prompt.get("version"),
        "routed_by_fallback": score == 0,
        "matched_triggers": matched,
        "required_slots": prompt.get("required_slots", []),
        "guardrails": prompt.get("guardrails", []),
        "system_prompt": prompt.get("system_prompt", ""),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)