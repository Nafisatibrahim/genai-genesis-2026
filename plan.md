# FlexCare — Project Plan

Step-by-step plan for building the AI Musculoskeletal Recovery Assistant (FlexCare): symptom intake with body map, multi-agent assessment, safety checks, recovery suggestions, and referral guidance.

---

## 1. Architecture Overview

### High-level flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER                                            │
│  • Body map (tap regions + pain level → heat visualization)                 │
│  • Optional: free-text description                                           │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INTAKE LAYER                                         │
│  • Collect: body map data (regions + levels) + optional chat                 │
│  • Output: structured payload for pipeline                                  │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION / PIPELINE                                  │
│  Linear: Assessment → Safety → [Recovery | Referral] → Response             │
│  (Safety gates: if red flags → skip Recovery, go to Referral/Urgent)         │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  Assessment     │       │  Safety          │       │  Recovery        │
│  Agent          │       │  Agent/Tool      │       │  Agent           │
│  • Structured   │       │  • Rule-based    │       │  • Stretches     │
│    output       │       │    red flags     │       │  • Posture       │
│  • Summary +    │       │  • Output:       │       │  • (Optional     │
│    risk level   │       │    safe | soon   │       │    RAG over      │
│                 │       │    | urgent      │       │    exercise KB)  │
└─────────────────┘       └─────────────────┘       └─────────────────┘
          │                           │                           │
          │                           ▼                           │
          │               ┌─────────────────┐                     │
          │               │  Referral        │                     │
          └──────────────►│  Agent           │◄────────────────────┘
                          │  • physio |      │
                          │    chiro |       │
                          │    massage |     │
                          │    urgent        │
                          └────────┬────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RESPONSE TO USER                                     │
│  • Recommendation + "Why this recommendation?" (+ optional session summary)   │
│  • Escalation message if Safety said urgent / see professional              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Stack

