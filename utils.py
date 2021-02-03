import requests
from bs4 import BeautifulSoup
import re
import os
import math
import csv
import matplotlib.pyplot as plt


def getContent(string, left_str, right_str, index=0):
    canFind = True
    start_index = string.find(left_str, index) + len(left_str)
    end_index = string.find(right_str, start_index)
    if start_index < len(left_str):
        canFind = False
    return canFind, string[start_index:end_index], end_index + len(right_str)


def getLink(span):
    return getContent(str(span), 'href="', '"')


def getRaceName(div):
    return getContent(str(div), '>', '\n')


def getRaceDetail(title):
    return getContent(str(title), '| ', ' レース情報')


def getTitle(span):
    return getContent(str(span), 'title="', '"')


def getTable(table):
    return getContent(str(table), '>', '</tbody>')


def getTableRow(table, index):
    return getContent(str(table), '<tr>', '</tr>', index)


def getRowElement(table, index):
    return getContent(str(table), '>', '</td>', index)


def getAtag(row_element):
    return getContent(str(row_element), '>', '</a>')


def getPtag(row_element):
    return getContent(str(row_element), '>', '</p>')


def getH1(row_element):
    return getContent(str(row_element), '<h1>', '<')


def getSpan(table):
    return getContent(str(table), '<span>', '<')


def getLap(link):
    site = requests.get(link)
    site.encoding = site.apparent_encoding
    data = BeautifulSoup(site.text, 'html.parser')
    lap = data.find(class_='race_lap_cell')
    lap_str = getRowElement(lap, 0)[1]
    # 取得したラップの文字列を分割し、数値に変換したリストの作成
    return list(map(float, lap_str.split(' - ')))


def getFather(link):
    site = requests.get(link)
    site.encoding = site.apparent_encoding
    horse_data = BeautifulSoup(site.text, 'html.parser')
    father = getTitle(horse_data.find(class_='blood_table'))[1]
    return father


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


def makeCsv(dir_path):
    if not os.path.exists(dir_path):
        print('そのようなフォルダは存在しません。(' + os.path.join(os.getcwd(), dir_path) + ')')
        exit()
    with open(os.path.join(dir_path, '平均タイム.txt'), 'r', encoding='utf-8') as f:
        data_list = f.read().splitlines()
    with open(os.path.join(dir_path, '平均タイム.csv'), 'w', newline='', encoding='cp932') as f:
        writer = csv.writer(f)
        writer.writerow(['レースレベル', '平均タイム'])
        for datas in data_list:
            data = datas.split(' ')
            time_float = float(data[2])
            time = str(int(int(time_float) / 60)) + ':' + str(int(time_float) % 60).zfill(2) + '.' + str(time_float - int(time_float)).split('.')[1]
            writer.writerow([data[0], time])
    with open(os.path.join(dir_path, '枠別成績.txt'), 'r', encoding='utf-8') as f:
        data_list = f.read().splitlines()
    with open(os.path.join(dir_path, '枠別成績.csv'), 'w', newline='', encoding='cp932') as f:
        writer = csv.writer(f)
        writer.writerow(['枠', '1着', '2着', '3着', '着外', '単勝率', '連対率', '複勝率'])
        for datas in data_list:
            data = datas.split(' ')
            r1 = int(data[1])
            r2 = int(data[2])
            r3 = int(data[3])
            r4 = int(data[4])
            total = r1 + r2 + r3 + r4
            win_rate = r1 / total * 100
            quinella_rate = (r1 + r2) / total * 100
            place_rate = (total - r4) / total * 100
            writer.writerow([data[0] + '枠', r1, r2, r3, r4, win_rate, quinella_rate, place_rate])
    with open(os.path.join(dir_path, '種牡馬別成績.txt'), 'r', encoding='utf-8') as f:
        data_list = f.read().splitlines()
    with open(os.path.join(dir_path, '種牡馬別成績.csv'), 'w', newline='', encoding='cp932') as f:
        writer = csv.writer(f)
        writer.writerow(['種牡馬', '1着', '2着', '3着', '着外', '単勝率', '連対率', '複勝率'])
        father_grades_list_list = []
        for datas in data_list:
            data = datas.split('  ')
            r1 = int(data[1])
            r2 = int(data[2])
            r3 = int(data[3])
            r4 = int(data[4])
            total = r1 + r2 + r3 + r4
            win_rate = r1 / total * 100
            quinella_rate = (r1 + r2) / total * 100
            place_rate = (total - r4) / total * 100
            father_grades_list = [data[0], r1, r2, r3, r4, win_rate, quinella_rate, place_rate]
            insertFatherGradesList(father_grades_list_list, father_grades_list)
        father_grades_list_list.reverse()
        writer.writerows(father_grades_list_list)


