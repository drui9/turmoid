from dotenv import load_dotenv
from threading import Lock
from loguru import logger
import requests
import os

class AI:
    model = "llama3-70b-8192"
    endpoint = 'https://api.groq.com/openai/v1/chat/completions'
    # <> constructor
    def __init__(self, key: str, system_message: str):
        assert key, 'Missing key!'
        self.session = requests.session()
        self.session.headers = { 'Authorization': 'Bearer {}'.format(key) }
        self.tools = {
            'lock': Lock(),
            'items': list()
        }
        self.context = {
            'lock': Lock(),
            'usage': 0,
            'data': {
                'system': {
                    'role': 'system',
                    'content': system_message
                }
            }
        }
    # </>

    # <> query llm
    def prompt(self, query: str, context :str = 'default', hist_count=2, tool_call=False):
        q = {
            'role': 'user',
            'content': '{}'.format(query)
        }
        with self.context['lock']:
            prepend = list()
            if context not in self.context['data']:
                self.context['data'][context] = list()
            else:
                prepend = self.context['data'][context][0 - hist_count:]
            out = {
                'model': self.model,
                'messages': [self.context['data']['system'], *prepend, q]
            }
            if tool_call:
                with self.tools['lock']:
                    out['tools'] = [(i, i.pop('handle'))[0] for i in self.tools['items']]
            # --
            logger.debug(out['messages'])
            rep = self.session.post(self.endpoint, json=out)
            logger.debug(rep.json().keys())
            if rep.status_code == 200:
                response = rep.json()
                reply = response['choices'][0]
                self.context['usage'] += reply['total_tokens']
                print('<<', reply)
                return reply
            else:
                logger.debug(rep.content)
    # </>

    # <> register a function
    def add_tool(self, name:str, desc:str, params:dict):
        def wrapper(func):
            tool = {
                "handle": func,
                "type": "function",
                "function": {
                    "name": name,
                    "description": desc,
                },
            }
            if params:
               tool['function'] |= {
                    "parameters": {
                        "type": "object",
                        "properties": params.get('properties'),
                    "required": params.get('required') or list(),
                    }
                }
            with self.tools['lock']:
                return self.tools['items'].append(tool)
        return wrapper
        # </>

# <> test
def test(ai):
    ai.prompt("Guess what I've been advised to name my cat.")
    ai.prompt("Whiskers. What do you think?")
    # --
    # params = {}
    # from datetime import datetime
    # ai.add_tool('current_time', 'Query datetime string', params)(lambda: datetime.now().ctime())
    # ai.prompt('What is the time?', tool_call=True)
# </>


system = """ You are an android personal assistant with access to tools you can call.\
To load context data from tools, strictly respond with a json object {"TOOLING": tool_name} \
, picking tool_name from the specified list, and wait for the next prompt before you answer.\
Accurately provide accurate responses through critical evaluation."""

# --
if __name__ == '__main__':
    load_dotenv()
    ai = AI(os.getenv('GROQKEY'), system)
    test(ai)

