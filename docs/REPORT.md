# Report: AI-Powered Escape Room

## 1. Goal
Build a text escape room where an LLM acts as Game Master, then make it reliable. The room is a locked
library with five objects (desk, bookshelf, painting, drawer, door), three puzzles and a final exit.

## 2. Version 1 - design and implementation
V1 is a Streamlit chat app calling Gemini. A single system prompt contains the room description, all
secret codes and the rules. Memory is the chat history resent each turn. A win is detected when the
model emits the token `[ESCAPED]`. It works and is engaging because the LLM improvises natural responses.

**Problems found.** (1) The LLM is both narrator and referee, so rules are only suggestions: it can accept
items the player never collected. (2) Secrets sit in the prompt and can leak or be extracted. (3) State is
implicit in text, so the model can forget, contradict itself or invent objects. (4) Win detection depends on the model
printing a token, which a persuasive player can trigger.

## 3. Version 2 - design and implementation
V2 separates *deciding* from *describing*:
- **Game state** is a Python dictionary (inventory, examined objects, clues, drawer, deadbolt, escaped, failed codes).
- **Game config** (`game_data.py`) holds objects, items, clue text and the secret codes outside any LLM text.
- **Intent parser (LLM):** converts free text into JSON `{action, target, item, code}`. It sees only object names, never codes.
- **Engine (Python):** one handler per action validates preconditions (item in inventory, item reachable, correct code,
  deadbolt opened before code) and updates state.
- **Narrator (LLM):** receives only the facts the engine produced and rewrites them atmospherically, with instructions
  not to add anything.
- **Offline fallback:** keyword parser plus plain facts when no API key or on API errors; this also makes the engine unit-testable.

## 4. Testing
Seven automated tests (`pytest`) cover the required adversarial cases: uncollected key, wrong code, false "already solved" claim,
administrator impersonation, secret extraction, invented objects and repeated actions, plus a full playthrough.
See `docs/TEST_CASES.md` for the V1-vs-V2 comparison.

## 5. Problems encountered and lessons
- Designing a puzzle chain with real dependencies (torch -> painting; books -> drawer -> key + note; key + both code halves -> door)
  so that inventory and ordering rules actually matter.
- Parsing free text: the LLM parser handles phrasing variety, but is still probabilistic; safety comes from validating after parsing.
- Keeping the narrator faithful: low-risk because it only gets facts, but a model can still embellish; the prompt forbids new facts.
- Key lesson: never put authority (state, rules, secrets) in the model; give it only the job of language.

## 6. Limitations and future work
One room, fixed vocabulary of actions, no LLM-output verification step (e.g. checking the narration does not contain codes),
no persistence across browser reloads. Possible extensions: multiple rooms, a narration filter, saved games, automated adversarial prompt suites.