def getTimeDictionaryList(path):
    time_dictionary_list = []
    with open(path, 'r', encoding='utf-8') as f:
        data_list = f.read().splitlines()
    for datas in data_list:
        data = datas.split(' ')
        data_dictionary = {'level': data[0], 'count': int(data[1]), 'avetime': float(data[2])}
        time_dictionary_list.append(data_dictionary)
    return time_dictionary_list


def getFrameDictionaryList(path):
    frame_dictionary_list = []
    with open(path, 'r', encoding='utf-8') as f:
        data_list = f.read().splitlines()
    for datas in data_list:
        data = datas.split(' ')
        data_dictionary = {'frame': int(data[0]), '1': int(data[1]), '2': int(data[2]), '3': int(data[3]), 'otherwise': int(data[4])}
        frame_dictionary_list.append(data_dictionary)
    return frame_dictionary_list


def getFatherDictionaryList(path):
    father_dictionary_list = []
    with open(path, 'r', encoding='utf-8') as f:
        data_list = f.read().splitlines()
    for datas in data_list:
        data = datas.split('  ')
        data_dictionary = {'father': data[0], '1': int(data[1]), '2': int(data[2]), '3': int(data[3]), 'otherwise': int(data[4])}
        father_dictionary_list.append(data_dictionary)
    return father_dictionary_list


def insertFatherGradesList(father_grades_list_list, father_grades_list):
    left = 0
    right = len(father_grades_list_list)
    while(left < right):
        middle = int((left + right) / 2)
        if father_grades_list_list[middle][7] < father_grades_list[7]:
            left = middle + 1
        elif father_grades_list_list[middle][7] > father_grades_list[7]:
            right = middle
        else:
            if father_grades_list_list[middle][6] > father_grades_list[6]:
                right = middle
            elif father_grades_list_list[middle][6] < father_grades_list[6]:
                left = middle + 1
            else:
                if father_grades_list_list[middle][5] > father_grades_list[5]:
                    right = middle
                elif father_grades_list_list[middle][5] < father_grades_list[5]:
                    left = middle + 1
                else:
                    if father_grades_list_list[middle][0] < father_grades_list[0]:
                        right = middle
                    else:
                        left = middle + 1
    father_grades_list_list.insert(left, father_grades_list)


def getDirecoryList(path):
    files = os.listdir(path)
    files_dir = [f for f in files if os.path.isdir(os.path.join(path, f))]
    return files_dir


def writeGraph(directoryName, distance, race_info_list, filename):
    fontname = 'MS Gothic'
    figure = plt.figure()
    xmax = math.ceil(distance / 200) + 2
    yrange = [10 + i * 0.5 for i in range(11)]
    # グラフの表示範囲の設定
    plt.xlim(0, xmax)
    plt.ylim(10, 15)
    plt.xticks(range(xmax + 1))
    plt.yticks(yrange)
    # タイトル、ラベルの設定
    plt.title(filename.replace('.png', ''), fontname=fontname)
    plt.xlabel('距離(F)', fontname=fontname)
    plt.ylabel('ラップタイム(s)', fontname=fontname)
    count = 0
    for race_info in race_info_list:
        count += 1
        if race_info['distance'] % 200 == 0:
            x = [i + 1 for i in range(int(race_info['distance'] / 200))]
        else:
            x = [race_info['distance'] % 200 / 200 +
                 i for i in range(int(race_info['distance'] / 200) + 1)]
            race_info['lap'][0] *= 200 / (race_info['distance'] % 200)
        plt.plot(x, race_info['lap'], label=race_info['label'])
        if count == 10:
            break
    lg = plt.legend(bbox_to_anchor=(1.01, 0.5, 0.5, .100),
                    loc='lower left', prop={'family': fontname, 'size': 8})
    figure.savefig(os.path.join(directoryName, filename),
                   bbox_extra_artists=(lg,), bbox_inches='tight')
    plt.close(figure)


