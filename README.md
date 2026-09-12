# AI-Powered Customer Complaint Management System

An AI-powered customer complaint management system designed for pharmaceutical manufacturing Quality Management Systems (QMS).

The application extracts structured complaint information from natural-language input and complaint documents, performs AI-based risk assessment, checks complaint completeness, generates summaries, and allows users to make corrections using natural language.

## Features

- Natural-language complaint extraction
- Structured complaint data extraction
- Complaint source and customer identification
- AI-based risk assessment
  - Severity
  - Priority
  - Complaint category
  - Suggested next action
  - Initial risk assessment
- Complaint completeness checking
- Automatic complaint summary generation
- Natural-language complaint correction
- PDF complaint processing
- OCR extraction for scanned/image-based PDFs
- React-based complaint management interface
- AI Copilot interface

## Tech Stack

### Frontend
- React
- Vite
- JavaScript
- CSS

### Backend
- FastAPI
- Python
- Pydantic

### AI
- LangChain
- LangGraph
- Groq
- `openai/gpt-oss-20b`

### Document Processing
- PyMuPDF
- PyPDF
- Tesseract OCR
- Pytesseract
- Pillow

## Architecture

```text
User
  │
  ▼
React Frontend
  │
  │ HTTP Request
  ▼
FastAPI Backend
  │
  ▼
LangGraph Workflow
  │
  ├── Complaint Extraction
  │
  ├── Risk Assessment
  │
  ├── Completeness Check
  │
  └── Summary Generation
  │
  ▼
Groq LLM
  │
  ▼
Structured Complaint Data
  │
  ▼
React UI