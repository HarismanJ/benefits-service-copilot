# Benefits Service Copilot

An internal AI-powered tool that converts unstructured employee-benefits inquiries into organized, grounded and review-ready cases.

## Features

- Extracts structured intake information from client inquiries
- Identifies missing information
- Generates client follow-up questions
- Searches an internal benefits knowledge base using RAG
- Produces a grounded internal report
- Supports contextual follow-up conversations
- Flags cases requiring human advisor review
- Exports reports as Markdown files
- Includes automated structured-output and RAG evaluations

## How It Works

1. A user submits an unstructured benefits inquiry.
2. The application extracts validated information using Pydantic and Structured Outputs.
3. Missing information and follow-up questions are identified.
4. File search retrieves relevant internal guidance from a vector store.
5. The application generates a concise internal report.
6. The user can ask contextual follow-up questions.
7. Final benefits decisions remain with a human advisor.

## Project Structure

- `app.py` — Streamlit user interface
- `copilot.py` — AI extraction, RAG and follow-up logic
- `benefits_knowledge.md` — Internal benefits knowledge base
- `setup_knowledge_base.py` — Vector-store setup
- `evaluate.py` — Automated evaluation cases
- `.env.example` — Required environment variables
- `requirements.txt` — Python dependencies

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Create `.env` from `.env.example` and add your OpenAI API key and vector-store ID.

Run the application:

```bash
streamlit run app.py
```

Run the evaluations:

```bash
python evaluate.py
```

## Safety

The copilot is instructed not to invent pricing, coverage, eligibility rules or provider recommendations. Cases involving professional judgment are flagged for human review.

## Limitations

This is a prototype using a synthetic knowledge base. It does not connect to live provider systems, calculate real quotations, store permanent client records or replace a licensed benefits advisor.

##Demo
https://youtu.be/pQmRmwbLCe0 
