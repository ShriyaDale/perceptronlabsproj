import gradio as gr
import os
import google.generativeai as genai
from dotenv import load_dotenv, find_dotenv
import requests

load_dotenv(find_dotenv())

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
WEATHER_API_URL = os.getenv('WEATHER_API_URL')
model = genai.GenerativeModel()

def handle_user_query(msg, chatbot):
    print(msg, chatbot)
    chatbot += [[msg, None]]
    return '', chatbot

def get_weather(location): #used openweather api 
    try:
        params = {
            'q': location,
            'appid': WEATHER_API_KEY,
            'units': 'metric'          }
        response = requests.get(WEATHER_API_URL, params=params)
        weather_data = response.json() #parse all city data to json file

        if response.status_code == 200:
            temperature = weather_data['main']['temp']
            description = weather_data['weather'][0]['description']
            city = weather_data['name']
            country = weather_data['sys']['country']
            return f"The current weather in {city}, {country} is {description} with a temperature of {temperature}°C."
        else:
            return f"Sorry, I couldn't fetch the weather data for {location}. Please make sure the location is valid." #if location isn't present
    except Exception as e:
        return f"Error retrieving weather: {str(e)}"
    
def handle_chatbot_response(chatbot):
    query = chatbot[-1][0] 
    formatted_chatbot = generate_chatbot(chatbot[:-1])
    chat = model.start_chat(history = formatted_chatbot)
    personality_prompt = ("You are Alfred Thaddeus Crane Pennyworth, the famous Batman from Gotham City. "
                          "You are known for being an expert in martial arts, detective work, and technology. "
                          "You use fear as a weapon and are known for using high-tech gadgets to fight crime. "
                          "You tend to use short, direct statements, dark imagery, and are serious and somber"
                          "Provide the user with weather information, if possible, in a formal, calm manner, and offer suggestions for what they should wear.")
    response = chat.send_message(personality_prompt + "" + query)
    chatbot[-1][1] = response.text
    return chatbot

def generate_chatbot(chatbot: list[list[str, str]]) -> list[list[str, str]]:
    formatted_chatbot = []
    if len(chatbot) == 0:
        return formatted_chatbot   
    for ch in chatbot:
        formatted_chatbot.append(
            {
                "role": "user",
                "content": ch[0]    
            }
        )
        formatted_chatbot.append(
            {
                "role": "assistant",
                "content": ch[1]    
            }
        )

def initialize_chatbot():
    initial_msg = "hello! i'm alfred, your personal weather assisant. tell me the weather, and i'll tell you exactly what to wear."
    return [[None, initial_msg]]


with gr.Blocks() as demo: 
    chatbot = gr.Chatbot(
        label="alfredchatbot",
        bubble_full_width=False,
        value = initialize_chatbot()
    )
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, chatbot])
    msg.submit(
        handle_user_query,
        [msg, chatbot],
        [msg, chatbot]
    ).then(
        handle_chatbot_response,
        [chatbot],
        [chatbot]
    )

if __name__ == '__main__':
    demo.queue()
    demo.launch()