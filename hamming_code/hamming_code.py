import random
#кодируем по буквам
def encode_str_to_bin_seq(data):
    str = data.encode('cp1251')
    bin_seq = ''
    for letter_code in str:
        bin_letter = f'{letter_code:08b}'
        bin_seq += bin_letter
    
    return bin_seq

def create_words_hamming(bins_seq):
    #Здесь нужно полностью подготовить к передаче слова.
    #Они у нас будут длиной 44 бита информационных + 7(6 основных + 1 дополнительный) вспомогательные  = 51 слово Хемминга
    #Так как у нас 44 бита это 5.5 букв. Т.е. 5 букв передали и еще половинку. В начале следующего тогда будет остатки это буквы + еще 5 букв
    #Таким образом на четном переданном слове начало буквы в конце, а на нечетном конец буквы - в начале.
    #Если двойная ошибка на четном слове, то конец буквы нас не волнует и мы можем распознать 5 следующих букв
    #Если двойная ошибка на нечетном слове, следовательно возможно конец буквы неправильно, то предыдущую букву мы также теряем.
    #Простыми словами из-за особенности длины слова, мы теряем не 5 букв за одну двойную ошибку, а 6. В условии задачи четко сказано 44 символа,
    #так что оставляем как есть
    #Пропущенные буквы заменю на знак звездочка (*) чтобы было нагляднее где произошла потеря

    #Для последнего слова мы формируем целую последовательность. Нужное количество информационных как положено, а остальные информационные биты заполняем нулями.
    
    #1. Разбиваем на длину слова (44 бита)
    len_of_word = 44
    q = False
    hamming_words = []
    hamming_words_error = []
    for i in range(int(len(bins_seq) / len_of_word) + 1):
        word_44 = bins_seq[i*len_of_word:i*len_of_word+len_of_word]
        
        #Последние символы (конец последовательности)
        if len(word_44) == 0:
            break #если все хорошо и у нас идеально все совпало
        while len(word_44) < len_of_word:
            word_44 = word_44 + '0'
 
        hamming_word = create_code_hamming(word_44)
        hamming_words.append(hamming_word)
        pos_error = random.randint(1,51) - 1 #т.к. массивы стартуют от 0. Следовательно от 1 до 51 и -1
        print(f'Error at pos 1 {pos_error}')
        error = 1 if int(hamming_word[pos_error]) == 0 else 0
        hamming_word = hamming_word[:pos_error] + f'{error}' + hamming_word[pos_error+1:] 
        if q:
            pos_error = random.randint(1,51) - 1 #т.к. массивы стартуют от 0. Следовательно от 1 до 51 и -1
            print(f'Error at pos 2 {pos_error}')
            error = 1 if int(hamming_word[pos_error]) == 0 else 0
            hamming_word = hamming_word[:pos_error] + f'{error}' + hamming_word[pos_error+1:] 
            q = False
        
        hamming_words_error.append(hamming_word)
        res = decode_code_hamming(hamming_word)
    return hamming_words_error

def create_code_hamming(word):
    print(word)
    code_hamming = '0'
    left = 0
    #нам необходимо добавить 6 вспомогательных битов.
    for i in range(1,6):
        right = left + 2**i -1
        #print(len(word[left:right]))
        code_hamming = code_hamming + '0' + word[left:right]
        left = right
    #Высчитываем вспомогательные биты
    for i in range(6):
        r = 2**i
        xor = 0
        for k in range(r-1, len(code_hamming), 2*r): #шагаем до начало последовательности
            #print(k)
            for j in range(0, r):   #шагаем по последовательности
                #print(f'--{k+j}')

                xor = xor ^ int(code_hamming[k+j])
                if (k+j >= len(code_hamming)-1):
                    break
        #print(f'Xor at pos {r} = {xor}')
        code_hamming = code_hamming[:r-1] + f'{xor}' + code_hamming[r-1+1:]       
    #7ой просто добавим к концу
    support_xor = 0
    for bit in code_hamming:
        support_xor = support_xor ^ int(bit)
    code_hamming = code_hamming + f'{support_xor}'
    
    return code_hamming

