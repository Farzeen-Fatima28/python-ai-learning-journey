# Python for AI — Learning Journey

Documenting my journey learning Python for AI development, following along
with a YouTube tutorial and building my own practice projects on top of it.
Learning Python first, as a second language alongside JavaScript, aiming to
combine mobile, web, and AI skills for my FYP.

## What's in this repo

| Folder | Topics Covered |
|--------|----------------|
| `1_datatype_functions` | Variables, strings, lists, dictionaries, tuples, loops |
| `2_functions` | Functions, `*args`/`**kwargs`, default parameters, multiple returns |
| `3_OOP_Class` | Classes, `__init__`, `self`, multiple objects, inheritance basics |
| `4_calling_LLM` | Calling the Gemini API, building AI-powered functions |
| `5_Error_Handling` | `try`/`except`, custom error messages, safe input validation |
| `6_chatbot_memory` | Building a chatbot with conversation memory, `reset()`, personality via `system_instruction` |
| `7_comprehension` | List and dictionary comprehensions |
| `8_Structured_output` | Pydantic + `response_schema`, `response.parsed` for clean structured LLM output |
| `9_File_Handling` | `open()`, JSON files, `os.path.exists()`, safe file writing |
| `10_Web_API` | `requests`, status codes, path vs query parameters |
| `11_FastAPI` | Path/query parameters, Pydantic request & response models, building a real server |
| `12_databases` | SQLite (`sqlite3`), CRUD operations, connecting a database to a FastAPI route |
| `13_streamlit` | Streamlit basics — widgets, auto-rerun behavior, building simple interactive pages |
| `14_Customer_Feedback_Analyzer` | A full project: FastAPI + Streamlit + Gemini + SQLite tied together — batch sentiment analysis with a live dashboard |

## Tech / Concepts Used

- Core Python (data structures, functions, OOP)
- [Pydantic](https://docs.pydantic.dev/) for data validation
- [Google Gemini API](https://ai.google.dev/) for LLM calls
- `python-dotenv` for secure API key management
- FastAPI for building web APIs
- SQLite for persistent storage
- Streamlit for interactive frontends

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file with:

```
GEMINI_API_KEY=your_key_here
```

## Progress

- [x] Data types, loops, functions
- [x] OOP (classes, objects, `self`)
- [x] Modules (`random`, `datetime`)
- [x] Data validation with Pydantic
- [x] Calling LLM APIs (Gemini)
- [x] Error handling (`try`/`except`)
- [x] Chatbot memory & conversation state
- [x] Comprehensions
- [x] Structured output
- [x] File handling
- [x] Web APIs
- [x] FastAPI
- [x] Databases (SQLite)
- [x] Building a Streamlit app
- [x] Customer Feedback Analyzer (capstone project)
- [ ] Class inheritance (advanced)
- [ ] Decorators
- [ ] Virtual environments (in depth)

## Notes

- Git workflow: practice daily, push periodically whenever there's
  meaningful progress (not every single day).
- `.gitignore` protects `.env`, `.venv/`, `__pycache__/`, `.ipynb_checkpoints/`,
  and any local `.db` files — none of these are ever pushed.