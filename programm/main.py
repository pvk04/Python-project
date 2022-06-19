from tkinter import *
import pymysql
from config import host, user, password, db_name  # Модуль с данными для подключания к бд
import random


def registration():  # Функция регистрации в приложении
    login = entry_login.get()
    password = entry_password.get()
    check = True

    if login == "" or password == "":  # Валидация данных для регистрации
        error_label["text"] = 'Заполните все поля!'
        check = False
    elif " " in login:
        error_label["text"] = 'В логине не может быть пробелов!'
        check = False
    elif " " in password:
        error_label["text"] = 'В пароле не может быть пробелов!'
        check = False
    elif len(login) < 6 or len(password) < 6:
        error_label["text"] = 'Логин и пароль должны быть длиннее 5 символов'
        check = False
    elif login != "" and password != "":
        cursor.execute("SELECT login FROM accounts;")
        logins = cursor.fetchall()
        for login_row in logins:
            print(login_row)
            if login_row["login"] == login:
                error_label["text"] = 'Такой логин занят!'
                check = False

    if check:  # Добавление записи об аккаунте в бд
        cursor.execute(f"insert into accounts (login, password) values ('{str(login)}', '{str(password)}');")
        connection.commit()

        cursor.execute("SELECT * FROM accounts;")
        logins = cursor.fetchall()
        for login_row in logins:
            if login_row["login"] == login and login_row["password"] == password:
                account_id = login_row["idaccount"]

        cursor.execute(f"insert into account_info values ({str(account_id)}, 0, 0);")
        connection.commit()

        error_label["text"] = 'Вы зарегистрировались'


def login():  # Функция авторизации в приложении
    global account_id # Глобальная переменная, в которую поместится айди аккаунта, в который вошли
    login = entry_login.get()
    password = entry_password.get()

    if login == "" or password == "":  # Валидация данных при авторизации
        error_label["text"] = 'Заполните все поля!'
    if login != "" and password != "":
        cursor.execute("SELECT * FROM accounts;")
        logins = cursor.fetchall()
        for login_row in logins:
            if login_row["login"] == login and login_row["password"] == password:
                account_id = login_row["idaccount"]
                root.deiconify()
                auth.destroy()
                return
    try:
        error_label["text"] = 'Неверный логин или пароль'
    except Exception:
        pass


def main_menu():  # Функция, отрисовыващая главное меню
    # Удаление всех элементов с виджета root
    list = root.grid_slaves()
    for elem in list:
        elem.destroy()

    # Конфигурация виджета
    for i in range(5):
        root.grid_columnconfigure(i, minsize=100)
    root.rowconfigure(0, minsize=100)
    for i in range(1, 5):
        root.rowconfigure(i, minsize=60)

    root.title("Главное меню")
    root["bg"] = "white"

    # Отрисовка меню
    menu_lab = Label(root, text="МЕНЮ", bg="white", font=("Montserrat", 20))
    menu_lab.grid(row=0, column=1, columnspan=3, stick='we')

    button_play = Button(root, text="Играть", font=("Montserrat", 14), command=play)
    button_play.grid(row=1, column=1, columnspan=3, stick='we')

    button_account = Button(root, text="Аккаунт", font=("Montserrat", 14), command=open_account)
    button_account.grid(row=2, column=1, columnspan=3, stick='we')

    button_leaderboard = Button(root, text="Таблица лидеров", font=("Montserrat", 14), command=open_leaderboard)
    button_leaderboard.grid(row=3, column=1, columnspan=3, stick='we')

    button_rules = Button(root, text="Правила", font=("Montserrat", 14), command=open_rules)
    button_rules.grid(row=4, column=1, columnspan=3, stick='we')


