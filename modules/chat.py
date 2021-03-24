import cx_Oracle

def drop_chat( chat_id, user_id=None, username=None):
    """drop chat for user_id

    Args:
        user_id  : user id.           Default to None
        chat_id  : chat id
        username : Not allowrd param. Default to None

    Raises:
        Exception: Bad arguments. user_id == None and username == None
    """
    if (user_id == None and username == None) or chat_id == None:
        raise Exception("Bad arguments!")
    
    connection = cx_Oracle.connect("shadow7en", "93151802Vlad", "localhost:1521/XEPDB1")
    cursor     = connection.cursor()
    
    if username != None and chat_id == None:
        cursor.execute('select id from users where login = {}'.format(username))
        user_id = cursor.fetchall()[0][0]
    
    cursor.execute("delete from users_chats where user_id = {} and chat_id ={}".format(user_id, chat_id))
    connection.commit()

    connection.close()

def get_messages(chat_id):
    connection = cx_Oracle.connect("shadow7en", "93151802Vlad", "localhost:1521/XEPDB1")
    cursor     = connection.cursor()

    cursor.execute("select (select login from users where id = owner_id), text, time_send from messages where chat_id = {} order by time_send".format(chat_id))
    return [
        {
            'author' : msg[0],
            'text'   : msg[1],
            'time'   : msg[2].strftime('%d.%m.%Y  %H:%M')
        }
        for msg in cursor.fetchall()
    ]

def send_message(text, username, chat_id):
    connection = cx_Oracle.connect("shadow7en", "93151802Vlad", "localhost:1521/XEPDB1")
    cursor     = connection.cursor()

    cursor.execute("""
    insert into messages values(
        id_messages.nextval,
        {chat_id},
        '{text}',
        (select id from users where login = '{username}'),
        CURRENT_TIMESTAMP,
        '0'
        )""".format(
            username=username,
            text=text,
            chat_id=chat_id
        ))
    connection.commit()

def get_chat_name(chat_id):
    connection = cx_Oracle.connect("shadow7en", "93151802Vlad", "localhost:1521/XEPDB1")
    cursor     = connection.cursor()

    cursor.execute("select name from chats where id = {}".format(chat_id))
    return cursor.fetchall()[0][0]