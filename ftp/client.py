from ftplib import FTP
import os
import random
def authorization(ftp):
    while True:
        host = str(input('> Сервер (Нажмите Enter, eсли хотите зайти на файловый сервер по умолчанию 127.0.0.2): '))
        if host == '':
            host ='127.0.0.2'
        try: 
            ftp.connect(host)
        except ConnectionRefusedError as err:
            print('Нет возможности подключиться к серверу. Проверьте правильность данных')
        ftp_user = str(input('> Пользователь (Нажмите Enter, eсли хотите зайти как anonymous): '))
        if ftp_user != '':
            ftp_password = str(input('Пароль:'))
            try:
                ftp.login(ftp_user, ftp_password)
                break
            except Exception as err:
                code_err = int(str(err.args[0]).split(' ')[0])
                if code_err == 530:
                    print('Неверно указан логин или пароль')
                else:
                    print(err.args[0])
        else:
            #Авторизация как аноним
            ftp.login()
            break
        
    
    while True:
        mode = str(input('> Выберете мод (активный - 1 или пассивный - 2) или нажмите Enter: '))
        if mode == '1':
            #Active
            try:
                p1 = random.randint(1,256)
                p2 = random.randint(1,256)
                param = '127,0,0,1,' + str(p1)+',' +str(p2)
                port = int(param.split(',')[-1]) + int(param.split(',')[-2]) * 256
                resp = ftp.sendcmd('PORT ' + param)
                print(f'Установлен активный режим на порту сервера {port}')
            except Exception as err:
                #print(err)
                print(f'Установлен активный режим на порту {port}')
            break
        elif mode == '2' or mode == '':
            #Passive
            try:
                resp = ftp.sendcmd('PASV')
                port = int(resp.split(',')[-1][:-1]) + int(resp.split(',')[-2]) * 256
                print(f'Установлен пассивный режим на порту сервера {port}')
            except Exception as err:
                print(err)
            break
        else:
            print('Неправильный код')
    if ftp_user == '':
        ftp_user = 'anonymous'
    return ftp, ftp_user

def processHELP():
    helpList = '\
    CWD — Сменить директорию \n\
    DELE — Удалить файл (DELE filename)\n\
    HELP — Выводит список команд, принимаемых сервером \n\
    LIST — Возвращает список файлов директории. Список передаётся через соединение данных \n\
    MKD — Создать директорию\n\
    NLST — Возвращает список файлов директории в более кратком формате, чем LIST. Список передаётся через соединение данных \n\
    PWD — Возвращает текущую директорию \n\
    QUIT — Отключиться \n\
    RETR — Скачать файл или файлы. После команды RETR через пробел укажите какие файлы необходимо скачать, а в конце - где сохранить на сервере\n\
    RMD — Удалить директорию \n\
    STOR — Загрузить файл или файлы. После команды STOR через пробел укажите какие файлы необходимо загрузить, а в конце - где сохранить на диске'
    print(helpList)

def processLIST(ftp):
    try:
        lines = []
        response = ftp.retrlines('LIST', lines.append) 
        if int(response.split(' ')[0]) == 226:
            if len(lines) == 0:
                print('Нет файлов и папок в этой директории')
            else:
                for line in lines:
                    print(line)
    except Exception as err:
        code_err = int(str(response[1].args[0]).split(' ')[0])
        print(response[1].args[0])

def processCWD(ftp, args):
    if len(args) == 0:
        print('Укажите директорию')
        return 0
    elif len(args) > 1:
        print('Укажите только одну директорию')
        return 0
    try:
        response = ftp.cwd(args[0])
        code = int(str(response).split(' ')[0])
        if code == 250:
            dir = response.split(' ')[3]
            print(f'Переход прошел успешно. Вы в директории {dir}')
    except Exception as err:
        code_err = int(str(err.args[0]).split(' ')[0])
        if code_err == 550:
            dir = err.args[0].split(' ')[3]
            print(f'Ошибка CWD! Директория {dir} не найдена')
        else:
            print(err.args[0])
        
