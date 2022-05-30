import json
import sqlite3
import requests
import streamlit as st
from bs4 import BeautifulSoup as bs
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter


class Utils:
    
    @staticmethod
    def print_json(json_data):
        json_str = json.dumps(json_data, indent=4, sort_keys=True, ensure_ascii=False)
        print(highlight(json_str, JsonLexer(), TerminalFormatter()))
    
    @staticmethod
    def json_submission(soup: bs):
        items = soup.select('td')
        data = {
            'no'         : int(items[0].get_text()),
            'user_id'    : items[1].get_text(),
            'problem_id' : int(items[2].get_text()) if items[2].get_text() else None,
            'result'     : items[3].get_text(),
            'memory'     : int(items[4].get_text()) if items[4].get_text() else None,
            'time'       : int(items[5].get_text()) if items[5].get_text() else None,
            'language'   : items[6].get_text(),
            'byte'       : int(items[7].get_text()) if items[7].get_text() else None,
            'submit_time': int(items[8].select_one('a').attrs['data-timestamp'])
        }
        return data


class Config:

    session = requests.Session()
    base_url = 'https://www.acmicpc.net'
    headers = { 
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36',
        'Referer': 'https://www.acmicpc.net/'
    }
    
    @staticmethod
    def reset():
        Config.session = requests.Session()
    
    @staticmethod
    def request(**kwargs):
        if 'headers' in kwargs:
            Config.headers.update(kwargs['headers'])
            del kwargs['headers']
        if 'path' in kwargs:
            kwargs['url'] = Config.base_url + kwargs['path']
            del kwargs['path']
        response: requests.Response = Config.session.request(**kwargs, headers=Config.headers)
        if response.status_code != 200:
            raise Exception(f'HTTP error: {response.status_code} {response.reason} / {response.text}')
        return bs(response.text, 'lxml')
    

class BOJ:

    @staticmethod
    def accepted(username, top=None):
        path = '/status'
        params = { 'user_id': username, 'result_id': 4, 'top': top }
        soup = Config.request(method='GET', path=path, params=params)
        submissions = [ Utils.json_submission(submission) for submission in soup.select('#status-table > tbody > tr') ]
        return submissions


class DB:
    
    @staticmethod
    def connect():
        return sqlite3.connect('aloha.db')

def main():
    Utils.print_json(BOJ.accepted('ymjoo12', 41444978))

if __name__ == '__main__':
    main()

