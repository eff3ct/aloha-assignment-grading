import sqlite3


class DB:
    
    db = None
    
    @classmethod
    def connect(cls):
        cls.db = sqlite3.connect('aloha.db')
        return cls.db

    @classmethod
    def init(cls):
        cls.connect()
        cls.db.execute('''
            CREATE TABLE IF NOT EXISTS members (
                user_id TEXT PRIMARY KEY,
                level INTEGER,
                group_no INTEGER
            )
        ''')
        cls.db.execute('''
            CREATE TABLE IF NOT EXISTS problems (
                problem_id INTEGER PRIMARY KEY,
                title TEXT
            )
        ''')
        cls.db.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                no INTEGER PRIMARY KEY,
                user_id TEXT,
                problem_id INTEGER,
                result TEXT,
                memory INTEGER,
                time INTEGER,
                language TEXT,
                byte INTEGER,
                submitted_at INTEGER,
                CONSTRAINT user_id_fk FOREIGN KEY (user_id) REFERENCES members (user_id),
                CONSTRAINT problem_id_fk FOREIGN KEY (problem_id) REFERENCES problems (problem_id)
            )
        ''')
        cls.db.execute('''
            CREATE TABLE IF NOT EXISTS practices (
                practice_id INTEGER PRIMARY KEY,
                title TEXT,
                started_at INTEGER,
                ended_at INTEGER
            )
        ''')
        cls.db.execute('''
            CREATE TABLE IF NOT EXISTS practice_problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                practice_id INTEGER,
                problem_id INTEGER,
                no INTEGER,
                title TEXT,
                is_required INTEGER,
                CONSTRAINT practice_id_fk FOREIGN KEY (practice_id) REFERENCES practices (practice_id),
                CONSTRAINT problem_id_fk FOREIGN KEY (problem_id) REFERENCES problems (problem_id)
            )
        ''')
        cls.db.commit()
    
    @classmethod
    def tables(cls):
        cls.connect()
        return [
            table for table, 
            in cls.db.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall()
            if table != 'sqlite_sequence'
        ]

    @classmethod
    def drop(cls, table):
        cls.connect()
        cls.db.execute(f'DROP TABLE {table}')
        cls.db.commit()
        
    @classmethod
    def insert_member(cls, user_id):
        cls.init()
        cls.db.execute('''
            INSERT INTO members (user_id) VALUES (?)
        ''', (user_id,))
        cls.db.commit()
        
    @classmethod
    def insert_problem(cls, problem_id, title=None):
        cls.init()
        if cls.db.execute(f'SELECT * FROM problems WHERE problem_id={problem_id}').fetchone():
            return
        cls.db.execute('''
            INSERT INTO problems (problem_id, title) VALUES (?, ?)
        ''', (problem_id, title))
        cls.db.commit()
    
    @classmethod
    def insert_submission(cls, no, user_id, problem_id, result, memory, time, language, byte, submitted_at):
        cls.init()
        cls.db.execute('''
            INSERT INTO submissions (no, user_id, problem_id, result, memory, time, language, byte, submitted_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (no, user_id, problem_id, result, memory, time, language, byte, submitted_at))
        cls.db.commit()
        
    @classmethod
    def insert_practice(cls, practice_id, title, started_at, ended_at):
        cls.init()
        cls.db.execute('''
            INSERT INTO practices (practice_id, title, started_at, ended_at) VALUES (? ,?, ?, ?)
        ''', (practice_id, title, started_at, ended_at))
        cls.db.commit()
    
    @classmethod
    def insert_practice_problem(cls, practice_id, problem_id, no, title):
        cls.init()
        cls.db.execute('''
            INSERT INTO practice_problems (practice_id, problem_id, no, title) VALUES (?, ?, ?, ?)
        ''', (practice_id, problem_id, no, title))
        cls.db.commit()
        
    @classmethod
    def select_members(cls):
        cls.init()
        return cls.db.execute('SELECT * FROM members').fetchall()
    
    @classmethod
    def select_problems(cls):
        cls.init()
        return cls.db.execute('SELECT * FROM problems').fetchall()
    
    @classmethod
    def select_submissions(cls, user_id, started_at, ended_at):
        cls.init()
        return cls.db.execute('SELECT * FROM submissions WHERE user_id = ? AND submitted_at BETWEEN ? AND ? GROUP BY problem_id', (user_id, started_at, ended_at)).fetchall()
    
    @classmethod
    def get_practice(cls, practice_id):
        cls.init()
        return cls.db.execute('SELECT * FROM practices WHERE practice_id = ?', (practice_id,)).fetchone()
    
    @classmethod
    def select_practices(cls):
        cls.init()
        return cls.db.execute('SELECT * FROM practices').fetchall()
    
    @classmethod
    def select_practice_problems(cls, practice_id):
        cls.init()
        return cls.db.execute('SELECT * FROM practice_problems WHERE practice_id = ?', (practice_id,)).fetchall()
