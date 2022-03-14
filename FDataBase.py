from fileinput import filename
from msilib.schema import Error
import sqlite3, math, time

class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()
    
    def getMenu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Ошибка чтения")
        return []
    
    def addPost(self, title, text, url):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM posts WHERE url LIKE '{url}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Статья с таким URL уже существует")
                return False
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO posts VALUES(NULL, ?, ?, ?, ?)", (title, text, url, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка  добавления статьи в бд"+str(e))
            return False
        return True 

    def getPost(self, alias):
        try:
            self.__cur.execute(f'SELECT title, text FROM posts WHERE url LIKE "{alias}" LIMIT 1')
            print(alias)
            res = self.__cur.fetchone()
            print(res)
            if res:
                base = url_for('static', filename='images_html')
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из бд "+str(e))
        return (False, False )
    
    def getPostsAnonce(self):
        try:
            self.__cur.execute(f"SELECT id, title, text, url FROM posts ORDER BY time DESC")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД"+str(e))
        return []