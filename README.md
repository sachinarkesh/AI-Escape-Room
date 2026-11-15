# AI-Escape-Room

An interactive escape-room game where an LLM (Google Gemini) is the Game Master. Built in two versions to show why
LLM-only game logic is unreliable and how a structured game state with Python-side validation fixes it.

You wake up in a locked library. Examine the desk, bookshelf, painting and drawer, collect items, solve the puzzles and open the door.

## Versions
| | V1 - Interactive | V2 - Reliable |
|---|---|---|
| Rules & secrets | In the system prompt | In Python (`game_data.py`, `engine.py`) |
| State | Chat history | Structured dict |
| Who decides success | LLM | Python engine |
| LLM role | Narrator + referee | Intent parser + narrator only |
| Adversarial inputs | Vulnerable | Handled and tested |

Architecture diagrams for both versions: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Tech stack
Python 3.10+, Streamlit, Google Gemini API (`google-genai`, free tier), python-dotenv, pytest.

## Setup
```bash
git clone https://github.com/<your-username>/AI-Escape-Room.git
cd AI-Escape-Room
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # then put your free key from https://aistudio.google.com/apikey
```
## Run
```bash
streamlit run app.py        # both versions on one page; switch in the sidebar (switching starts a fresh game)
streamlit run v1/app.py     # Version 1 only
streamlit run v2/app.py     # Version 2 only (works offline without a key, using a keyword parser)
pytest -q                   # V2 engine tests, no API key needed
```
Deploy on Streamlit Community Cloud with **Main file path: `app.py`** and your `GEMINI_API_KEY` in the app Secrets.

## Solution (spoiler)
<details><summary>Show</summary>
Torch on desk -> use on painting (".. ends with 58"); bookshelf digits 4-1-7-2 -> drawer; take brass key, note says "starts with 60";
use key on door, then enter 6058.
</details>

## Testing
Seven adversarial/consistency cases with V1-vs-V2 behaviour: [`docs/TEST_CASES.md`](docs/TEST_CASES.md). Screenshots: `docs/screenshots/`.

## Report
[`docs/REPORT.md`](docs/REPORT.md): design, implementation, problems and improvements.

## Security
API keys are read from environment variables (`.env`, git-ignored). Never commit `.env`.
