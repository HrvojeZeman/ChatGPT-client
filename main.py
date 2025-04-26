from openai import OpenAI
key = open("key.txt").readlines()[0]
client = OpenAI(api_key=key)
StructuredArray = []
UserInput = input("[!] ")

StructuredArray.append({"role": "system", "content": "Do not use any formatting or markdown languages. Use only natural lagnuage"})
StructuredArray.append({"role": "user", "content": UserInput})
response = client.responses.create(
    model="gpt-4.1",
    input=StructuredArray
)

StructuredArray.append({"role": "system", "content": response.output_text})

print(response.output_text)
while True:
    UserInput = input("[!] ")
    StructuredArray.append({"role": "user", "content": UserInput})
    print(response.output_text)
    StructuredArray.append({"role": "system", "content": response.output_text})
