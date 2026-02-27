from mistralai import Mistral
from settings.config import MISTRAL_API_KEY

client = Mistral(api_key=MISTRAL_API_KEY)

def generate(prompt):
    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content