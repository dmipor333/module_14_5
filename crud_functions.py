import sqlite3


def initiate_db():
    connection = sqlite3.connect('products.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM Products')  # очищаем таблицу от предыдущих записей
    # создаём таблицу продуктов и заполняем её данными
    cursor.execute('''  
    CREATE TABLE IF NOT EXISTS Products(     
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    price INTEGER NOT NULL)''')
    for i in range(1, 5):
        cursor.execute(
                'INSERT INTO Products (title, description, price) VALUES (?, ?, ?)',
            (f'Продукт {i}', f'Описание {i}', i * 100)
                      )
    # connection.commit()
    # connection.close()

    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
   # cursor.execute('DELETE FROM Users')  # очищаем таблицу от предыдущих записей
    # создаём таблицу пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users(
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    age INTEGER NON NULL,
    balance INTEGER NOT NULL)''')

    connection.commit()
    connection.close()

initiate_db()

def get_all_products():
    connection = sqlite3.connect('products.db')
    cursor = connection.cursor()
    cursor.execute('SELECT id, title, description, price FROM Products')
    db = cursor.fetchall()

    connection.commit()
    connection.close()
    return list(db)


def is_included(username):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()  # получаем данные из таблицы
    cursor.execute('SELECT * FROM Users WHERE username = ?', (username, ))
    user = cursor.fetchone()
    connection.close()
    return bool(user)


def add_user(username, email, age, balance):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    # создаём таблицу пользователей и заполняем её данными
    cursor.execute('SELECT id, username, email, age, balance FROM Users')
    # Добавляем нового пользователя в таблицу
    if not is_included(username):
        cursor.execute('INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, ?)',
                       (username, email, age, balance))

    connection.commit()
    connection.close()