def processMKD(ftp, args):
    if len(args) == 0:
        print('Укажите имя директории, которую необходимо создать')
        return 0
    elif len(args) > 1:
        print('Укажите только одно имя директории')
        return 0
    try:
        response = ftp.mkd(args[0])
        if response != "":
            print(f'Директория {response} была успешно создана.')
    except Exception as err:
        code_err = int(str(err.args[0]).split(' ')[0])
        if code_err == 550:
            if err.args[0].find('Permission denied') > 0:
                print(f'Вам запрещено здесь создавать директорию')
            elif err.args[0].find('already exists') > 0:
                dir = err.args[0].split(' ')[3]
                print(f'Директория уже создана')
            else:
                print(err.args[0])
        else:
            print(err.args[0])

def processRMD(ftp, args):
    if len(args) == 0:
        print('Укажите имя директории, которую необходимо удалить')
        return 0
    elif len(args) > 1:
        print('Укажите только одно имя директории')
        return 0
    try:
        response = ftp.rmd(args[0])
        if response != "":
            print(f'Директория была успешно удалена.')
    except Exception as err:
        code_err = int(str(err.args[0]).split(' ')[0])
        if code_err == 550:
            if err.args[0].find('Permission denied') > 0:
                print(f'Вам запрещено удалять эту директорию')
            elif err.args[0].find('not found') > 0:
                dir = err.args[0].split(' ')[3]
                print(f'Директория не была найдена')
            elif err.args[0].find('not empty') > 0:
                dir = err.args[0].split(' ')[3]
                print(f'Директория имеет файлы или вложенные папки. Нельзя удалять не пустые папки')
            else:
                print(err.args[0])
        else:
            print(err.args[0])

def processPWD(ftp):
    try:
        response = ftp.pwd()
        print(f"Текущая директория: '{response}'")
    except Exception as err:
        print(err)

def processNLST(ftp):
    try:
        lines = []
        response = ftp.nlst()
        lines= response
        if len(lines) == 0:
            print('Нет файлов и папок в этой директории')
        else:
            for line in lines:
                print(line)
    except Exception as err:
        print(code_err)

def processDELE(ftp, args):
    if len(args) < 1:
        print('Необходимо передать как минимум одинпараметра через пробел и указав путь до папки куда записывать')
        return 0
    #TODO('Сделать массовую обработку')
    files = args

    for file in files:
        try:
            ftp.delete(file)
            print(f"Файл {file} успешно удален со сервера.")
        except Exception as err:
            code_err = int(str(err.args[0]).split(' ')[0])
            if code_err == 550:
                if err.args[0].find('Permission denied') > 0:
                    print(f'Вам запрещено скачивать этот файл')
                elif err.args[0].find('not found') > 0:
                    print(f'Файл {file} не был найден')
                elif err.args[0].find('Permission denied') >= 0:
                    print(f'Вам запрещено загружать этот файл в эту директорию')
                else:
                    print(err)
            elif code_err == 22:
                print('Неправильно задан путь до файла!')
            elif code_err == 13:
                if err.args[1].find('Permission denied') >= 0:
                    print(f'Вам запрещено скачивать этот файл')

def processQUIT(ftp):
    try:
        response = ftp.quit().split(' ')[1]
        print(f'Ответ сервера на выход: {response}')
    except Exception as err:
        print(err)