def getAveragePaceInfo(directoryName, link_list, distance, saveDirectoryName='過去レース'):
    average_lap = [0 for i in range(int(distance / 200))]
    race_info_list = []
    if distance % 200 != 0:
        average_lap.append(0)
    count = 0
    for link in link_list:
        if link == '' or len(link) == 0:
            continue
        if 'https://db.netkeiba.com/race/' not in link:
            print('不正なURLです。' + link)
            continue
        site = requests.get(link)
        site.encoding = site.apparent_encoding
        data = BeautifulSoup(site.text, 'html.parser')
        ptag = getPtag(data.find(class_='racedata fc'))[
            1].split(u'\xa0')
        if len(ptag) < 4:
            print('不正なURLです。' + link)
            continue
        horse_field = ptag[4][ptag[4].find(':') + 2:]
        detail = getPtag(data.find(class_='smalltxt'))[1].split(
            u'\xa0')[0]
        split_detail = detail.split(' ')
        time = re.split('[年月日]', split_detail[0])
        label = time[0] + '/' + time[1].zfill(2) + '/' + time[2].zfill(
            2) + ' ' + split_detail[1] + ' ' + getH1(ptag[0])[1] + '(' + horse_field + ')'
        lap = getLap(link)
        race_info = {'label': label,
                     'lap': lap, 'distance': distance}
        race_info_list.append(race_info)
        for i in range(len(average_lap)):
            average_lap[i] += lap[i]
        count += 1
    for i in range(len(average_lap)):
        average_lap[i] /= count
    average_pace_info = {'label': '平均ペース',
                         'lap': average_lap, 'distance': distance}
    race_info_list.insert(0, average_pace_info)
    saveDirectoryPath = os.path.join(directoryName, saveDirectoryName)
    os.makedirs(saveDirectoryPath, exist_ok=True)
    filename = '過去レース.png'
    writeGraph(saveDirectoryPath, distance, race_info_list, filename)
    return average_pace_info


def analysis(directoryName, average_pace_info, course, horse_name, link):
    print(horse_name, link)
    site = requests.get(link)
    site.encoding = site.apparent_encoding
    data = BeautifulSoup(site.text, 'html.parser')
    table = data.find(class_='db_h_race_results nk_tb_common')
    table_str = getTable(table)[1]
    start_index = 0
    race_info_list = [[average_pace_info], [
        average_pace_info], [average_pace_info]]
    while(True):
        table_row = getTableRow(table_str, start_index)
        start_index = table_row[2]
        if not table_row[0]:
            break
        start_index_element = table_row[1].find('>')
        count = 0
        race_info = {'label': '', 'lap': [], 'distance': 0}
        while(True):
            row_element = getRowElement(table_row[1], start_index_element)
            start_index_element = row_element[2]
            if not row_element[0]:
                break
            # 開催日取得
            if count == 0:
                day = getAtag(row_element[1])[1]
            # 競馬場取得
            if count == 1:
                tmp_track = getAtag(row_element[1])[1]
                # 中央開催かどうかチェック
                if tmp_track[0] < '0' or tmp_track[0] > '9':
                    break
                track = re.sub('\d+', '', tmp_track)
            # レース名とラップ取得
            if count == 4:
                race_name = getTitle(row_element[1])[1]
                if '障害' in race_name:
                    break
                race_info['lap'] = getLap(
                    'https://db.netkeiba.com' + getLink(row_element[1])[1])
            # 着順を取得
            if count == 11:
                rank = row_element[1]
                if rank[0] < '0' or rank[0] > '9':
                    break
            # 騎手取得
            if count == 12:
                jockey = getTitle(row_element[1])[1]
            # 距離取得
            if count == 14:
                if row_element[1][0] != course:
                    break
                race_info['distance'] = int(row_element[1][1:])
                if abs(average_pace_info['distance'] - race_info['distance']) > 400:
                    break
            # 馬場取得
            if count == 15:
                horse_field = row_element[1]
            count += 1
        if count == 28:
            race_info['label'] = day + ' ' + race_name + \
                '(' + jockey + ',' + horse_field + ')' + \
                ' ' + rank + '着 ' + track + str(race_info['distance']) + 'm'
            if rank == '1' or rank == '2':
                race_info_list[0].append(race_info)
            elif rank == '3' or rank == '4' or rank == '5':
                race_info_list[1].append(race_info)
            else:
                race_info_list[2].append(race_info)
    filename = [horse_name + '連対.png', horse_name +
                '掲示板.png', horse_name + '凡走.png']
    for i in range(3):
        if race_info_list[i]:
            saveDirectoryPath = os.path.join(directoryName, horse_name)
            os.makedirs(saveDirectoryPath, exist_ok=True)
            writeGraph(saveDirectoryPath, average_pace_info['distance'],
                       race_info_list[i], filename[i])
