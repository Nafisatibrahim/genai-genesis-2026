# AI Musculoskeletal Recovery Assistant

An agentic AI solution that helps Canadians monitor and improve musculoskeletal health through early symptom assessment, guided recovery support, progress tracking, and smart care routing.

## Overview

Musculoskeletal pain, especially back, neck, shoulder, and posture-related pain, is a major barrier to day-to-day wellness and work productivity. Many people do not know whether they should rest, stretch, monitor symptoms, or seek professional care. This project uses a team of AI agents to help users take the right next step early.

## Problem

A large number of people experience pain caused by sitting for long hours, repetitive work, poor posture, overuse, or minor strain. In many cases, symptoms begin small but worsen over time because people delay care, do the wrong exercises, or do not track recovery properly.

## Solution

AI Musculoskeletal Recovery Assistant is a multi-agent system that supports users from first symptom report to recovery tracking.

The system helps users:

* describe their pain in natural language
* receive an initial symptom assessment
* get safe stretches or recovery suggestions for low-risk cases
* track progress over time
* know when to escalate to a physiotherapist, chiropractor, massage therapist, or urgent medical care

## Why this fits Sun Life

This project aligns with the challenge because it focuses on physical health, prevention, symptom management, and treatment tracking. It also fits well with common extended health benefits categories such as physiotherapy, chiropractic care, and massage therapy.

## Core User Story

A user says: “I have lower back pain after sitting all day.”

The system then:

1. assesses the symptom severity and context
2. determines whether the issue appears low risk or needs escalation
3. recommends gentle stretches, posture adjustments, or recovery tips when appropriate
4. tracks whether symptoms improve, stay the same, or worsen
5. routes the user toward a covered care option if needed

## Agent Architecture

### 1. Assessment Agent

Responsible for understanding the symptom report.

Inputs:

* pain location
* pain severity
* duration
* triggers
* mobility limitations
* warning signs

Outputs:

* structured symptom summary
* preliminary risk level
* missing information to ask for

### 2. Safety Agent

Looks for red flags and determines whether the user should seek urgent care instead of self-management.

Examples of red flags:

* numbness or tingling
* loss of bladder or bowel control
* chest pain
* sudden severe weakness
* inability to stand or walk
* recent trauma

Outputs:

* safe to continue with guided recovery
* recommend professional assessment soon
* recommend urgent care now

### 3. Exercise and Recovery Agent

Generates low-risk recovery suggestions for appropriate cases.

Examples:

* light stretches
* posture adjustments
* work-break reminders
* mobility guidance
* recovery education

Outputs:

* short, practical recovery plan
* daily actions
* precautions

### 4. Progress Tracking Agent

Tracks symptoms across time and compares current status with earlier check-ins.

Tracks:

* pain level over time
* mobility changes
* symptom triggers
* response to suggested exercises

Outputs:

* improvement trend
* worsening trend
* recommendation to continue, modify, or escalate

### 5. Referral Agent

Routes the user to the most appropriate next step based on symptom pattern and progress.

Possible routes:

* physiotherapist
* chiropractor
* massage therapist
* family doctor
* urgent care

Outputs:

* recommended provider type
* reason for referral
* suggested timing

## Example Workflow

### Scenario: Desk-related lower back pain

1. User enters: “My lower back hurts after sitting for long periods.”
2. Assessment Agent asks follow-up questions.
3. Safety Agent confirms no major red flags.
4. Exercise and Recovery Agent suggests a short stretching and posture routine.
5. Progress Tracking Agent checks in later.
6. If pain persists after several days, Referral Agent recommends physiotherapy.

## Demo Scope for Hackathon

### Must Have

* symptom intake interface
* multi-agent workflow
* risk classification
* simple recovery suggestions
* progress tracker
* referral recommendation

### Nice to Have

* voice input
* body map for pain location
* personalized exercise cards
* provider matching by care type
* benefit-aware recommendation layer

## Suggested Tech Stack

### Frontend

* React or Next.js
* Tailwind CSS
* simple chat or guided form interface

### Backend

* Python FastAPI or Node.js Express
* API routes for agent orchestration

### AI Layer

* agent orchestration with LangGraph or similar framework
* LLM for reasoning and follow-up questions
* rule-based safety checks for red flags

### Data and State

* lightweight database such as Supabase, Firebase, or SQLite
* session-based symptom history and progress logs

## Safety Positioning

This is not a diagnostic tool and should not claim to replace medical professionals. The product should clearly state that it provides educational guidance, symptom support, and care navigation.

## Target Users

* desk workers with posture-related pain
* students with repetitive strain or neck pain
* people recovering from mild musculoskeletal discomfort
* anyone unsure whether they should self-manage or seek care

## Hackathon Pitch Angle

This is not just a chatbot. It is an AI care workflow made up of specialized agents that collaborate to support prevention, symptom management, and treatment tracking.

## MVP Build Plan

### Day 1

* define workflow and prompts
* build intake UI
* implement agent orchestration
* create safety rules and response logic

### Day 2

* connect progress tracking
* polish recommendations and referral flow
* prepare demo script and presentation
* create screenshots and architecture diagram

## Repository Structure

```text
ai-msk-recovery-assistant/
├── README.md
├── frontend/
├── backend/
├── agents/
│   ├── assessment_agent.py
│   ├── safety_agent.py
│   ├── recovery_agent.py
│   ├── tracking_agent.py
│   └── referral_agent.py
├── prompts/
├── data/
├── docs/
└── demo/
```

## First Build Tasks

1. define the exact user flow
2. design the symptom intake schema
3. write prompts for each agent
4. implement the orchestration logic
5. create the frontend chat or form experience
6. define referral output categories
7. add sample user scenarios for testing

## Sample Output

**Assessment Summary**

* Location: lower back
* Severity: mild to moderate
* Trigger: prolonged sitting
* Duration: 3 days
* Risk: low

**Suggested Recovery Plan**

* stand and stretch every 45 to 60 minutes
* perform 3 guided mobility exercises
* avoid prolonged slouched sitting
* recheck symptoms tomorrow

**Referral Recommendation**

* if symptoms persist for 7 days or worsen, consult a physiotherapist

## Future Extensions

* wearables integration
* workplace ergonomics scoring
* personalized recovery plans based on history
* insurance benefit awareness
* provider booking integration

## Team Roles

* frontend: intake interface and progress dashboard
* backend: orchestration and API integration
* AI: prompts, safety logic, agent coordination
* product/pitch: demo flow, slides, storytelling, judging alignment

## License

Hackathon prototype.