def processRETR(ftp, args):
    #args[0-last] что передаем, args[last] и в какую папку передаем
    if len(args) < 2:
        print('Необходимо передать как минимум два параметра через пробел и указав путь до папки куда записывать')
        return 0
    #TODO('Сделать массовую обработку')
    files = args[:-1]
    out_base = args[-1]
    if out_base[-1] != '/' and out_base[-1] != '\\':
        out_base = out_base + '/'

    for file in files:
        out = out_base + file.split('/')[-1]
        try:
            with open(out, 'wb') as f:
                ftp.retrbinary('RETR ' + file, f.write)
            print(f"Файл {file.split('/')[-1]} успешно скачен со сервера. Находится {os.path.realpath(out)}.")
        except Exception as err:
            code_err = int(str(err.args[0]).split(' ')[0])
            if code_err == 550:
                if err.args[0].find('Permission denied') > 0:
                    print(f'Вам запрещено скачивать этот файл')
                elif err.args[0].find('not found') > 0:
                    print(f'Файл {file} не был найден')
                elif err.args[0].find('Permission denied') >= 0:
                    print(f'Вам запрещено загружать этот файл в эту директорию')
                else:
                    print(err)
            elif code_err == 22:
                print('Неправильно задан путь до файла!')
            elif code_err == 13:
                if err.args[1].find('Permission denied') >= 0:
                    print(f'Вам запрещено скачивать этот файл')

def processSTOR(ftp, args):
    #args[0-last] что передаем, args[last] и в какую папку передаем
    if len(args) < 2:
        print('Необходимо передать как минимум два параметра через пробел и указав путь до папки куда записывать')
        return 0
    files = args[:-1]
    path_base = args[-1]
    if path_base[-1] != '/' and path_base[-1] != '\\':
        path_base = path_base + '/'

    for file in files:
        path = path_base + os.path.normpath(file).split('\\')[-1] #путь на сервере
        ftype = file.split('.')[-1].upper()

        if not os.path.isfile(file):
            print(f'Файла {file} не существует')
            continue

        try:
            if ftype == 'TXT':
                with open(file, 'rb') as fobj:
                    ftp.storlines('STOR ' + path, fobj)
            else:
                with open(file, 'rb') as fobj:
                    ftp.storbinary('STOR ' + path, fobj, 1024)
            print(f"Файл {file.split('/')[-1]} успешно загружен на сервер. Находится {path}.")
        except Exception as err:
            code_err = int(str(err.args[0]).split(' ')[0])
            if code_err == 550:
                if err.args[0].find('Permission denied') > 0:
                    print(f'Вам запрещено загружать этот файл в эту директорию')
                elif err.args[0].find('Filename invalid') > 0:
                    print(f'Неправильно указан путь на сервере {path}. Убедитесь, что папка {path_base} существует')
                else:
                    print(err)
            else:
                print(err)
            
def commandProcessing(command_, ftp):
    #Парсим команду
    command_splited = command_.split(' ')
    command, args   = command_splited[0].upper(), command_splited[1:]
    #Выбираем команду
    if command == 'HELP':
        processHELP()
    elif command == 'LIST':
        processLIST(ftp)
    elif command == 'NLST':
        processNLST(ftp)
    elif command == 'CWD':
        processCWD(ftp, args)
    elif command == 'MKD':
        processMKD(ftp, args)
    elif command == 'RMD':
        processRMD(ftp, args)
    elif command == 'PWD':
        processPWD(ftp)
    elif command == 'RETR':
        processRETR(ftp, args)
    elif command == 'STOR':
        processSTOR(ftp, args)
    elif command == 'DELE':
        processDELE(ftp, args)
    elif command == 'QUIT':
        processQUIT(ftp)
        return -1
    else:
        print(f"Нет команды '{command_splited[0]}'")
    return 0
    
#инициализируем ftp
ftp = FTP()

#авторизуемся
ftp, login = authorization(ftp)
print('------------------------------------')
print(f'Ваш адрес : {ftp.sock.getsockname()}')
print(f'Вы зашли под пользователем {login}')
ftp.cwd('./')

print('------------------------------------')
print('Приветствие от сервера:')
print(ftp.welcome)
print(f'Based at {ftp.host}')
print('------------------------------------')

while True:
    #Цикл с обработками команд
    command = str(input('Команда: '))
    code = commandProcessing(command, ftp)
    if code < 0:
        break
    print('------------------------------------')

print('Конец сессии')

