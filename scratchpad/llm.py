from dotenv import load_dotenv
import requests
import os

def main(key):
    header = { 'Authorization': 'Bearer {}'.format(key) }
    params = {
        'model': "llama3-70b-8192",
        "messages": [{
            'role': "user",
            'content': "What song goes, all of our tears will be washed in the rain when I find my way back to your arms again."
        }]
    }
    url = 'https://api.groq.com/openai/v1/chat/completions'
    rep = requests.post(url, headers=header, json=params)
    print(rep.json())

if __name__ == '__main__':
    load_dotenv()
    key = os.getenv('GROQ_KEY')
    main(key)
