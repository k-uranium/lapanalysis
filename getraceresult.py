import requests
from bs4 import BeautifulSoup
import os
import re
import sys
from utils import getLink, getRowElement, getSpan, getTable, getTableRow, getTitle


def getFather(link):
    site = requests.get(link)
    site.encoding = site.apparent_encoding
    horse_data = BeautifulSoup(site.text, 'html.parser')
    father = getTitle(horse_data.find(class_='blood_table'))[1]
    return father


# リストの父名の位置を返す
def findFather(father_dictionary_list, father):
    left = 0
    right = len(father_dictionary_list)
    while(left < right):
        middle = int((left + right) / 2)
        if father_dictionary_list[middle]['father'] < father:
            left = middle + 1
        elif father_dictionary_list[middle]['father'] > father:
            right = middle
        else:
            return middle
    # 見つからなかった場合リストに新たに追加
    data_dictionary = {'father': father, '1': 0, '2': 0, '3': 0, 'otherwise': 0}
    father_dictionary_list.insert(left, data_dictionary)
    return left


# リストのraceIdの位置を返す
def findRaceId(raceId_list, raceId):
    left = 0
    right = len(raceId_list)
    while(left < right):
        middle = int((left + right) / 2)
        if raceId_list[middle] < raceId:
            left = middle + 1
        elif raceId_list[middle] > raceId:
            right = middle
        else:
            return -1
    # 見つからなかった場合リストに新たに追加
    raceId_list.insert(left, raceId)
    return left


def getLevel(smalltxt):
    text = str(smalltxt)
    if '新馬' in text:
        return 0
    elif '未勝利' in text:
        return 1
    elif '1勝クラス' in text or '500万下' in text:
        return 2
    elif '2勝クラス' in text or '1000万下' in text:
        return 3
    elif '3勝クラス' in text or '1600万下' in text:
        return 4
    else:
        return 5