def play():  # Функция отрисовки виждета игры
    global found_letters  # Массив с найденными буквами
    global not_match_letters  # Массив с лишними буквами
    global attempts_num  # Количество попыток
    attempts_num = 5
    found_letters = []
    not_match_letters = []

    root.title("Игра")

    # Очистка виджета root
    list = root.grid_slaves()
    for elem in list:
        elem.destroy()

    root["bg"] = "grey"

    # Открытие файла и считываение слов
    words_file = open("words.txt", "r", encoding="utf-8")
    words = words_file.read().split(" ")
    random_word = words[random.randint(0, len(words) - 1)]  # Загаданное слово
    print("Загаданное слово: " + random_word)

    # Конфигурация виджета
    for i in range(5):
        root.grid_columnconfigure(i, minsize=90)
    for i in range(8):
        root.grid_rowconfigure(i, minsize=55)

    # Отрисовка виджета игры
    lab1 = Label(root, text="Введите слово:", font=("Montserrat", 11), bg='grey')
    lab1.grid(row=0, column=1, columnspan=2, sticky='ws')

    lab2 = Label(root, text=f"Попытки: {attempts_num}", font=("Montserrat", 11), bg='grey')
    lab2.grid(row=0, column=3, sticky='se')

    entry_word = Entry(root, font=("Montserrat", 14), justify=CENTER, bd=5)
    entry_word.bind('<KeyPress>', lambda event: char_limit(event, entry_word, '4'))
    entry_word.grid(row=1, column=1, columnspan=3, sticky='we')

    lab3 = Label(root, text="Найденные буквы:", font=("Montserrat", 11), bg='grey')
    lab3.grid(row=2, column=1, sticky='ws')

    letters = Label(root, text="", font=("Montserrat", 20), bd=1)
    letters.grid(row=3, column=1, columnspan=3, sticky='we', pady=0)

    lab4 = Label(root, text="Лишние буквы:", font=("Montserrat", 11), bg='grey')
    lab4.grid(row=4, column=1, sticky='ws', pady=0)

    letters_not_match = Label(root, text="", font=("Montserrat", 20), bd=1)
    letters_not_match.grid(row=5, column=1, columnspan=3, sticky='we')

    button_try = Button(root, text="Проверить", font=("Montserrat", 12), command=lambda: check_word(entry_word, random_word, words, lab_err, lab2, letters, letters_not_match))
    button_try.grid(row=6, column=1, columnspan=3, sticky='we', pady=10)

    lab_err = Label(root, text="", bg='grey', fg='white', font=("Montserrat", 10))
    lab_err.grid(row=7, column=0, columnspan=5)


def char_limit(event, entry, count):  # Функция, позволяющая лимитировать ввод символов в поле Entry
    keys = [49, 50, 51, 52, 53, 54, 55, 56, 57, 48, 189, 187, 81, 87, 69, 82, 84, 89, 85, 73, 79, 80, 219, 221, 220, 65,
            83, 68, 70, 71, 72, 74, 75, 76, 186, 222, 90, 88, 67, 86, 66, 78, 77, 188, 190, 191, 192]
    for key in keys:
        if event.keycode == key:
            entry.delete(count, END)


