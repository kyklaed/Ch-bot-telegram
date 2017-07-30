
import mysql.connector

class Add_new_news:
    def __init__(self,database,table):
        self.connection = mysql.connector.connect(host="localhost", user='root', passwd='', db=database,
                                                  charset='utf8')
        self.cursor = self.connection.cursor()
        self.table = table

    def addtable(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS `%s` (
	`id` INTEGER(200) NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`user_id` INTEGER(40),
	`user_name` VARCHAR(100),
	`text` VARCHAR(1000),
	`photo` VARCHAR(1000),
	`date` VARCHAR(40),
	`chekpost`INTEGER(1))""",(self.table, ))

    def add_news(self,user_id,user_name,text_u,photo_u,date_u):
        print(date_u)
        self.cursor.execute("INSERT INTO `%s` (`user_id`,`user_name`,`text`,`photo`,`date`) VALUES (%s,%s,%s,%s,%s)",(self.table,user_id,user_name,text_u,photo_u,date_u))
        self.cursor.fetchone()
        self.connection.commit()

    def select_news(self,date_u):
        self.cursor.execute("SELECT id, user_id, text, photo,user_name FROM `%s` WHERE  date = %s and chekpost IS NULL",(self.table,date_u))
        return self.cursor.fetchall()

    def c_news(self,date_u):
        self.cursor.execute("SELECT count(id) FROM `%s` WHERE  date = %s and chekpost IS NULL",
                            (self.table, date_u))
        return self.cursor.fetchone()

    def update_checkpost(self,checknum,id_db):
        self.cursor.execute("UPDATE `%s` SET chekpost = %s WHERE id = %s", (self.table,checknum,id_db))
        self.cursor.fetchone()
        self.connection.commit()

    def close(self):
        self.connection.close()

class Check_blacklist:
    def __init__(self, database, table):
        self.connection = mysql.connector.connect(host="localhost", user='root', passwd='Cgbhn96%', db=database,
                                                  charset='utf8')
        self.cursor = self.connection.cursor()
        self.table = table

    def addtable(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS `%s` (
        `id` INTEGER(20) NOT NULL PRIMARY KEY AUTO_INCREMENT,
        `user_id` INTEGER(40),
        `date` VARCHAR(40))""", (self.table,))

    def add_to_blacklist(self, user_id, date_d):
        self.cursor.execute("INSERT INTO `%s` (`user_id`,`date`) VALUES (%s,%s)",(self.table, user_id, date_d))
        self.cursor.fetchone()
        self.connection.commit()

    def chk_list(self,user_id):
        self.cursor.execute("SELECT user_id FROM `%s` WHERE user_id = %s", (self.table,user_id))
        return self.cursor.fetchall()




