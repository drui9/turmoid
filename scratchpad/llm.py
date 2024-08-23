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
            'tools': False,
            'data': {
                'system': {
                    'role': 'system',
                    'content': system_message
                }
            }
        }
    # </>

    # <> query llm
    def prompt(self, query: str, context :str = 'default'):
        q = {
            'role': 'user',
            'content': '{}'.format(query)
        }
        with self.context['lock']:
            prepend = list()
            if context not in self.context['data']:
                self.context['data'][context] = list()
            prepend = self.context['data'][context]
            out = {
                'model': self.model,
                'messages': [self.context['data']['system'], *prepend, q]
            }
            if self.context['tools']:
                with self.tools['lock']:
                    out['tools'] = [(i, i.pop('handle'))[0] for i in self.tools['items']]
            # --
            rep = self.session.post(self.endpoint, json=out)
            if rep.status_code != 200:
                raise RuntimeError(rep.content)
            response = rep.json()
            reply = response['choices'][0]
            message = reply['message']
            stop = reply['finish_reason']
            self.context['data'][context].append(q)
            self.context['data'][context].append(message)
            logger.debug(message)
            return message, stop
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
    # ai.prompt("Guess what I've been advised to name my cat.")
    # ai.prompt("Whiskers. What do you think?")
    # ai.prompt("Should I get a dog too?")
    # ai.prompt("What should I call him?")
    # ai.prompt("Who is Einstein?")
    # ai.prompt("Can you summarize this conversation?")
    # --
    params = {}
    from datetime import datetime
    ai.add_tool('current_time', 'Query datetime string', params)(lambda: datetime.now().ctime())
    ai.context['tools'] = True
    ai.prompt('What is the time?')
# </>


system = "If a list of tools is specified in the question and an informed reply cannot be generated without calling one, reply with the best matching tool name, else act like a human. Do not \
hint on the question in your reply, and do not use vocal illustration in words. Maintain brevity to save usage tokens unless the answer demands an explanation."

# --
if __name__ == '__main__':
    load_dotenv()
    ai = AI(os.getenv('GROQKEY'), system)
    test(ai)