def check_word(entry, solve, arr, err, attempts_lab, label, label2):  # Функция проверки введенного пользователем слова
    global attempts_num  # Количество попыток
    global found_letters  # Найденные буквы
    global not_match_letters  # Лишние буквы

    # Вспомогательные переменные
    users_word = entry.get().lower()
    solve = solve.lower()
    contains = False

    err["text"] = ""
    err["bg"] = "grey"
    label["text"] = ""
    label2["text"] = ""
    word_for_check = ""

    if users_word == solve and attempts_num != 0:  # Если пользователь угадал слово
        cursor.execute(f"update account_info set total_solved = total_solved + 1 where account = {account_id};")
        connection.commit()

        cursor.execute(f"update account_info set spend_points = spend_points + {attempts_num*10} where account = {account_id};")
        connection.commit()

        list = root.grid_slaves()
        for elem in list:
            elem.destroy()

        # Отрисовка окна победы
        root["bg"] = "white"
        lab = Label(root, text="Вы угадали!", font=("Montserrat", 20), bg="white")
        lab.grid(row=0, column=1, columnspan=3)

        lab1 = Label(root, text=f"Вы получаете: {attempts_num*10} очков", font=("Montserrat", 14), bg="white")
        lab1.grid(row=1, column=1, columnspan=3, sticky='we')

        button_play_again = Button(root, text="Играть снова", font=("Montserrat", 14), command=play)
        button_play_again.grid(row=2, column=2, pady=100)

        button_menu = Button(root, text="Меню", font=("Montserrat", 14), command=main_menu)
        button_menu.grid(row=3, column=2, pady=10)
    else:  # Валидация введенного пользователем слова
        for elem in arr:
            if users_word == elem.lower():
                contains = True
                word_for_check = elem.lower()
                break

    if contains:  # Проверка слова после прохождения валидации
        for let in range(len(solve)):
            if word_for_check[let] in solve:  # Если есть одинаковые буквы
                contains_status = True
                for letter in found_letters:
                    if letter == word_for_check[let]:  # Есть ли в массие эти буквы
                        contains_status = False
                if contains_status:
                    found_letters.append(word_for_check[let])  # Добавление новых букв в массив найденных букв
            if word_for_check[let] not in solve:  # Одинаковых букв нет
                contains_status = True
                for letter in not_match_letters:
                    if letter == word_for_check[let]:  # Есть ли в массиве эти буквы
                        contains_status = False
                if contains_status:
                    not_match_letters.append(word_for_check[let])  # Добавление новых букв в массив лишних букв
        attempts_num -= 1  # Уменьшение числа попыток
    else:  # Слово не прошло валидацию
        if len(users_word) < 5:
            err["bg"] = "dark red"
            err["text"] = "Введите слово из 5 букв"
        else:
            err["bg"] = "dark red"
            err["text"] = "Такого слова нет в нашем словаре"

    if attempts_num == 0:  # Закончились попытки
        list = root.grid_slaves()
        for elem in list:
            elem.destroy()

        # Отрисовка окна поражения
        root["bg"] = "white"
        lab = Label(root, text="Попытки закончились!", font=("Montserrat", 20), bg="dark red", fg="white")
        lab.grid(row=0, column=1, columnspan=3)

        lab1 = Label(root, text=f"Загаданное слово: {solve}", font=("Montserrat", 14), bg="white")
        lab1.grid(row=1, column=1, columnspan=3, sticky='we')

        button_play_again = Button(root, text="Играть снова", font=("Montserrat", 14), command=play)
        button_play_again.grid(row=2, column=2, pady=100)

        button_menu = Button(root, text="Меню", font=("Montserrat", 14), command=main_menu)
        button_menu.grid(row=3, column=2, pady=10)

    for letter in found_letters:  # Отрисовка найденных букв
        label["text"] += letter

    for letter in not_match_letters:  # Отрисовка лишних букв
        label2["text"] += letter

    attempts_lab["text"] = f"Попыток: {attempts_num}"  # Отрисовка числа попыток


def open_leaderboard():  # Функция открытия таблицы лидеров
    # Создание окна Toplevel и скрытие виджета root
    root.withdraw()
    leaderboard = Toplevel(root)
    leaderboard.title("Правила")
    leaderboard.resizable(width=False, height=False)
    leaderboard.title("Таблица лидеров")

    # Расположение окна по середине экрана
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    w = w // 2
    h = h // 2
    leaderboard.geometry(f'500x450+{w - 250}+{h - 225}')

    # Конфигурация виджета
    for i in range(3):
        leaderboard.grid_columnconfigure(i, minsize=150, weight=1)
    for i in range(7):
        leaderboard.rowconfigure(i, minsize=20, weight=1)

    # Отрисовка
    header = Label(leaderboard, font=("Montserrat", 14), text="ТОП 5:")
    header.grid(row=0, column=1)

    cursor.execute("select * from account_info order by spend_points desc limit 5;")  # Запрос на топ 5 лучщих игроков по количеству очков
    leaderboard_top = cursor.fetchall()
    row_num = 1  # Вспомогательная переменная
    for elem in leaderboard_top:
        cursor.execute(f"select login from accounts where idaccount = {elem['account']}")
        name = cursor.fetchall()
        name = name[0]['login']

        Label(leaderboard, font=("Montserrat", 14), text=f"{row_num} место. {name}, очки: {elem['spend_points']};")\
            .grid(row=row_num, column=0, columnspan=3, sticky='we')
        row_num += 1
    menu_button = Button(leaderboard, text="Назад", font=("Montserrat", 14), command=lambda: back(leaderboard, root))
    menu_button.grid(row=7, column=1)


