"""Static game configuration. Secrets live HERE (Python), never in an LLM prompt."""

ROOM = {
    "title": "The Locked Library",
    "intro": ("You wake up on a cold floor in a locked library. Dust hangs in the lamplight. "
              "You can see a desk, a bookshelf, a painting, a drawer with a keypad, and a heavy "
              "door. Type what you want to do (try 'examine the desk'). Type 'hint' if you are stuck."),
    "objects": {
        "desk": {"aliases": ["table", "writing desk"],
                 "description": "A heavy oak desk with an inkwell and a small UV torch lying on it."},
        "bookshelf": {"aliases": ["shelf", "books", "bookcase"],
                      "description": "A tall bookshelf. Four books stick out of line with the others."},
        "painting": {"aliases": ["picture", "canvas"],
                     "description": "An oil painting of a sunset over the sea. Nothing else stands out in normal light."},
        "drawer": {"aliases": ["keypad", "locked drawer"],
                   "description": "A locked drawer with a 4-digit keypad."},
        "door": {"aliases": ["exit", "keypad door"],
                 "description": "A heavy door with a deadbolt and a 4-digit keypad."},
    },
    "items": {
        "uv_torch": {"aliases": ["torch", "uv torch", "flashlight", "uv light", "blacklight"],
                     "description": "A small ultraviolet torch."},
        "brass_key": {"aliases": ["key", "brass key"],
                      "description": "A small brass key with a worn handle."},
    },
    # Where each item starts. The container must be opened/examined before the item is reachable.
    "item_locations": {"uv_torch": "desk", "brass_key": "drawer"},
}

SECRETS = {"drawer_code": "4172", "door_code": "6058"}

# Text of clues, only released by the engine when the player earns them.
CLUES = {
    "books": "The four books carry handwritten numbers: red 4, blue 1, green 7, gold 2.",
    "note": "Inside the drawer, a note reads: 'The exit code starts with 60'.",
    "uv": "Under the UV light, faint writing appears on the painting: '...ends with 58'.",
}
