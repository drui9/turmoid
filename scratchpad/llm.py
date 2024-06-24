from dotenv import load_dotenv
import requests
import os

def main(key):
    header = { 'Authorization': 'Bearer {}'.format(key) }
    params = {
        'model': "llama3-70b-8192",
        "messages": [{
            'role': "user",
            'content': "Explain how to simulate the collapse of a quantum function using two sets of bit arrays together with and bitwise operator."
        }]
    }
    url = 'https://api.groq.com/openai/v1/chat/completions'
    rep = requests.post(url, headers=header, json=params)
    print(rep.json())

if __name__ == '__main__':
    load_dotenv()
    key = os.getenv('GROQ_KEY')
    main(key)
