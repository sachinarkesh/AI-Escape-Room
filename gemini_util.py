"""Shared Gemini helper used by V1 and V2: one place for the client, model names and retry-on-404."""
import os

PRIMARY = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
FALLBACKS = [m.strip() for m in os.getenv("GEMINI_FALLBACK_MODELS", "gemini-3.1-flash-lite").split(",") if m.strip()]


def get_client():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return None
    from google import genai
    return genai.Client(api_key=key)


def generate(client, contents, config):
    """Call generate_content; if a model is retired/unknown (404), try the next one."""
    last = None
    for model in [PRIMARY] + [m for m in FALLBACKS if m != PRIMARY]:
        try:
            return client.models.generate_content(model=model, contents=contents, config=config)
        except Exception as e:  # noqa: BLE001
            last = e
            if "404" not in str(e) and "NOT_FOUND" not in str(e):
                raise
    raise last