def decode_code_hamming(code_hamming):
    left = 0
    support_bits = []
    #Высчитываем снова вспомогательные биты
    for i in range(6):
        r = 2**i
        xor = 0
        for k in range(r-1, len(code_hamming)-1, 2*r): #шагаем до начало последовательности
            for j in range(0, r):   #шагаем по последовательности
                xor = xor ^ int(code_hamming[k+j])
                if (k+j >= len(code_hamming)-1-1): #ВОЗМОЖНО ЗДЕСЬ ПРОБЛЕМА
                    break
        support_bits.append(int(xor))
    
    C = 0 #позиция где возможно произошла ошибка
    for idx, bit in enumerate(support_bits):
        if bit > 0:
            C += 2**idx
    #print(C)
    P = 0
    support_xor = 0
    isDoubleError = False
    oneError = -1 #Передаем C

    #Высчитываем вспомогательный 7ой бит
    for bit in code_hamming:
        P = P ^ int(bit)
    print(P)
    if C == 0 and P == 0:
        print('Is ok')
        #No error и все хорошо
    if C != 0 and P == 1:
        #Single error
        #Сделаем коррекцию
        pos_error = C - 1 #т.к. массивы стартуют от 0. Следовательно от 1 до 51 и -1
        correct = 1 if int(code_hamming[pos_error]) == 0 else 0
        code_hamming = code_hamming[:pos_error] + f'{correct}' + code_hamming[pos_error+1:] 
        oneError = C
        print('Single error')
    if C != 0 and P == 0:
        #Double error и все очень плохо. Потеряли 6 символов
        isDoubleError = True

        print('Double error')
    if C == 0 and P == 1:
        print('Is ok. Error at 51 bit')
        oneError = C
        #Error в 51ом саппортном бите
        #Можно не исправлять, так как все равно откидывать
    
    #Теперь осталось откинуть лишние биты, если конечно у нас не isDoubleError
    if not (isDoubleError):
        code_hamming = code_hamming[:len(code_hamming)-1] #последний бит выкидываем
        for i in reversed(range(6)):
            r = 2**i
            code_hamming = code_hamming[:r - 1] + code_hamming[r:]
        bit_seq = code_hamming
        return bit_seq, oneError
    else:
        return [], -2 # - 2 показываем, что у нас двойная ошибка и биты потеряны

    