def getResult(raceId, track):
    link = 'https://db.netkeiba.com/race/' + raceId
    site = requests.get(link)
    site.encoding = site.apparent_encoding
    race_data = BeautifulSoup(site.text, 'html.parser')
    table_str = getTable(race_data.find(class_='race_table_01 nk_tb_common'))[1]
    if table_str == 'Non':
        return False
    level_list = ['新馬', '未勝利', '1勝クラス', '2勝クラス', '3勝クラス', 'オープン']
    race_level = getLevel(race_data.find(class_='smalltxt'))
    race_detail = getSpan(race_data.find(class_='racedata fc'))[1]
    mPosition = race_detail.find('m')
    course = race_detail[0]
    if course == '障':
        return True
    distance = race_detail[mPosition - 4:mPosition]
    condition = race_detail.split('/')[2].split(' : ')[1][:-1]
    directoryName = './競馬場データ/' + track + '/' + distance + course
    os.makedirs(directoryName, exist_ok=True)
    directoryPath = os.path.join(directoryName, condition)
    os.makedirs(directoryPath, exist_ok=True)
    frameDataFilePath = os.path.join(directoryPath, '枠別成績.txt')
    fatherDataFilePath = os.path.join(directoryPath, '種牡馬別成績.txt')
    timeDataFilePath = os.path.join(directoryPath, '平均タイム.txt')
    frame_dictionary_list = []
    father_dictionary_list = []
    time_dictionary_list = []
    if os.path.exists(frameDataFilePath):
        with open(frameDataFilePath, 'r', encoding='utf-8') as f:
            data_list = f.read().splitlines()
            for datas in data_list:
                data = datas.split(' ')
                data_dictionary = {'frame': int(data[0]), '1': int(data[1]), '2': int(data[2]), '3': int(data[3]), 'otherwise': int(data[4])}
                frame_dictionary_list.append(data_dictionary)
    else:
        for num in range(8):
            data_dictionary = {'frame': num + 1, '1': 0, '2': 0, '3': 0, 'otherwise': 0}
            frame_dictionary_list.append(data_dictionary)
    if os.path.exists(fatherDataFilePath):
        with open(fatherDataFilePath, 'r', encoding='utf-8') as f:
            data_list = f.read().splitlines()
            for datas in data_list:
                data = datas.split('  ')
                data_dictionary = {'father': data[0], '1': int(data[1]), '2': int(data[2]), '3': int(data[3]), 'otherwise': int(data[4])}
                father_dictionary_list.append(data_dictionary)
    if os.path.exists(timeDataFilePath):
        with open(timeDataFilePath, 'r', encoding='utf-8') as f:
            data_list = f.read().splitlines()
            for datas in data_list:
                data = datas.split(' ')
                data_dictionary = {'level': data[0], 'count': int(data[1]), 'avetime': float(data[2])}
                time_dictionary_list.append(data_dictionary)
    else:
        for level in level_list:
            data_dictionary = {'level': level, 'count': 0, 'avetime': 0.0}
            time_dictionary_list.append(data_dictionary)
    start_index = 0
    while(True):
        table_row = getTableRow(table_str, start_index)
        start_index = table_row[2]
        if not table_row[0]:
            break
        start_index_element = table_row[1].find('>')
        count = 0
        while(True):
            row_element = getRowElement(table_row[1], start_index_element)
            start_index_element = row_element[2]
            if not row_element[0]:
                break
            if count == 0:
                rank = row_element[1]
                if not rank.isdecimal():
                    break
            if count == 1:
                frame = int(getSpan(row_element[1])[1])
                if int(rank) <= 3:
                    frame_dictionary_list[frame - 1][rank] += 1
                else:
                    frame_dictionary_list[frame - 1]['otherwise'] += 1
            if count == 3:
                father = getFather('https://db.netkeiba.com' + getLink(row_element[1])[1])
                father_num = findFather(father_dictionary_list, father)
                if int(rank) <= 3:
                    father_dictionary_list[father_num][rank] += 1
                else:
                    father_dictionary_list[father_num]['otherwise'] += 1
                if rank != '1':
                    break
            if count == 7:
                time_split = re.split('[:.]', row_element[1])
                time = int(time_split[0]) * 60 + int(time_split[1]) + int(time_split[2]) * 0.1
                sum_time = time_dictionary_list[race_level]['count'] * time_dictionary_list[race_level]['avetime'] + time
                time_dictionary_list[race_level]['count'] += 1
                time_dictionary_list[race_level]['avetime'] = sum_time / time_dictionary_list[race_level]['count']
                with open(timeDataFilePath, 'w', encoding='utf-8') as f:
                    for time_dictionary in time_dictionary_list:
                        f.write(time_dictionary['level'] + ' ' + str(time_dictionary['count']) + ' ' + str(time_dictionary['avetime']) + '\n')
                    break
            count += 1
    with open(frameDataFilePath, 'w', encoding='utf-8') as f:
        for frame_dictionary in frame_dictionary_list:
            f.write(str(frame_dictionary['frame']) + ' ' + str(frame_dictionary['1']) + ' ' + str(frame_dictionary['2']) + ' ' + str(frame_dictionary['3']) + ' ' + str(frame_dictionary['otherwise']) + '\n')
    with open(fatherDataFilePath, 'w', encoding='utf-8') as f:
        for father_dictionary in father_dictionary_list:
            f.write(father_dictionary['father'] + '  ' + str(father_dictionary['1']) + '  ' + str(father_dictionary['2']) + '  ' + str(father_dictionary['3']) + '  ' + str(father_dictionary['otherwise']) + '\n')
    return True


def getStart(raceId_norace, track):
    for race in range(12):
        with open('./analysisedraceid.txt', 'r', encoding='utf-8') as f:
            raceId_list = f.read().splitlines()
        raceId = raceId_norace + str(race + 1).zfill(2)
        if findRaceId(raceId_list, raceId) == -1:
            continue
        print(raceId, track)
        result = getResult(raceId, track)
        if not result:
            return race
        with open('./analysisedraceid.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(raceId_list))
    return 12


if len(sys.argv) != 2:
    print('分析するraceId(race数前まで)をコマンドラインに入力して実行してください。')
    exit()
if len(sys.argv[1]) != 10:
    print('形式が違います。')
os.makedirs('./競馬場データ', exist_ok=True)
track_list = ['札幌', '函館', '福島', '新潟', '東京', '中山', '中京', '京都', '阪神', '小倉']
for track in track_list:
    os.makedirs('./競馬場データ/' + track, exist_ok=True)
getStart(sys.argv[1], track_list[int(sys.argv[1][4:6])])
