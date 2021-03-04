import socket
import select
import hamming_code as HC

#Сервер принимает сообщение и обратно отправляет сообщение об результатах

def printStat(stat_err):
    oneError = 0
    twoError = 0
    noError = 0
    for idx, err in enumerate(stat_err):
        if err >= 0:
            oneError +=1
            print(f'There is a single mistake in word number {idx} at position {err}')
        elif err == -1:
            noError +=1
            print(f'There is no mistake in word number {idx}')
        elif err == -2:
            twoError +=1
            print(f'There is a double mistake in word number {idx} ')
    #6) Выводим общий результат
    total_word = oneError+noError+twoError
    print(f'Common statistic: \nTotal word count : {total_word} \nWithout errors: {noError}/{total_word} \nOne error: {oneError}/{total_word} \nTwo erros: {twoError}/{total_word}')


#Тут будем декодировать коды и возвращать будем последовательность бит со статистикой. Будем считать, что сервер знает длину слова 51
def process(response):
    #Разбиваем на слова
    words = [response[i*51:i*51+51].decode('cp1251') for i in range(int(len(response)/51))]
    #Декодируем и собираем статистику по ошибкам
    stat_err = []
    str_res, stat_err = HC.getSeqOfBitsAndDecode(words, stat_err)
    printStat(stat_err)
    #Кодируем статистику в код Хемминга
    print(str_res)
    #Делаем последовательность из чисел со статистикой
    statistic_str = ''
    sep = ';'
    for i in stat_err:
        statistic_str = statistic_str + str(i) + sep
    
    bins = HC.encode_str_to_bin_seq(statistic_str)
    #Кодируем последовательность в слова hamming'a
    words, temp = HC.create_words_hamming(bins, 0) #передаем без ошибок уже
    message = ''
    for word in words:
        message = message + word
    message = message.encode('cp1251')
    return message


def main():
    sock = socket.socket()
    sock.bind(('', 9090))
    sock.listen(1)
    count = 0
    while True: #будет слушать постоянно
        conn, addr = sock.accept()
        count += 1
        print('connected:', addr)
        response = b''
        #ready = select.select([sock], [], [], 1)
        while True:
            conn.settimeout(2.0) #ждем 5 секунд, и после считаем что передача окончена
            try:
                data = conn.recv(1024)
            except:
                break #выходим из цикла
            response = response + data
                
        #Работаем с входным сообщением
        req = process(response)   
        #Отправляем статистику клиенту
        conn.send(req)
        #Закрываем соеденение
        conn.close()
        if count == 5: #ограничим количество передач до 5. После сервер выключится
            break 

    return 0

if __name__ == "__main__":
    main()