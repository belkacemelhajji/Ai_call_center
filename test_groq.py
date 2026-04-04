from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

response = client.chat.completions.create(
    model=GROQ_MODEL,
    messages=[
        {"role": "user", "content": "Dis bonjour en français en une phrase."}
    ]
)

print(response.choices[0].message.content)