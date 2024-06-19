from autogram import Autogram, Start
from urllib.parse import quote
from datetime import datetime
from autogram import Autogram
from loguru import logger
import requests
import time
import json


class Telegram(Autogram):
    session = requests.session()
    baseurl = 'https://www.googleapis.com/youtube/v3'
    # --
    @classmethod
    def ytsearch(cls, query, api_key):
        logger.debug('Searching: {}', query)
        url = '{}/search?q={}&maxResults=32&type=video&key={}'.format(cls.baseurl, quote(query), api_key)
        if (rep := cls.session.get(url)).ok:
            items = list()
            parts='snippet'
            for item in rep.json()['items']:
                it = item['id']['videoId']
                url = '{}/videos?part={}&id={}&key={}'.format(cls.baseurl,parts, it, api_key)
                if (res := cls.session.get(url)).ok:
                    metadata = res.json()['items']
                    items.extend([i['snippet'] for i in metadata])
            return items
        logger.warning('Search failed: {}', rep.content)

    #--
    @Autogram.add('message')
    def message(self, bot: Autogram, update):
        key = bot.settings('gcloud-api-key')
        message = update['message']
        chat_id = update['message']['chat']['id']
        # --
        keyb = [[{'text': 'Testing', 'callback_data': 'tested'}]]
        data = {
            'reply_markup': bot.getInlineKeyboardMarkup(keyb)
        }
        res = bot.sendMessage(chat_id, 'Welcome!', **data)
        print(res.status_code, res.json())
        # if message['text'] == '/start':
        #     bot.sendMessage(chat_id, 'Welcome back! What for?')
        # else:
        #     if not (results := ytsearch(message['text'], key)):
        #         bot.sendMessage(chat_id, 'Sorry. Nothing found.')
        #     else:
        #         username = update['message']['chat']['username']
        #         try:
        #             data = bot.data(username) or dict()
        #         except KeyError:
        #             data = dict()
        #         data['results'] = results
        #         item = results[0]
        #         title = item['title']
        #         pubDate = datetime.fromisoformat(item['publishedAt']).ctime()
        #         thumb = item['thumbnails']['standard']['url']
        #         vid = thumb.split('/')[-2]
        #         caption = '{}[{}]\nPublished on: [{}]'.format(title, vid, pubDate)
        #         if (res := session.get(thumb)).ok:
        #             keyb = {
        #                 'params': {
        #                     'reply_markup': bot.getInlineKeyboardMarkup([[{'ok': True, 'callback_data':'y'}]])
        #                 }
        #             }
        #             if (ok := bot.sendPhoto(chat_id, res.content, caption, keyb)):
        #                 out = ok.json()
        #                 msgid = out['result']['message_id']
        #                 time_out = out['result']['date']
        #                 data['current'] = {
        #                     'message-id': msgid,
        #                     'date': time_out,
        #                     'result-id': vid
        #                 }
        #                 bot.data(username, data)

    #--
    @Autogram.add('callback_query')
    def callback_query(bot: Autogram, update):
        print('callback_query:', update)
        call_id = update['callback_query']['id']
        rep = bot.answerCallbackQuery(call_id, 'Processing')
        print(rep.json())
        return

    #--
    def __init__(self, config):
        super().__init__(config)
        self.search = dict()

    #--
    def run(self):
        super().run()
        print(self.data('offset'))

#**************** <start>
@Start('yeatbeat.json')
def main(config):
    global api_key
    bot = Telegram(config)
    bot.run()
#-- </start>
