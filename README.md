# AI Clinical Notes Documentation System

An end to end AI powered system that converts raw doctor patient conversations into structured, machine readable clinical notes using speech recognition, large language models, and a normalized relational database.

This project demonstrates how modern AI models can be orchestrated with database design principles to reduce clinical documentation burden while preserving data integrity and downstream usability.

---

## Overview

Clinicians often spend more time documenting visits than interacting with patients. Clinical conversations contain valuable diagnostic information, but they are unstructured, difficult to store, and hard to analyze.

This system automates clinical documentation by:

* Recording doctor patient conversations through a web interface
* Transcribing audio to text using OpenAI Whisper
* Generating both narrative summaries and structured clinical data using Gemini
* Storing results in a normalized PostgreSQL schema designed for analytics and integration

The result is a fully automated pipeline that produces EHR ready clinical notes while maintaining relational consistency.

---

## System Architecture

The pipeline follows a clear, modular flow:

1. **Audio Capture**
   A lightweight web interface records clinical encounters using the MediaRecorder API.

2. **Speech to Text**
   Audio is transcribed using OpenAI Whisper, producing a clean transcript tied to a visit record.

3. **Summarization and Structuring**
   Gemini generates:

   * A concise clinical summary for human readability
   * A schema aligned JSON object for structured storage

4. **Relational Storage**
   Data is stored in Neon PostgreSQL using a normalized schema with enforced foreign keys and constraints.

This design supports reprocessing, auditing, and downstream analytics without modifying raw conversation data.

---

## Database Design

The database is centered around real clinical workflows.

### Core Entities

* Patient
* Doctor
* Visit
* Conversation

### Supporting Entities

* Symptoms
* Treatments
* Surgeries
* Medical History
* Structured Summaries

Key design principles:

* One visit corresponds to one conversation
* Structured outputs are stored both as raw JSON and decomposed relational tables
* Referential integrity is enforced through foreign keys
* The schema supports longitudinal patient and clinician analysis

This structure makes the system suitable for EHR integration, reporting, and clinical analytics.

---

## Tech Stack

**Backend**

* Python
* Flask
* OpenAI Whisper
* Google Gemini API

**Database**

* Neon PostgreSQL
* Normalized relational schema
* SQL constraints and foreign keys

**Frontend**

* JavaScript
* HTML/CSS
* MediaRecorder API

**AI Techniques**

* Automatic Speech Recognition
* LLM based summarization
* Schema constrained structured extraction

---

## Key Features

* Fully automated clinical documentation pipeline
* Dual output: narrative summary and structured clinical data
* Database first design focused on integrity and extensibility
* Modular services that allow easy model or pipeline upgrades
* Serverless PostgreSQL backend that scales with workload

---

## Limitations and Future Work

* No clinician review interface before final database insertion
* Some temporal fields remain unnormalized text
* Occasional LLM hallucinations in ambiguous transcripts
* Limited authentication and patient identity management

Future improvements include:

* Editable review layers for clinicians
* Temporal normalization and confidence scoring
* Stronger schema constraints and validation
* Authentication and audit logging

---

## Academic Context

This project was developed as part of a database systems course and applies core concepts including:

* Entity relationship modeling
* Normalization and relational design
* SQL based data integrity enforcement
* End to end system integration

It serves as a practical demonstration of how AI systems benefit from strong database foundations.

---

## Contributors

* Jisun Kim
* Woochang Shin
* Jeonghyo Kim
* Shaun Ting

University of Minnesota

---

## License

This project is for academic and educational purposes.

---

If you want, next we can:

* Tighten this for a recruiter focused repo
* Add an architecture diagram section
* Write a shorter README for public visibility and keep this as `README_full.md`
