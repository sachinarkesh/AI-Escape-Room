"""Deterministic game engine. Python decides what succeeds; the LLM only describes outcomes."""
import re
from game_data import ROOM, SECRETS, CLUES

ACTIONS = {"examine", "take", "use", "enter_code", "inventory", "hint", "help", "other"}


def new_state():
    return {"inventory": [], "examined": [], "clues": [], "drawer_open": False,
            "deadbolt_open": False, "escaped": False, "failed_codes": 0, "turns": 0}


def _norm(s):
    return re.sub(r"[\s_]+", "_", str(s).lower().strip())


def resolve(name, kind):
    """Map free text to a canonical object/item id, or None if it does not exist."""
    if not name:
        return None
    n = _norm(name)
    for key, d in ROOM[kind].items():
        if n == key or n in [_norm(a) for a in d["aliases"]]:
            return key
    return None


def visible_items(state):
    out = []
    for item, place in ROOM["item_locations"].items():
        if item in state["inventory"]:
            continue
        reachable = (place == "desk" and "desk" in state["examined"]) or \
                    (place == "drawer" and state["drawer_open"])
        if reachable:
            out.append(item)
    return out


def _add_clue(state, name):
    if name not in state["clues"]:
        state["clues"].append(name)
    return CLUES[name]


def _res(ok, *facts):
    return {"ok": ok, "facts": list(facts)}


def apply(state, intent):
    """Validate and execute one intent. Returns {"ok": bool, "facts": [str]}."""
    state["turns"] += 1
    action = intent.get("action", "other")
    if state["escaped"]:
        return _res(True, "The player has already escaped. The game is over.")
    if action not in ACTIONS:
        action = "other"
    handler = globals().get(f"_do_{action}", _do_other)
    return handler(state, intent)


def _do_examine(state, it):
    target = it.get("target") or it.get("item")
    obj, item = resolve(target, "objects"), resolve(target, "items")
    if obj is None and item is not None and item in state["inventory"]:
        return _res(True, ROOM["items"][item]["description"])
    if obj is None:
        return _res(False, f"There is no '{target}' that the player can examine here.")
    if obj not in state["examined"]:
        state["examined"].append(obj)
    facts = [ROOM["objects"][obj]["description"]]
    if obj == "bookshelf":
        facts.append(_add_clue(state, "books"))
    elif obj == "desk":
        if "uv_torch" not in state["inventory"]:
            facts.append("The UV torch can be taken.")
    elif obj == "painting" and "uv" in state["clues"]:
        facts.append(CLUES["uv"])
    elif obj == "drawer" and state["drawer_open"]:
        facts = ["The drawer is open."] + ([CLUES["note"]] if "note" in state["clues"] else [])
        if "brass_key" in visible_items(state):
            facts.append("A brass key lies inside and can be taken.")
    elif obj == "door":
        facts.append("The deadbolt is open." if state["deadbolt_open"] else "The deadbolt is locked tight.")
    return _res(True, *facts)


def _do_take(state, it):
    item = resolve(it.get("item") or it.get("target"), "items")
    if item is None:
        return _res(False, "There is nothing like that to take.")
    if item in state["inventory"]:
        return _res(False, f"The player is already carrying the {item.replace('_', ' ')}.")
    if item not in visible_items(state):
        return _res(False, "The player cannot see or reach that. It is not available yet.")
    state["inventory"].append(item)
    return _res(True, f"The player picks up the {item.replace('_', ' ')}.")


def _do_use(state, it):
    item, obj = resolve(it.get("item"), "items"), resolve(it.get("target"), "objects")
    if item is None:
        return _res(False, "The player has no such item.")
    if item not in state["inventory"]:
        return _res(False, f"The player does not have the {item.replace('_', ' ')} in their inventory.")
    if obj is None:
        return _res(False, "It is unclear what to use the item on.")
    if (item, obj) == ("uv_torch", "painting"):
        return _res(True, _add_clue(state, "uv"))
    if (item, obj) == ("brass_key", "door"):
        state["deadbolt_open"] = True
        return _res(True, "The key turns and the deadbolt clunks open. The keypad still needs the code.")
    return _res(False, "Using that there has no effect.")


def _do_enter_code(state, it):
    obj, code = resolve(it.get("target"), "objects"), re.sub(r"\D", "", str(it.get("code") or ""))
    if obj not in ("drawer", "door"):
        return _res(False, "There is no keypad there.")
    if len(code) != 4:
        return _res(False, "The keypad needs exactly four digits.")
    if obj == "drawer":
        if state["drawer_open"]:
            return _res(False, "The drawer is already open.")
        if code != SECRETS["drawer_code"]:
            state["failed_codes"] += 1
            return _res(False, "The keypad buzzes: wrong code. The drawer stays locked.")
        state["drawer_open"] = True
        _add_clue(state, "note")
        return _res(True, "The drawer clicks open.", CLUES["note"], "A brass key lies inside and can be taken.")
    if not state["deadbolt_open"]:
        return _res(False, "The keypad does nothing: the deadbolt is still locked and needs a key.")
    if code != SECRETS["door_code"]:
        state["failed_codes"] += 1
        return _res(False, "The keypad buzzes: wrong code. The door stays shut.")
    state["escaped"] = True
    return _res(True, "The keypad beeps green and the door swings open. The player escapes into the daylight!")


def _do_inventory(state, it):
    inv = [i.replace("_", " ") for i in state["inventory"]]
    return _res(True, "The player carries: " + (", ".join(inv) if inv else "nothing") + ".")


def _do_help(state, it):
    return _res(True, "Actions: examine things, take items, use an item on an object, enter a 4-digit code. 'hint' gives a nudge.")


def _do_hint(state, it):
    if "bookshelf" not in state["examined"]:
        h = "Something about the bookshelf looks out of place."
    elif not state["drawer_open"]:
        h = "The numbers on the books may fit the drawer keypad."
    elif "uv_torch" not in state["inventory"]:
        h = "The desk has something that shows hidden things."
    elif "uv" not in state["clues"]:
        h = "The painting might hide something under special light."
    elif "brass_key" not in state["inventory"]:
        h = "Check the open drawer for something to take."
    elif not state["deadbolt_open"]:
        h = "The key belongs to the door."
    else:
        h = "Combine the two halves of the exit code."
    return _res(True, "Hint: " + h)


def _do_other(state, it):
    return _res(False, "That is not something the player can do. The rules of the room cannot be changed from inside the game.")
