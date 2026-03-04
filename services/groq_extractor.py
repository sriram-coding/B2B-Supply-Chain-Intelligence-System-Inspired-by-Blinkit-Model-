from groq import Groq
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config


def get_groq_client():
    return Groq(api_key=config.GROQ_API_KEY)


def extract_insights(text: str, context: str = "") -> str:
    """Use Groq LLM to extract insights from supply chain data."""
    client = get_groq_client()
    system_prompt = (
        "You are an expert Supply Chain Intelligence AI for Blinkit Enterprise. "
        "Analyze the provided data and return concise, actionable insights. "
        "Focus on performance metrics, risks, and opportunities."
    )
    user_prompt = f"{context}\n\nData:\n{text}\n\nProvide structured insights."
    try:
        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Groq Error] {str(e)}"


def chat_completion(messages: list, system: str = "") -> str:
    """General-purpose chat completion."""
    client = get_groq_client()
    full_messages = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)
    try:
        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=full_messages,
            max_tokens=2048,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Groq Error] {str(e)}"
