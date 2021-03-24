import cx_Oracle, hashlib


class User:
    """[User class with connect from  oracle database]"""

    def __init__(self, login=None, password=None):
        """
        Init

        Args:
            login ([string], optional): [Login, seted on register]. Defaults to None.
            password ([string], optional): [Password, seted on register]. Defaults to None.

        Raises:
            Exception: [Not valid login or password]
        """

        #Check empty values
        if login == None or password == None:
            raise Exception("Not valid login or password!")
        
        #Hashed password
        password_hash = hashlib.md5(password.encode()).hexdigest()

        #Create connection and cursor
        self.connection = cx_Oracle.connect("shadow7en", "93151802Vlad", "localhost:1521/XEPDB1")
        self.cursor = self.connection.cursor()

        #Create query
        self.cursor.execute("select * from users where login='{}' and password='{}'".format(login, password_hash) )
        result = self.cursor.fetchall()

        #Check exist user
        if len(result) == 0:
            raise Exception("Not valid login or password!")

        self.uid    = result[0][0] 
        self.key    = login + ';' + password

    def get_chats(self):
        """
        Get chats for self user

        Raises:
            Exception: [Not conntion from db]

        Returns:
            [dict's arr]: [
                {
                    'id'          : ... ,
                    'name'        : ... ,
                    'admin'       : ... ,
                    'count_msg'   : ... ,
                    'count_users' : ...
                },
                ...
            ]
        """
        
        #Result arr
        result = []
        
        #Create query
        try:
            self.cursor.execute("select id, name, admin_id from chats where id in (select chat_id from users_chats  where users_chats.users_id = {uid})".format(
                uid=self.uid)
                )
        except Exception as e:
            raise e

        answer = self.cursor.fetchall()
        for data in answer:
            try:
                #Create chat data collection
                self.cursor.execute("select login from users where id = {}".format(data[2]))

                result.append({
                    'name'  : data[1],
                    'id'    : data[0],
                    'admin' : self.cursor.fetchall()[0][0],
                })
                
                self.cursor.execute("select count(*) from messages where chat_id = {}".format(data[0]))
                result[-1]['count_msg'] = self.cursor.fetchall()[0][0]
                
                self.cursor.execute("select count(*) from users_chats where chat_id = {}".format(data[0]))
                result[-1]['count_users'] = self.cursor.fetchall()[0][0]
            except:
                pass
        
        return result


def register_user(login, password, name, surname, email, department, rank, headers):
    """
    Register new user

    Args:
        login ([string], optional): [Login, seted on register page]. 
        password ([string], optional): [Password, seted on register page].
        name ([string], optional): [Name, seted on register page].
        email ([string], optional): [email, seted on register page].
        department ([string], optional): [department, seted on register page].
        rank ([string], optional): [rank, seted on register page].
        headers ([arr], optional): [browser headers].

    Raises:
        
    """
    
    #Create connection from database
    try:
        connection = cx_Oracle.connect("shadow7en", "93151802Vlad", "localhost:1521/XEPDB1") 
        cursor = connection.cursor()
    except:
        raise Exception("Trouble connect to database!")

    #Check login
    cursor.execute("select * from users where login = '{}'".format(login))
    answer = cursor.fetchall()

    if (len(answer) != 0):
        raise Exception("Login already registered!")
    
    #Check department name
    cursor.execute("select * from department where name = '{}'".format(department))
    answer = cursor.fetchall()
    print(answer)
    if (len(answer) == 0):
        raise Exception("No correct department name!")
    
    connection.commit()

    #If all good. Create new user
    cursor.execute("insert into users values(id_users.nextval, '{login}', '{email}', '{password}', CURRENT_TIMESTAMP)".format(
                login=login,
                password=hashlib.md5(password.encode()).hexdigest(),
                email=email
            ))

    cursor.execute("""
        insert into session_info(browser, ip_address, time_sign, user_id) values(
            '{browser}', '{ip_addr}', CURRENT_TIMESTAMP, (select id from users where login='{login}')
        )""".format(
            browser=headers['Sec-ch-Ua'],
            ip_addr=headers['Host'],
            login=login
        ))
    connection.commit()
    
    cursor.execute("""
        insert into user_info values(
            (select id from users where login='{login}'), '{name}', '{surname}', (select id from department where name='{dep_name}'), '{rank}'
        )
        """.format(
            login=login,
            name=name,
            surname=surname,
            dep_name=department,
             rank=rank
        ))

    connection.commit()


def update_session(login, headers):
    #Create connection from database
    try:
        connection = cx_Oracle.connect("shadow7en", "93151802Vlad", "localhost:1521/XEPDB1") 
        cursor = connection.cursor()
    except:
        raise Exception("Trouble connect to database!")

    #Query execute
    cursor.execute("""
        insert into session_info(browser, ip_address, time_sign, user_id) values(
            '{browser}', '{ip_addr}', CURRENT_TIMESTAMP, (select id from users where login='{login}')
        )""".format(
            browser=headers['Sec-ch-Ua'],
            ip_addr=headers['Host'],
            login=login
        ))
    connection.commit()
                