def open_rules():  # Функция открытия правил
    # Создание окна Toplevel и скрытие root
    root.withdraw()
    rules = Toplevel(root)
    rules.title("Правила")
    rules.resizable(width=False, height=False)

    # Расположение окна по середине экрана
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    w = w // 2
    h = h // 2
    rules.geometry(f'500x450+{w - 250}+{h - 225}')

    # Отрисовка
    rules_lab = Label(rules, font=("Montserrat", 14), wraplength=450, justify="left")
    rules_lab["text"] = "Игра загадывает слово из 5 букв и вам нужно его отгадать. " \
                        "Вы должны ввести слово из 5 букв. " \
                        "Если буквы из введенного слова есть в загаданном, они поместятся в поле " \
                        "'Найденные буквы', если их нет, то они отобразятся в поле 'Лишние буквы'. Всего дано 5 попыток." \
                        "\nОчки начисляются если вы угадаете слово, по принципу: количество оставшихся попыток * 10."
    rules_lab.pack(side=TOP, pady=30)

    button_back = Button(rules, text="Назад", font=("Montserrat", 14), command=lambda: back(rules, root))
    button_back.pack(side=BOTTOM, pady=10)


def open_account():  # Функция открытия информации об аккаунте
    # Создание окна Toplevel и скрытие root
    root.withdraw()
    account = Toplevel(root)
    account.title("Аккаунт")
    account.resizable(width=False, height=False)

    # Расположение окна по середине экрана
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    w = w // 2
    h = h // 2
    account.geometry(f'500x450+{w - 250}+{h - 225}')

    # Конфигурация виджета
    for i in range(3):
        account.grid_columnconfigure(i, minsize=150, weight=1)

    cursor.execute(f"select login from accounts where idaccount = {account_id}")  # Запрос на получение данных авторизированного аккаунта
    account_auth = cursor.fetchall()

    cursor.execute(f"select total_solved, spend_points from account_info where account = {account_id}")  # Запрос на получение данных об аккаунте
    account_info = cursor.fetchall()

    # Отрисовка
    head_lab = Label(account, font=("Montserrat", 14), text="Мой аккаунт")
    head_lab.grid(row=0, column=0, columnspan=3, sticky='we', pady=20)
    error_label = Label(account, font=("Montserrat", 10), text="", fg="red")
    error_label.grid(row=8, column=0, columnspan=3, sticky='we', pady=20)

    login_lab = Label(account, font=("Montserrat", 12), text=f"Логин: {account_auth[0]['login']}")
    login_lab.grid(row=1, column=0, columnspan=3, sticky='we', pady=5)

    total_solved_lab = Label(account, font=("Montserrat", 12), text=f"Всего решено: {account_info[0]['total_solved']}")
    total_solved_lab.grid(row=2, column=0, columnspan=3, sticky='we', pady=5)

    points_lab = Label(account, font=("Montserrat", 12), text=f"Очки: {account_info[0]['spend_points']}")
    points_lab.grid(row=3, column=0, columnspan=3, sticky='we', pady=5)

    old_password_lab = Label(account, font=("Montserrat", 12), text="Старый пароль: ")
    old_password_lab.grid(row=4, column=0)
    old_password_entry = Entry(account, bd=3)
    old_password_entry.bind('<KeyPress>', lambda event: char_limit(event, old_password_entry, '14'))
    old_password_entry.grid(row=4, column=1)

    new_password_lab = Label(account, font=("Montserrat", 12), text="Новый пароль: ")
    new_password_lab.grid(row=5, column=0)
    new_password_entry = Entry(account, bd=3)
    new_password_entry.bind('<KeyPress>', lambda event: char_limit(event, new_password_entry, '14'))
    new_password_entry.grid(row=5, column=1)

    button_save = Button(account, text="Сохранить", font=("Montserrat", 14), command=lambda: change_password(old_password_entry.get(), new_password_entry.get(), error_label))
    button_save.grid(row=6, column=1, pady=5)

    button_back = Button(account, text="Назад", font=("Montserrat", 14), command=lambda: back(account, root))
    button_back.grid(row=7, column=1, pady=5)


