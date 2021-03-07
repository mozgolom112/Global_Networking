import socket
import hamming_code as HC

import codecs

#Клиент отправляет сообщение

def printStat(stat_err):
    oneError = 0
    twoError = 0
    noError = 0
    for idx, err in enumerate(stat_err):
        if err >= 0:
            oneError +=1
            #print(f'There is a single mistake in word number {idx} at position {err}')
        elif err == -1:
            noError +=1
            #print(f'There is no mistake in word number {idx}')
        elif err == -2:
            twoError +=1
            #print(f'There is a double mistake in word number {idx} ')
    #6) Выводим общий результат
    total_word = oneError+noError+twoError
    print(f'Common statistic: \nTotal hamming words count : {total_word} \nWithout errors: {noError}/{total_word} \nOne error: {oneError}/{total_word} \nTwo erros: {twoError}/{total_word}')
    with open('./client_result.txt', 'a') as wf:
        wf.write(f'Common statistic: \nTotal word count : {total_word} \nWithout errors: {noError}/{total_word} \nOne error: {oneError}/{total_word} \nTwo erros: {twoError}/{total_word}')

def process(str, sock, flag):
    #1) Получаем последовательность битов
    bins = HC.encode_str_to_bin_seq(str)
    #2) Кодируем ее в слова hamming'a
    words, check_err_list  = HC.create_words_hamming(bins, flag)
    #3) Делаем сообщение которое будем отправлять на сервер
    message = ''
    for word in words:
        message = message + word
    message = message.encode('cp1251')
    #3) Передаем сообщение на сервер. Будем считать, что сервер уже знает, что длина слова 51
    sock.send(message)
    #4) Получаем сообщение от сервера со статистикой также в виде кода Хемминга, так что нам также необходимо его расшифровать
    response = sock.recv(1024)
    while True:
        data = sock.recv(1024)
        if not data:
            break
        response = response + data
    #Закрываем соеденение, так как длина очереди равна 1
    sock.close()
    #5) Расшифровываем
    #Разбиваем на слова
    words_resp = [response[i*51:i*51+51].decode('cp1251') for i in range(int(len(response)/51))]
    #Декодируем и собираем статистику по ошибкам
    stat_err = []
    str_res, stat_err = HC.getSeqOfBitsAndDecode(words_resp, stat_err)
    stat_from_server_str = str_res.split(';')
    stat_from_server = []
    for stat in stat_from_server_str:
        if stat != '':
            stat_from_server.append(int(stat))
    #Провереяем нашу статистику ошибок с нашей
    with open('./client_result.txt', 'w') as wf:
        for idx, value in enumerate(check_err_list):
            if value != stat_from_server[idx]:
                #Произошло неудачное определение
                print(f'Attention!!! The word number {idx} is not true. True value = {value}. From server = {stat_from_server[idx]}')
                wf.write(f'Attention!!! The word number {idx} is not true. True value = {value}. From server = {stat_from_server[idx]}')

    with open('./client_result.txt', 'a') as wf:
        print('stat_from_server')
        wf.write('\nstat_from_server\n')
    printStat(stat_from_server)
    with open('./client_result.txt', 'a') as wf:
        print('true_stat')
        wf.write('\ntrue_stat\n')
    printStat(check_err_list)


    

def main():

    #Делаем connect
    sock = socket.socket()
    path_to_file = r'E:\glob_net\hamming_code\release\test.txt' # input("Input full path to file with text.Important! Text should be in cp1251 or : ")  #r'E:\glob_net\hamming_code\release\test.txt' 
    flag = 0#int(input("Input flag of erros. 0 - no errors, 1 - only one error, 2 - only two error, 3 - mix both of them: "))
    #flag=0 без ошибок flag=1 только с одиночными ошибками flag=2 только со множественными flag=3 в разброс
    with open(path_to_file, 'r') as read_file:
        str = read_file.read()

    print(f'Amount symbols: {len(str)}')
    w = str.split(' ')
    print(f'Amount (precisely) of words which divede by Space(between two words): {len(w)}')
    sock.connect(('localhost', 9090))

    process(str, sock, flag)

    return 0

if __name__ == "__main__":
    main()