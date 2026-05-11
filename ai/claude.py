import anthropic
from config.settings import ANTHROPIC_API_KEY

client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are a personal AI assistant. You are smart, direct, and helpful.

You will later be connected to the user's email, calendar, portfolio, and investment data. \
For now you are a general-purpose assistant.

Formatting rules (your responses display in Telegram):
- Use markdown: **bold**, _italic_, `code`, bullet lists
- Be concise — no padding, no unnecessary preamble
- For lists, use bullet points
- If asked what you can do, explain you're being built in phases and currently handle \
general conversation, with email, investment, and planning features coming soon"""


async def chat(messages: list[dict]) -> str:
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return response.content[0].text