def change_password(old, new, lab):  # Функция смены пароля
    # Вспомогательные переменные
    check = True
    lab["text"] = ""
    lab["fg"] = "red"

    cursor.execute(f"select password from accounts where idaccount = {account_id}")  # Запрос на получение текущего пароля
    old_pass = cursor.fetchall()

    if old == "" or new == "":  # Валидация при изменении пароля
        check = False
        lab["text"] = "Заполните все поля!"
    elif " " in new:
        check = False
        lab["text"] = "В пароле не должно быть пробелов!"
    elif len(new) < 6:
        check = False
        lab["text"] = "Пароль должен быть длиннее 6 символов"
    elif old == new:
        check = False
        lab["text"] = "Старый и новый пароли не должны совпадать"

    if check:  # Изменение пароля
         if old_pass[0]["password"] == old:
             cursor.execute(f"update accounts set password = '{new}' where idaccount = {account_id}")  # Запрос в бд на изменение пароля
             connection.commit()
             lab["fg"] = "green"
             lab["text"] = "Успешно!"
         else:
             lab["text"] = "Неправильный старый пароль"


def back(window, global_win):  # Функция закрытия окна Toplevel
    window.destroy()
    global_win.deiconify()


if __name__ == "__main__":
    # Авторизация и подключение к базе данных
    try:
        connection = pymysql.connect(
            host=host,
            port=3306,
            user=user,
            password=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Successfully connected...")

        try:
            cursor = connection.cursor()
            print("Cursor created...")
        except Exception as ex:
            print("Failed to create cursor...")
            print(ex)
    except Exception as ex:
        print("Connection failed...")
        print(ex)

    # Вспомогательные переменные
    attempts_num = 5
    found_letters = []  # Найденные буквы
    not_match_letters = []  # Лищние буквы

    # Создание главного виджета root
    root = Tk()
    root.resizable(width=False, height=False)

    # Расположение окна по середине экрана
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    w = w // 2
    h = h // 2
    root.geometry(f'500x450+{w - 250}+{h - 225}')

    main_menu()  # Вызов функции отрисовки меню

    # Создание окна вторизации
    auth = Toplevel(root)
    auth.title("Авторизация")
    auth.resizable(width=False, height=False)
    auth["bg"] = "white"

    # Расположение по середине экрана
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    w = w//2
    h = h//2
    auth.geometry(f'400x200+{w-200}+{h-100}')

    # Вспомогательная переменная
    account_id = 0  # После авторизации записывается айди аккаунта для дальнейшей работы

    # Отрисовка
    auth_lab1 = Label(auth, text="Войдите или зарегистрируйтесь", bg="white", font=("Montserrat", 12))
    auth_lab1.grid(row=0, column=0, columnspan=4)

    auth_lab2 = Label(auth, text="Логин", bg="white", font=("Montserrat", 10))
    auth_lab2.grid(row=2, column=0)
    entry_login = Entry(auth, bd=3)
    entry_login.bind('<KeyPress>', lambda event: char_limit(event, entry_login, '14'))
    entry_login.grid(row=2, column=1, columnspan=2, stick='we')

    auth_lab3 = Label(auth, text="Пароль", bg="white", font=("Montserrat", 10))
    auth_lab3.grid(row=5, column=0)
    entry_password = Entry(auth, bd=3)
    entry_password.bind('<KeyPress>', lambda event: char_limit(event, entry_password, '14'))
    entry_password.grid(row=5, column=1, columnspan=2, stick='we')

    error_label = Label(auth, text="", font=("Montserrat", 12), bg="white", wraplength=240)
    error_label.grid(row=6,column=1, columnspan=2)
    login_btn = Button(auth, text="Вход", font=("Montserrat", 12), bg="blue", fg="yellow", command=login)
    login_btn.grid(row=7, column=1, stick='w')
    register_btn = Button(auth, text="Регистрация", font=("Montserrat", 12), bg="blue", fg="yellow", command=registration)
    register_btn.grid(row=7, column=2)

    # Конфигурация виждета
    for i in range(4):
        auth.grid_columnconfigure(i, minsize=100)
    for i in range(1, 3):
        auth.rowconfigure(i, minsize=20)

    # Скрытие окна root при авторицазии
    root.withdraw()
    root.mainloop()
