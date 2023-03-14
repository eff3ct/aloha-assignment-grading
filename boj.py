import requests
from bs4 import BeautifulSoup as bs


class Config:

    session  = requests.Session()
    base_url = 'https://www.acmicpc.net'
    token    = 'lmh14k9q5n00ce3q24hmabjn7k' # OnlineJudge token from your browser cookies
    headers  = { 
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Referer'   : 'https://www.acmicpc.net/'
    }
    
    lower_bound = 55437069  # 대충 lower bound
    group_id    = 17099 # ALOHA 2023 group id
    
    @classmethod
    def reset(cls):
        cls.session = requests.Session()
    
    @classmethod
    def request(cls, **kwargs):
        cookies = {}
        if 'auth' in kwargs and kwargs['auth']:
            if not cls.token:
                raise Exception('You need to login first')
            else:
                cookies['OnlineJudge'] = cls.token
            del kwargs['auth']
        if 'path' in kwargs:
            kwargs['url'] = cls.base_url + kwargs['path']
            del kwargs['path']
        response: requests.Response = cls.session.request(**kwargs, headers=cls.headers, cookies=cookies)
        if response.status_code != 200:
            raise Exception(f'HTTP error: {response.status_code} {response.reason} / {response.text}')
        return bs(response.text, 'lxml')
    
    @classmethod
    def auth(cls, token):
        cls.token = token
    

class Format:

    @staticmethod
    def json_submission(soup: bs):
        items = soup.select('td')
        data = {
            'no': int(items[0].get_text()),
            'user_id': items[1].get_text(),
            'problem_id': int(items[2].get_text()) if items[2].get_text() else None,
            'result': items[3].get_text(),
            'memory': int(items[4].get_text()) if items[4].get_text() else None,
            'time': int(items[5].get_text()) if items[5].get_text() else None,
            'language': items[6].get_text(),
            'byte': int(items[7].get_text()) if items[7].get_text() else None,
            'submitted_at': int(items[8].select_one('a')['data-timestamp'])
        }
        return data
    
    @staticmethod
    def json_practice(soup: bs):
        items = soup.select('td')
        data = {
            'practice_id': int(items[0].select_one('a')['href'].split('/')[-1]),
            'title': items[0].get_text(),
            'started_at': int(items[1].select_one('span')['data-timestamp']),
            'ended_at': int(items[2].select_one('span')['data-timestamp'])
        }
        return data

    @staticmethod
    def json_practice_problem(soup: bs):
        data = {
            'problem_id': int(soup['href'].split('/')[-1]),
            'no': int(soup.get_text().split(' - ')[0].strip()),
            'title': soup.get_text().split(' - ')[-1].strip()
        }
        return data


class Status:
    
    @classmethod
    def accepted(cls, username, top=None):
        path = '/status'
        params = { 'user_id': username, 'result_id': 4, 'top': top }
        soup = Config.request(method='GET', path=path, params=params)
        submissions = [ Format.json_submission(submission) for submission in soup.select('#status-table > tbody > tr') ]
        return submissions
    
    @classmethod
    def accepted_all(cls, username, lower_bound=Config.lower_bound):
        submissions = []
        top = None
        while top is None or top > lower_bound:
            data = cls.accepted(username, top)
            if not data: break
            submissions += data
            top = submissions[-1].get('no')-1
        return submissions
    

class Group:
    
    group_id = Config.group_id
    
    @classmethod
    def __init__(cls, group_id=Config.group_id):
        cls.group_id = group_id
    
    @classmethod
    def members(cls, order_by_rank=False):
        path = f'/group/ranklist/{cls.group_id}'
        soup = Config.request(method='GET', path=path)
        page = len(soup.select('.pagination > li'))
        members = [ member.select('td')[1].get_text() for member in soup.select('#ranklist > tbody > tr') ]
        for p in range(2,page+1):
            soup = Config.request(method='GET', path=f'{path}/{p}')
            members += [ member.select('td')[1].get_text() for member in soup.select('#ranklist > tbody > tr') ]
        return members if order_by_rank else sorted(members)

    @classmethod
    def practices(cls):
        path = f'/group/practice/{cls.group_id}'
        soup = Config.request(method='GET', path=path, auth=True)
        result = [ Format.json_practice(practice) for practice in soup.select('table > tbody > tr') ]
        print(result)
        return sorted(result, key=lambda x: x['practice_id'])

    @classmethod
    def practice_problems(cls, practice_id):
        path = f'/group/practice/view/{cls.group_id}/{practice_id}'
        soup = Config.request(method='GET', path=path, auth=True)
        return [ Format.json_practice_problem(problem) for problem in soup.select('ul.list-group.sidebar-nav-v1 > li > a')[:-1] ]

    @classmethod
    def problem_tier(cls, problem_id):
        path = f'/problem/{problem_id}'
        soup = Config.request(method='GET', path=path, auth=True)
        return soup.select('blockquote > span')[0]['class'][0].split('-')[-1]

