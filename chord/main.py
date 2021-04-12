import hashlib
import os
import sys
from random import choice, sample
import concurrent.futures
import time
import threading
import pydotplus
from PIL import Image

from Node import Node
from Network import Network

def time_message(start_time, message, returnTime=False):
    print(f'\n---{message} за: {(time.time() - start_time)} сек ---')
    if returnTime:
        return time.time() - start_time

def test(files, chord_net):
    # Поиск всех файлов в сети
    print(f'Поиск всех файлов в сети от узла {chord_net.first_node}')
    hops_stat = 0
    min_hops = 1000000000
    max_hops = 0
    common_time = 0
    for file in files:
        start_time = time.time()

        path = chord_net.find_file(file)
        hops = len(path) - 1
        hops_stat += hops
        print(path)
        common_time += time_message(start_time, 'поиск файла', True)
        min_hops = min(min_hops, hops)
        max_hops = max(max_hops, hops)
    with open('statistic.txt','a') as f:
        f.write(f'-------------------------------------------------------------------------------- \n')
        f.write(f'Минимальное количество hops: {min_hops} ')
        f.write(f'Максимальное количество hops: {max_hops} \n')
        f.write(f'Среднее количество hops: {round(hops_stat / len(files), 4)} \n')
        f.write(f'Количество затраченных временных ресурсов, чтобы найти все файлы (в секундах): {round(common_time,4)} \n')
    
    print('--------------------------------------------------------------------------------')
    print(f'Минимальное количество hops: {min_hops}')
    print(f'Максимальное количество hops: {max_hops}')
    print(f'Среднее количество hops: {round(hops_stat / len(files), 4)}')
    print(f'Количество затраченных временных ресурсов, чтобы найти все файлы (в секундах): {round(common_time,4)}')
    print('--------------------------------------------------------------------------------')
def show_menu(chord_net, node_ids):

    while True:
        chord_net.periodic_update()
        chord_net.update_network_fingers()
        print('================================================')
        print('1.Вставить узел в сеть')
        print('2.Найти файл в сети')
        print('3.Вставить файл в сеть')
        print('4.Распечатать граф сети')
        print('5.Вывести информацию о сети')
        print('6.Удалить узел из сети')
        print('7.Выход')
        print('================================================')

        choice = input('Выберите операцию: ')

        print('\n')

        if(choice == '1'):
            # вставка одного узлаinsert a single node to network
            node_id = int(input('>>> Введите id узла: '))
            if node_id not in node_ids:
                start_time = time.time()

                chord_net.insert_node(node_id)
                node_ids.append(node_id)

                time_message(start_time, 'узел добавлен')
            else:
                print('Такой узел уже существует в сети.')

        elif (choice == '2'):
            # поиск файла по сети
            query = input('>>> Введите имя файла, который хотите найти: ')
            start_time = time.time()

            path = chord_net.find_file(query)
            print(f'Путь до файла - {path}')
            time_message(start_time, 'Поиск файла')

        elif (choice == '3'):
            # Вставка файла
            query = input('Введите имя файла: ')
            start_time = time.time()

            chord_net.insert_data(query)

            time_message(start_time, 'файл добавлен')

        elif (choice == '4'):
            # Печать графа
            if(len(chord_net.nodes) > 0):
                chord_net.print_network()

        elif (choice == '5'):
            # Вывод основной инфомрации
            print(chord_net)

        elif (choice == '6'):
            node_id = int(input('Введите id узла, который хотите удалить: '))

            node_ids.remove(node_id)

            start_time = time.time()

            chord_net.delete_node(node_id)

            time_message(start_time, 'удаление узла')

        elif (choice == '7'):
            sys.exit(0)

        print('\n')


def create_network():
    sys.setrecursionlimit(10000000)

    m_par = int(input('Параметр сети m: '))
    Node.m = m_par
    Node.ring_size = 2 ** m_par

    print(f'Создание сети с предельной вместимостью в {Node.ring_size} узлов.')
    num_nodes = int(input('Количество узлов: '))

    while(num_nodes > 2**m_par):
        print('Ошибка! Количество узлов должно быть не больше предельной вместимости')
        num_nodes = int(input('Количество узлов : '))

    num_data = int(input('Количество искуственных данных, которые необходимо вставить: '))

    print('--------------------------------------------')

    node_ids = sample(range(Node.ring_size), num_nodes)

    chord_net = Network(m_par, node_ids)

    start_time = time.time()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        created_nodes = executor.map(
            chord_net.create_node, node_ids, chunksize=100)
        for node in created_nodes:
            chord_net.nodes.append(node)

    # Немного ускорим, разделив добавления узлов в два потока, которые независимы друг от друга
    half = len(chord_net.nodes)//2

    t1 = threading.Thread(target=chord_net.insert_nodes,
                          args=(chord_net.nodes[:half],))
    t2 = threading.Thread(target=chord_net.insert_nodes,
                          args=(chord_net.nodes[half:],))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    # Обновляем карту пальцев каждого узла
    chord_net.update_network_fingers()

    time_message(start_time, 'Создание сети')

    # Генерируем и добавляем данные в узлы
    if(num_data > 0):
        artificial_files = chord_net.generate_artificial_data(num_data)

    #Тестируем
    test(artificial_files,chord_net)

    #Небольшая менюшка, чтобы можно было потестить
    show_menu(chord_net, node_ids)


if __name__ == '__main__':
    create_network()
