"""
src/ai/groq_recommendation.py

Turns a pre-computed "decision pack" (real numbers calculated in Python)
into a concrete, store-manager-ready action plan.

The LLM never calculates anything and never invents data. It only
words the plan around the numbers it is given.
"""

import json
import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except Exception:
    pass

from groq import Groq


MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


SYSTEM_PROMPT = """You are a senior retail operations analyst advising a store manager.

You receive a JSON "decision pack" with numbers already calculated by the RetailIQ system.

STRICT RULES
1. Use ONLY numbers that appear in the JSON. Never invent stock levels, costs, prices, lead times or percentages.
2. Every action must name a specific product ID (or category), a specific quantity or target, and a timing.
3. Round units to whole numbers and money to whole dollars.
4. If `on_hand_provided` is false for a product, say "order up to <order_up_to> units minus current stock" instead of a single order quantity.
5. Do not use vague verbs such as "consider", "review", "monitor" or "explore" as the action. Use "order", "raise", "set", "cut", "move", "check".
6. Keep the whole answer under 260 words. No preamble, no closing remarks.

OUTPUT FORMAT (Markdown, exactly these sections)

**Verdict**
One or two sentences: what matters most this week and why (use a number).

**Do this week**
1. <Action> - <product> - <quantity/target> - <by when> - <why, with a number>
2. ...
3. ...
(maximum 3 actions, ordered by revenue at risk)

**Store opportunity**
One action for the weakest category using the category gap numbers. If none is provided, write "No category is below the chain average."

**Verify before acting**
Two short bullets naming what the numbers do NOT cover (for example actual stock on hand, supplier lead time, unit cost).
"""


def _get_api_key() -> str:
    key = os.getenv("GROQ_API_KEY")

    if not key:
        try:
            import streamlit as st

            key = st.secrets.get("GROQ_API_KEY")
        except Exception:
            key = None

    if not key:
        raise RuntimeError("GROQ_API_KEY is not set (.env or Streamlit secrets).")

    return key


def generate_groq_recommendation(decision_pack: dict) -> str:
    client = Groq(api_key=_get_api_key())

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        max_tokens=700,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": "Decision pack:\n" + json.dumps(decision_pack, indent=2),
            },
        ],
    )

    text = (response.choices[0].message.content or "").strip()

    if not text:
        raise RuntimeError("Groq returned an empty response.")

    return text