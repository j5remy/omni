from openai import OpenAI

# Make sure to set your API key
api_key = "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"
client = OpenAI(api_key=api_key)

def generate_notes(text):
    prompt = [
        {
            "role": "system", 
            "content": (
                "You are a highly capable note-taking assistant. "
                "Your job is to extract the most important points from the given text while ignoring extraneous details "
                "such as UI elements, bookmarks, or random numbers. Focus on the main context and key concepts that the user is reading about. "
                "Make sure to take notes as if you are the user writing down notes that they think are important and will need to know or remember in the future."
            )
        },
        {
            "role": "user",
            "content": f"Please read the following text and provide detailed bullet point notes of the most important topics and insights:\n\n{text}"
        }
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=prompt,
        temperature=0.3
    )

    notes = response.choices[0].message.content
    return notes