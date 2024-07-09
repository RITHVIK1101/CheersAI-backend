import openai
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")

def get_chatgpt_response(message):
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=message,
        max_tokens=1000,
        temperature=0.7,
        n=1,
        stop=None,
    )
    return response.choices[0].text