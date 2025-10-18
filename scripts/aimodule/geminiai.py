import google.generativeai as genai

apikey = "AIzaSyCEhWgzsr5ULqbz70cjHDyJkWS5l8-euLc"
# Configure the API key (replace with your key)
# It's better to use an environment variable for security
genai.configure(api_key= apikey)

# Create the model
model = genai.GenerativeModel('models/gemini-2.5-flash')

# Send a prompt and get the response
# prompt = f"generate a travel plan itinerary in json format for a 3 day trip to kulasai dhussera. gerate only json format without any extra text. example format: {example_json}"
# response = model.generate_content(prompt)

# # Print the result
# print(response.text)