#Мы полностью передаем слова и начинаем обрабатывать их
def getSeqOfBitsAndDecode(words, statistic):
    result_str = ''
    isPrevError = False
    halfLetter = ''
    fullLetter = ''
    #statistic = [] #-1 все хорошо, Pos - ошибка в позиции Pos #-2двойная ошибка
    #words пока листом сделано. Но если просто на прямую последовательность, то разбиваем на размер слова, т.е. на 51
    for idx, word in enumerate(words):
        #print(word)
        result, pos = decode_code_hamming(word) #word = code hamming
        statistic.append(pos)        

        #Последнее слово нужно обработать особым образом, так как возможны 000000000
        if idx == len(words) - 1:
            if len(result) > 0:
                print("TODO")
                if (idx % 2) == 0: # возможно только 1 2 3 4 и 5 символов. Половинки быть не может!
                    #ищем когда у нас подряд 8 нулей
                    for i in range(5):
                        symbol = result[i*8:i*8+8]
                        if int(symbol) == 0:
                            #значит у нас i символов есть
                            print(i)
                            last_letters = result[:i*8]
                            result_str = result_str + decode_bin_seq_to_str(last_letters)
                            break
                        if i == 4:
                            last_letters = result[:i*8+8]
                            result_str = result_str + decode_bin_seq_to_str(last_letters)
                            break

                    break
                else: #точно есть половина символа и возможны еще также от 1 до 5 символов
                    fullLetter = halfLetter + result[:4]
                    if len(fullLetter) == 8: #значит можно распознать символ иначе, на предыдущем шаге у нас была ошибка
                        result_str = result_str + decode_bin_seq_to_str(fullLetter)
                        fullLetter = '' 
                    #также ищем когда у нас подряд 8 нулей
                    for i in range(5):
                        symbol = result[i*8+4:i*8+8+4]
                        if int(symbol) == 0:
                            #значит у нас i символов есть
                            print(i)
                            last_letters = result[4:(i)*8+4]
                            result_str = result_str + decode_bin_seq_to_str(last_letters)
                            break
                        if i == 4:
                            last_letters = result[4:(i)*8+8+4]
                            result_str = result_str + decode_bin_seq_to_str(last_letters)
                            break
                    break
            else:
                #так как мы не можем точно сказать, сколько там было символов, так как данные утеряны, то ставим просто '???'
                isPrevError = True
                halfLetter = ''
                result_str = result_str + '???'
                break
                

        if len(result) > 0:
        #значит распозналось верно и ошибки уже исправлены
            if (idx % 2) == 0: #если четное, значит пол символа в конце |___8___|___8___|___8___|___8___|___8___|_4_|
                five_letters = result[:40]
                result_str = result_str + decode_bin_seq_to_str(five_letters)
                #записываем пол символа всегда
                halfLetter = result[40:] #всегда начало символа! Так что смело 
            else:               #значит пол символа в начале             |_4_|___8___|___8___|___8___|___8___|___8___|   
                fullLetter = halfLetter + result[:4]
                if len(fullLetter) == 8: #значит можно распознать символ иначе, на предыдущем шаге у нас была ошибка
                    result_str = result_str + decode_bin_seq_to_str(fullLetter)
                    fullLetter = ''
                five_letters = result[4:]
                result_str = result_str + decode_bin_seq_to_str(five_letters)
            isPrevError = False
        else: # двойная ошибка  
            isPrevError = True
            halfLetter = ''
            result_str = result_str + '??????'
    
    return result_str, statistic

def decode_bin_seq_to_str(bins_seq):
    if (len(bins_seq) % 8 != 0):
        print('Error. Not equal amount of bits')
    
    list_of_bins = [bins_seq[i*8:i*8+8] for i in range(int(len(bins_seq) / 8))]
    hex_str = b''

    for bin_letter in list_of_bins:
        letter_code = int(bin_letter, 2)    #переводим в int
        hex_code = hex(letter_code)[2:] #переводим в hex
        hex_str += bytes.fromhex(hex_code) #добавляем букву
    str = hex_str.decode('cp1251', 'replace')
    return str

def process(str):
    #1) Получаем последовательность битов
    bins = encode_str_to_bin_seq(str)
    #2) Кодируем ее в слова hamming'a
    words = create_words_hamming(bins)
    #3*)Условано передаем их. Если нужно то просто склеиваем их в последовательность битов
    print(words[0])
    #4*)Приняли и снова разбиваем на длину слова 51
    #5) Декодируем и собираем статистику по ошибкам
    stat_err = []
    str_res, stat_err = getSeqOfBitsAndDecode(words, stat_err)
    
    #str_res, stat_err = decode_bin_seq_to_str(bins, stat_err)

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
    
    print(str_res)
    print(f'Cтроки полностью совпали : {str == str_res}')
    #)7* отправляем пакет данных с ошибками в виде  bit(42;-1;-2;1;0;1;HaMmInGCooL) где HaMmInGCooL - кодовое слово

def main():
    str = 'Думаю, что теперь будет легче. Да и само клиентское приложение проще — нам нужно создать сокет, подключиться к серверу послать ему данные, принять данные и закрыть соединение. Все это делается так:#!/usr/bin/env python # -*- coding: utf-8 -*-ЮАФЫ2??13ads5%^@' 
    process(str)
    return 0

if __name__ == "__main__":
    main()