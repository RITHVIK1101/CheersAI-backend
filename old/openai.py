import openai
import requests
import os

# Set up OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

def chat_with_gpt(users_collection, user_id, prompt, audio=False):
    # Get user data from MongoDB
    user_data = users_collection.find_one({"user_id": user_id})

    # If user data exists, append it to the prompt
    if user_data:
        prompt += f"\nUser Data: {user_data['data']}"

    # Generate response from ChatGPT
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=prompt,
        max_tokens=1000,
        temperature=0.7,
        n=1,
        stop=None,
    )

    # If audio is enabled, generate voice message from response
    if audio:
        voice_response = openai.Completion.create(
            engine="text-to-speech-gpt-35-turbo",
            prompt=response.choices[0].text,
            max_tokens=1000,
            temperature=0.7,
            n=1,
            stop=None,
        )

        # Send voice message as audio file
        audio_file = requests.get(voice_response.choices[0].audio_url)
        with open("voice_message.mp3", "wb") as file:
            file.write(audio_file.content)

    # Store user data in MongoDB
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"data": response.choices[0].text}},
    )

    # Return response
    return response.choices[0].text



# # Example usage with audio enabled
# user_id = "12345"
# prompt = "Hello, how can I help you?"
# response = chat_with_gpt(user_id, prompt, audio=True)
# print(response)

# # Example usage without audio
# user_id = "54321"
# prompt = "What's the weather today?"
# response = chat_with_gpt(user_id, prompt)
# print(response)