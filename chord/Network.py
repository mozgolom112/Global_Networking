import hashlib

import os
import sys

import time
import threading
import pydotplus

import concurrent.futures

from PIL import Image
from Node import Node
from random import choice, sample

class NetworkError(Exception):
    def __init__(self, msg='Ошибка!', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class Network:
    def __init__(self, m, node_ids):
        self.nodes = []
        self.m = m
        self.ring_size = 2 ** m
        self.insert_first_node(node_ids[0])
        self.first_node = self.nodes[0]
        node_ids.pop(0)

    def __str__(self):
        return f'Chord net:\n Существующие узлы: {len(self.nodes)} узлов. \n Максимальная вместимость: {self.ring_size} узлов. \n Параметр сети m: {self.m} \n Первый созданный узел: {self.first_node.node_id} \n '

    def print_network(self):
        for node in self.nodes:
            node.print_fingers_table()
            print(node.data)

    def update_network_fingers(self):
        self.first_node.update_fingers()

        curr = self.first_node.fingers_table[0]

        while curr != self.first_node:
            curr.update_fingers()
            curr = curr.fingers_table[0]

    def hash_function(self, key):

        num_bits = Node.m

        #переводим в hex и hashed bytes
        bt = hashlib.sha1(str.encode(key)).digest()

        # число нужного количество байт для id 
        req_bytes = (num_bits + 7) // 8

        # Получаем ключ в виде int
        hashed_id = int.from_bytes(bt[:req_bytes], 'big')
        if num_bits % 8:
            hashed_id >>= 8 - num_bits % 8

        return hashed_id, int.from_bytes(bt, 'big') #по первому хешу кладем в нужное место, по второму записываем

    def create_node(self, node_id):
        node = Node(node_id, self.m)
        return node

    def insert_nodes(self, nodes):
        for node in nodes:
            try:
                if(node.node_id > self.ring_size):
                    raise NetworkError(
                        '>>> ID узла должен быть меньше или равен размеру сети')
                # add new node to the network
                print(
                    f'>>> Узел {node.node_id} добавлен')

                node.join(self.first_node)
            except NetworkError as e:
                print(e)

    def insert_node(self, node_id):

        try:
            if(node_id > self.ring_size):
                raise NetworkError(
                    '>>> ID узла должен быть меньше или равен размеру сети.')

            self.nodes.append(self.create_node(node_id))

            node = self.nodes[-1]

            # Добавляем узел
            print(
                f'>>> Узел {node.node_id} добавлен к сети.')

            node.join(self.first_node)

        except NetworkError as e:
            print(e)

    def delete_node(self, node_id):

        try:
            node = list(filter(lambda temp_node: temp_node.node_id ==
                               node_id, self.nodes))[0]
        except:
            print(f'>>> Узел {node_id} не был найден!')
        else:
            node.leave()
            self.nodes.remove(node)
            self.update_network_fingers()

    def insert_first_node(self, node_id):
        print(f'>>>Создание сети. Вставка первого узла {node_id}\n')
        # create new node object
        node = Node(node_id, self.m)
        # add node to nodes of network
        self.nodes.append(node)

    def find_file(self, file):

        short_hashed_key, full_hashed_key = self.hash_function(file)

        print(f'>>> Поиск  \'{file}\' по короткому ключу {short_hashed_key}')
        node = self.first_node

        node, path = node.find_successor(short_hashed_key, [])

        fst_lvl_data = node.data.get(short_hashed_key, None)

        if fst_lvl_data != None:
            
            snd_lvl_data = fst_lvl_data.get(full_hashed_key, None)
            
            if snd_lvl_data != None:
                if type(snd_lvl_data) == type(dict()):
                    print('Множественное совпадение имен. Необходимо проверять содержание файла')
                print(
                    f'>>> Найден файл \'{file}\' в узле {node.node_id} по короткому ключу {short_hashed_key} и длинному {full_hashed_key}')
            else:
                print(f'>>> \'{file}\' нет в данной сети')
        else:
            print(f'>>> \'{file}\' нет в данной сети')
        
        return path

    def insert_data(self, key):
        node = self.first_node

        short_hashed_key, full_hashed_key = self.hash_function(key)
        print(
            f'Сохраняем ключ:{key} с Hash:{short_hashed_key} -> Узел:{node.find_successor(short_hashed_key)[0].node_id}')

        succ, _ = node.find_successor(short_hashed_key)

        current_short_dict = succ.data.get(short_hashed_key, None)

        if current_short_dict == None:
            succ.data.update({short_hashed_key: {}})

        current_full_dict = succ.data[short_hashed_key].get(full_hashed_key, None)

        if current_full_dict == None:
            #Все в порядке, и у нас не сохраняют один и тот же файл. Сохраняем по длинному ключу уже
            succ.data[short_hashed_key].update({full_hashed_key: key})
        else:
            #Идет сохранение того же самого файла. Необходимо хешировать по содержанию файла.
            print("Множественное совпадение имен. Необходимо проверять содержание файла")

        #succ.data[short_hashed_key].update(full_hashed_key: key)
        return succ.node_id



    def generate_artificial_data(self, num):

        extensions = ['.txt', '.png', '.doc', '.mov', '.jpg', '.py']
        files = [f'file_{i}'+choice(extensions) for i in range(num)]
        count = [0 for i in range(2 ** self.m)]
        start_time = time.time()
        for temp in files:
            id = self.insert_data(temp)
            count[id] +=  1

        min_files = 10000000000000000
        max_files = 0
        averange_files = 0

        for node in self.nodes:
            c = count[node.node_id]
            min_files = min(min_files, c)
            max_files = max(max_files, c)
            averange_files += c

        with open('statistic.txt','a') as f:
            f.write(f'Всего файлов было сгенерированно: {len(files)} \n')
            f.write(f'Минимальное количество файлов в узле: {min_files} \n')
            f.write(f'Максимальное количество файлов в узле: {max_files} \n')
            f.write(f'Среднее количество файлов в узле: {round(averange_files/len(self.nodes), 4)} \n')
            f.write(f'Количество затраченных временных ресурсов, чтобы разнести все файлы в правильные узлы (в секундах): {round(float(time.time() - start_time)/num, 4)} \n')
        print('--------------------------------------------------------------------------------')
        print(f'Минимальное количество файлов в узле: {min_files}')
        print(f'Максимальное количество файлов в узле: {max_files}')
        print(f'Среднее количество файлов в узле: {averange_files/len(self.nodes)}')
        print(f'Количество затраченных временных ресурсов, чтобы разнести все файлы в правильные узлы (в секундах): {round(float(time.time() - start_time)/num, 4)}')
        print('--------------------------------------------------------------------------------')
        return files
    #печатаем с помощью программы Graphviz
    def print_network(self):
        f = open('graph.dot', 'w+')
        f.write('digraph G {\r\n')
        for node in self.nodes:
            data = 'Keys:\n-------------\n'
            f.write(f'{node.node_id} -> {node.successor.node_id}\r\n')
            for key in sorted(node.data.keys()):
                data += f'key: {key} - data: \''
                for file in node.data[key].values():
                    data += file + ', '
                data += f"\'\n"

            fingers = 'Finger Table:\n-------------\n'
            for i in range(self.m):

                fingers += f'{(node.node_id + 2 ** i) % self.ring_size} : {node.fingers_table[i].node_id}\n'

            if data != '' and data != 'Keys:\n-------------\n':
                f.write(
                    f'data_{node.node_id} [label=\"{data}\", shape=box]\r\n')
                f.write(f'{node.node_id}->data_{node.node_id}\r\n')

            if fingers != '':
                f.write(
                    f'fingers_{node.node_id} [label=\"{fingers}\", shape=box]\r\n')
                f.write(f'{node.node_id}->fingers_{node.node_id}\r\n')

        f.write('}')
        f.close()

        try:
            graph_a = pydotplus.graph_from_dot_file('graph.dot')
            graph_a.write_png('graph.png', prog='circo')
            graph_image = Image.open('graph.png')
            graph_image.show()
        except pydotplus.graphviz.InvocationException:
            pass

    def periodic_update(self):
        threading.Timer(15, self.update_network_fingers).start()

