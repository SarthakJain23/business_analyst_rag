# 📖 Business Analyst RAG — Codebase Documentation

> Auto-generated, comprehensive guideline files for every source file in the project.

## Purpose

This `docs/` directory contains **per-file guideline documents** that explain each source file at both **high level** (architecture, purpose, design pattern) and **low level** (function-by-function, line-by-line breakdown).

## Structure

```
docs/
├── app/                          # Root application (Streamlit UI)
│   └── GUIDELINE.md
├── src/
│   ├── config/                   # Centralized settings
│   │   └── GUIDELINE.md
│   ├── core/
│   │   ├── ingestion/            # Document ingestion orchestrator
│   │   │   └── GUIDELINE.md
│   │   ├── state_tracker/        # File-level change detection
│   │   │   └── GUIDELINE.md
│   │   └── text_splitter/        # Chunking engine
│   │       └── GUIDELINE.md
│   ├── embeddings/               # Vendor-agnostic embedding provider (Class Singleton)
│   │   └── GUIDELINE.md
│   ├── llm/
│   │   ├── graph/                # LangGraph RAG workflow
│   │   │   └── GUIDELINE.md
│   │   ├── prompts/              # System prompt templates
│   │   │   └── GUIDELINE.md
│   │   └── rag_engine/           # RAG orchestrator + streaming
│   │       └── GUIDELINE.md
│   ├── loaders/
│   │   ├── base/                 # Abstract loader interface
│   │   │   └── GUIDELINE.md
│   │   ├── docx_loader/          # Word document loader
│   │   │   └── GUIDELINE.md
│   │   ├── excel_loader/         # Excel/CSV loader
│   │   │   └── GUIDELINE.md
│   │   ├── factory/              # Loader factory pattern
│   │   │   └── GUIDELINE.md
│   │   ├── pdf_loader/           # PDF document loader
│   │   │   └── GUIDELINE.md
│   │   └── text_loader/          # Plain text/Markdown loader
│   │       └── GUIDELINE.md
│   ├── utils/
│   │   └── logger/               # Logging utility
│   │       └── GUIDELINE.md
│   └── vector_store/
│       └── store/                # ChromaDB + hybrid retrieval
│           └── GUIDELINE.md
└── README.md                     # This file
```

## How to Read

Each `GUIDELINE.md` follows a consistent format:

1. **Header** — File path, purpose, module role
2. **High-Level Overview** — What the file does, which design patterns it uses, its place in the architecture
3. **Dependencies & Imports** — External libraries and internal module relationships
4. **Low-Level Breakdown** — Every class, function, and method explained with parameters, return values, and logic flow
5. **Design Patterns** — Patterns identified in the code (Factory, Strategy, State, etc.)
6. **Data Flow** — How data enters and exits the module
7. **Improvement Suggestions** — Actionable notes for future refactoring

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    app.py (Streamlit UI)                     │
│  Sidebar: Upload, Sync, Config   Main: Chat, Prompts       │
└──────────┬──────────────┬──────────────┬────────────────────┘
           │              │              │
     ┌─────▼─────┐  ┌────▼─────┐  ┌────▼──────────┐
     │ Ingestion  │  │  State   │  │  RAG Engine   │
     │  Engine    │  │ Tracker  │  │ (LangGraph)   │
     └─────┬──────┘  └──────────┘  └────┬──────────┘
           │                              │
     ┌─────▼──────────────────────────────▼──────┐
     │           Vector Store Manager            │
     │         (ChromaDB + BM25 Hybrid)          │
     └─────┬─────────────────────────────────────┘
           │
     ┌─────▼─────────┐
     │  Loaders       │
     │  (Factory →    │
     │   PDF/DOCX/    │
     │   Excel/Text)  │
     └────────────────┘
```
