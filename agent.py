import json
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from memory.long_term import get_memories, save_memory
from memory.short_term import ShortTermMemory


BASE_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = BASE_DIR / "prompts"
SOUL_PATH = PROMPTS_DIR / "soul.md"
MEMORY_EXTRACTION_PROMPT_PATH = PROMPTS_DIR / "memory_extraction.md"
MEMORY_TYPES = {"fact", "preference", "goal", "project_context"}

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL")

if not API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set.")
if not MODEL:
    raise ValueError("GROQ_MODEL environment variable is not set.")

for prompt_path in (SOUL_PATH, MEMORY_EXTRACTION_PROMPT_PATH):
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

client = Groq(api_key=API_KEY)
short_memory = ShortTermMemory(max_messages=12)


def extract_long_term_memories(user_message):
    memory_prompt = MEMORY_EXTRACTION_PROMPT_PATH.read_text(encoding="utf-8")
    response = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": memory_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    content = response.choices[0].message.content
    if content is None:
        raise RuntimeError("Groq returned an empty memory-classification response.")

    result = json.loads(content)
    memories = result.get("memories")
    if not isinstance(memories, list):
        raise ValueError("Memory classifier response must contain a memories list.")

    validated_memories = []
    for memory in memories:
        if not isinstance(memory, dict):
            raise ValueError("Each extracted memory must be a JSON object.")

        memory_type = memory.get("type")
        memory_content = memory.get("content")
        if memory_type not in MEMORY_TYPES or not isinstance(memory_content, str):
            raise ValueError("Extracted memory has an invalid type or content.")

        memory_content = memory_content.strip()
        if memory_content:
            validated_memories.append((memory_type, memory_content))

    return validated_memories


def ask_soul(user_message, session_id):
    soul = SOUL_PATH.read_text(encoding="utf-8")

    short_memory.add_message(session_id, "user", user_message)
    recent_messages = short_memory.get_messages(session_id)
    saved_memories = get_memories(session_id)
    long_term_context = "\n".join(
        f"- [{memory['memory_type']}] {memory['content']}"
        for memory in saved_memories
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": soul},
            {
                "role": "system",
                "content": (
                    "Relevant long-term memories from prior conversations:\n"
                    f"{long_term_context or '(none)'}"
                ),
            },
            *recent_messages,
        ],
    )
    answer = response.choices[0].message.content
    if answer is None:
        raise RuntimeError("Groq returned an empty response.")

    short_memory.add_message(session_id, "assistant", answer)

    for memory_type, memory_content in extract_long_term_memories(user_message):
        save_memory(session_id, memory_type, memory_content)

    return answer
