import json
import csv
import boj
from db import DB

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter


class Utils:
    
    @staticmethod
    def print_json(json_data):
        json_str = json.dumps(json_data, indent=4, sort_keys=True, ensure_ascii=False)
        print(highlight(json_str, JsonLexer(), TerminalFormatter()))
        
    @staticmethod
    def save_json(json_data, file_name):
        with open(file_name, 'w') as f:
            json.dump(json_data, f, indent=4, sort_keys=True, ensure_ascii=False)


class Data:
    
    @staticmethod
    def init():
        for table in DB.tables():
            DB.drop_table(table)
        DB.init()
        
    @classmethod
    def update_all(cls):
        cls.update_members()
        cls.update_practices()
        cls.update_submissions()
    
    @staticmethod
    def update_members():
        user_ids = boj.Group.members()
        for user_id in user_ids:
            DB.insert_member(user_id)
    
    @staticmethod
    def load_members():
        return [user[0] for user in DB.select_members()]
    
    @staticmethod
    def update_submissions(verbose=False):
        members = Data.load_members()
        for member in members[3:]:
            submissions = boj.Status.accepted_all(member)
            if verbose: print(f'{member}: {len(submissions)}')
            for submission in submissions:
                DB.insert_submission(*submission.values())
                
    @staticmethod
    def update_practices():
        practices = boj.Group.practices()
        for practice in practices:
            DB.insert_practice(*practice.values())
            problems = boj.Group.practice_problems(practice['practice_id'])
            for problem in problems:
                DB.insert_problem(problem['problem_id'], problem['title'])
                DB.insert_practice_problem(practice['practice_id'], *problem.values())
    
    @staticmethod
    def load_practices():
        return [practice for practice in DB.select_practices()]
    
    @staticmethod
    def load_practice_problems(practice_id):
        return [problem for problem in DB.select_practice_problems(practice_id)]

    @staticmethod
    def calc_ac(user_id, practice_id):
        practice = DB.get_practice(practice_id)
        week = 7 * 24 * 60 * 60 * 1000
        problems = [problem[2] for problem in DB.select_practice_problems(practice_id)]
        submissions = [submission[2] for submission in DB.select_submissions(user_id, practice[2]-week, practice[3]+week)]
        return [ac for ac in submissions if ac in problems]


def main():
    members = Data.load_members()
    practices = Data.load_practices()
    titles = ['handle'] + [practice[1] for practice in practices]
    rows = { str(member): [len(Data.calc_ac(member, practice[0])) for practice in practices] for member in members }
    with open('assignment.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['handle'] + [practice[1] for practice in practices])
        for row in rows.items():
            writer.writerow([row[0]] + row[1])


if __name__ == '__main__':
    main()