| Layer        | Tech |
|-------------|------|
| Frontend    | React (Vite) + Tailwind; body map via **react-muscle-highlighter** (see [Tools & libraries](#tools--libraries)) |
| Backend     | Python FastAPI (or Node); single API that runs the pipeline |
| AI / Agents | Railtracks (Gemini); agents + tools; optional RAG (ChromaDB) later |
| State (MVP) | In-memory or session; optional SQLite/Supabase for progress later |

### Tools & libraries

- **Body map (frontend):** [react-muscle-highlighter](https://github.com/soroojshehryar/react-muscle-highlighter) — React component library for interactive human body anatomy (male/female, front/back views, clickable muscle/body regions, intensity levels). Used for the FlexCare body map; region IDs are mapped to our intake schema in `frontend/src/constants/regions.js`.

---

## 2. Phase 0 — Setup & Conventions

| Step | Task | Details |
|------|------|---------|
| 0.1 | Repo structure | Create `frontend/`, `backend/`, `agents/` (or `backend/agents/`), `docs/`, `demo/`. |
| 0.2 | Env & config | `.env` for API keys (Gemini, optional OpenAI for embeddings); never commit `.env`. |
| 0.3 | Naming | Product name: **FlexCare**. Code/docs use FlexCare consistently. |
| 0.4 | Safety disclaimer | One source of truth for "not a diagnostic tool" copy; use in UI and docs. |

---

## 3. Phase 1 — Data & Schema

| Step | Task | Details |
|------|------|---------|
| 1.1 | Body map regions | Define list of regions (e.g. neck, upper_back, lower_back, left_shoulder, right_shoulder, etc.). Assign IDs for API and DB. |
| 1.2 | Pain level scale | Define scale (e.g. 1–5 or 1–10). Same scale for all regions. |
| 1.3 | Intake schema | Pydantic (or equivalent) for: `regions: [{ region_id, level }]`, optional `free_text`, optional `duration`, `triggers`. |
| 1.4 | Assessment output schema | Pydantic: symptom summary, risk level (low/medium/high), missing_info list. |
| 1.5 | Safety output schema | Enum or literal: `safe_to_continue` \| `professional_soon` \| `urgent_care`. Optional: list of triggered red flags. |
| 1.6 | Recovery output schema | Short recovery plan: list of actions, precautions, optional source (e.g. "from our exercise guide"). |
| 1.7 | Referral output schema | Provider type (physio/chiro/massage/urgent/none), reason, timing. |

---

## 4. Phase 2 — Backend Pipeline (Agents)

| Step | Task | Details |
|------|------|---------|
| 2.1 | Assessment Agent | Railtracks agent + structured output (symptom summary, risk level). Input: body map + optional text. |
| 2.2 | Safety tool/agent | Rule-based red-flag check (numbness, bowel/bladder, chest pain, weakness, trauma, etc.). Input: assessment summary. Output: safe / professional_soon / urgent_care. |
| 2.3 | Recovery Agent | Agent that suggests stretches/posture/breaks. Input: assessment (when safe). Optional: RAG tool over vetted exercise content. |
| 2.4 | Referral Agent | Agent that recommends next step (physio/chiro/massage/urgent/none) from assessment + safety + optional progress. Optional: RAG over referral guidelines. |
| 2.5 | Orchestration | Linear pipeline: intake → Assessment → Safety → (if safe) Recovery; (if not safe or referral needed) Referral. Single async entry point (e.g. `run_flexcare_pipeline(intake)`). |
| 2.6 | "Why" and summary | Pipeline returns structured response + short `reason` or `why_this_recommendation` string for UI. Optional: `session_summary` for user/clinician. |
| 2.7 | Error handling | On LLM/agent failure: return generic "try again or speak to a professional" message; log minimal metadata (no PII). |

---

## 5. Phase 3 — Body Map (Frontend)

| Step | Task | Details |
|------|------|---------|
| 3.1 | Body silhouette | SVG (or canvas) with front/back (or back-only for MVP). Predefined clickable regions. |
| 3.2 | Interaction | Click/tap region → set pain level (dropdown or slider). Multiple regions allowed. |
| 3.3 | Heat visualization | Color scale: cold (low pain) → hot (high pain). Optionally show numeric label per region (accessibility). |
| 3.4 | Data binding | Build payload: `{ regions: [{ region_id, level }], ... }` and send with optional free text to backend. |
| 3.5 | Text alternative | "Or describe where it hurts" so users can skip the map. Map + text can be combined in intake. |
| 3.6 | Mobile | Touch-friendly targets; test on small screen. |

---

## 6. Phase 4 — Chat / UI and API

| Step | Task | Details |
|------|------|---------|
| 4.1 | API contract | POST `/assess` or `/chat`: body = intake (body map + optional message). Response = recommendation + why + optional session summary. |
| 4.2 | Frontend flow | Screen 1: body map + optional short text. Submit → call API → show result. Optional: chat-style UI with streaming later. |
| 4.3 | Escalation display | When Safety says urgent or professional_soon: show clear, prominent message (e.g. card or banner). |
| 4.4 | "Why this recommendation?" | Show the `why_this_recommendation` (or equivalent) string in expandable section or below the main recommendation. |
| 4.5 | Disclaimers | "FlexCare is for education and care navigation only…" near first use or in footer. |

---

## 7. Phase 5 — Content & Optional RAG

| Step | Task | Details |
|------|------|---------|
| 5.1 | Red-flag list | Finalize list and wording; implement in Safety tool/agent (no LLM override for red flags). |
| 5.2 | Recovery content | Curated list of safe stretches/actions by region (or small doc set). If no RAG: hardcode or simple lookup. |
| 5.3 | RAG (optional) | If time: embed recovery (and/or referral) docs in ChromaDB; add search-as-tool for Recovery/Referral agents. Use same embedding model for ingest and query. |

---

## 8. Phase 6 — Demo & Hardening

| Step | Task | Details |
|------|------|---------|
| 6.1 | Demo script | Document 2–3 scenarios: happy path (low back, safe, recovery); red-flag (numbness → urgent); referral (no improvement → physio). Run before every demo. |
| 6.2 | Environment check | Script or README step: ensure `.env` has required keys; backend starts; frontend calls correct API. |
| 6.3 | Fallback copy | Generic error message and "when in doubt, see a professional" for edge cases. |
| 6.4 | Pitch | One-liner: "FlexCare: tap where it hurts, get a heat map and a clear next step—stretches or referral—with a simple 'why.'" |

---

## 9. Phase 7 — Exercise recording & posture feedback

*Goal: Let users record themselves doing a suggested exercise, analyze posture, and get feedback to reduce risk of further injury. Fits after Recovery recommendation (Phase 4); uses same exercise set the Recovery Agent suggests.*

| Step | Task | Details |
|------|------|---------|
| 7.1 | Capture | Frontend: request camera (e.g. `getUserMedia`); record a short clip or capture frames while the user performs the suggested exercise. Optional: upload pre-recorded video. |
| 7.2 | Pose estimation | Integrate pose detection: **Option A** — MediaPipe Pose in the browser (no video sent to server); **Option B** — backend (MediaPipe/OpenCV or API). Output: keypoints (shoulders, hips, spine, knees, etc.) per frame or snapshot. |
| 7.3 | Exercise reference | For each exercise the Recovery Agent can suggest, define a minimal "target form": key angles or alignment rules (e.g. "spine neutral," "knee over ankle"). Store in code or small config/DB keyed by exercise_id or name. |
| 7.4 | Feedback logic | Compare user pose to reference (rule-based: angle thresholds, alignment). Optionally: send keypoints + exercise_id to backend; use LLM (Gemini) to generate 1–2 natural-language corrections and "avoid further injury" tips. API: e.g. `POST /exercise-feedback` with `{ exercise_id, keypoints }` → `{ corrections[], safety_tips[] }`. |
| 7.5 | UI flow | After showing recovery actions, add "Record & get feedback" (or per-exercise "Do this & get form check"). Show exercise name → start camera → user does exercise → submit → display feedback and safety tips. Optional: overlay skeleton or corrections on video. Reuse disclaimer: not a substitute for in-person assessment. |

*Dependencies:* Recovery Agent (2.3) and its list of suggested exercises; Phase 4 frontend so the user sees which exercise to perform. *Order:* 7.1 → 7.2 → 7.3 → 7.4 → 7.5; 7.2 can be client-only (MediaPipe in browser) for privacy and latency.

---

## 10. Process

- **Order:** Phase 0 → 1 → 2 → 3 → 4; Phase 5 (RAG) and 6 (demo) in parallel once 2–4 are stable. **Phase 7 (exercise recording & posture feedback)** builds on Phase 4: after the user gets recovery actions, they can optionally record and get form feedback; implement 7.1–7.5 when 4 is stable.
- **Safety:** Safety Agent/tool and red-flag logic are implemented and tested before demo. Exercise feedback (Phase 7) must include "avoid further injury" tips and reuse the same "not a diagnostic tool" disclaimer.
- **Docs:** Keep `overview.md`, `ideas.md`, `plan.md`, and `phases.txt` in sync when scope or architecture changes.
