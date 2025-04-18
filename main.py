from openai import OpenAI
client = OpenAI(api_key="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")
# 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
response = client.responses.create(
    model="gpt-4.1",
    input=[
        {"role": "user", "content": "what teams are playing in this image?"},
        {
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/3b/LeBron_James_Layup_%28Cleveland_vs_Brooklyn_2018%29.jpg"
                }
            ]
        }
    ]
)

print(response.output_text)