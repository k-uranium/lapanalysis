import requests
from bs4 import BeautifulSoup
import re
import os
import math
import csv
import matplotlib.pyplot as plt
import pandas as pd


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


def getNum(n, N):
    if N <= 8:
        return n
    else:
        num = 0
        i = 1
        while i <= 8:
            if i <= 8 - N % 8:
                dn = int(N / 8)
            else:
                dn = int(N / 8) + 1
            num += dn
            if n <= num:
                return i
            else:
                i += 1


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
        condition = ptag[4][ptag[4].find(':') + 2:]
        detail = getPtag(data.find(class_='smalltxt'))[1].split(
            u'\xa0')[0]
        split_detail = detail.split(' ')
        time = re.split('[年月日]', split_detail[0])
        label = time[0] + '/' + time[1].zfill(2) + '/' + time[2].zfill(
            2) + ' ' + split_detail[1] + ' ' + getH1(ptag[0])[1] + '(' + condition + ')'
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


def getBaseTime(dir_path, level):
    time_dictionary_list = getTimeDictionaryList(os.path.join(dir_path, '平均タイム.txt'))
    condition_base_time = time_dictionary_list[level]['avetime']
    if time_dictionary_list[2]['count'] != 0:
        return time_dictionary_list[2]['avetime'], condition_base_time
    elif time_dictionary_list[3]['count'] != 0:
        return time_dictionary_list[3]['avetime'] * 1.01, condition_base_time
    elif time_dictionary_list[4]['count'] != 0:
        return time_dictionary_list[4]['avetime'] * 1.02, condition_base_time
    else:
        return time_dictionary_list[5]['avetime'] * 1.04, condition_base_time


def getConditionK(base_time, time, time_diff, distance_k):
    race_time = time
    if time_diff > 0:
        race_time -= time_diff
    return (race_time - base_time) * distance_k * 10


def getFrontK(pace_k, distance, course):
    distance_list = [1000, 1150, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2800, 3000, 3200, 3400, 3600]
    turf_k_list = [10.0, None, 7.0, None, 4.0, 2.0, 0.0, -2.0, -4.0, None, -6.0, None, -8.0, -9.0, -10.0, -10.5, -11.0, -11.5, -12.0, -12.25, -12.5, -12.75]
    dart_k_list = [13.0, 12.0, 11.0, 10.0, 9.0, None, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0, None, 0.0, -1.0, None, None, None, None, None, None, None]
    index = distance_list.index(distance)
    if course == '芝':
        ave_pace_k = turf_k_list[index]
    else:
        ave_pace_k = dart_k_list[index]
    return pace_k - ave_pace_k


def getSpeedK(weight, time, time_diff, spart, distance, dir_path, course, level):
    base_time, condition_base_time = getBaseTime(os.path.join(dir_path, '良'), level)
    distance_k = 1 / base_time * 100
    condition_k = getConditionK(condition_base_time, time, time_diff, distance_k)
    speed_k = (base_time - time) * distance_k * 10 + condition_k + (weight - 55) * 2 + 100
    if course == '芝':
        base_spart = 33.5
    else:
        base_spart = 35.5
    a = ((base_time - base_spart) - (time - spart)) * distance_k * 10
    b = condition_k * distance_k / (distance_k + 1)
    c = (weight - 55) * 2 * distance_k / (distance_k + 1)
    pace_k = a + b + c
    d = (base_spart - spart) * distance_k * 10
    e = condition_k / (distance_k + 1)
    f = (weight - 55) * 2 / (distance_k + 1)
    spart_k = d + e + f
    return speed_k, pace_k, spart_k, getFrontK(pace_k, distance, course)


def getFramePlaceRate(path, frame):
    with open(os.path.join(path, '枠別成績.csv'), 'r') as f:
        reader = csv.reader(f)
        line = [row for row in reader]
        return float(line[frame][7])


def getFrameK(frame, dir_path):
    dir_list = ['良', '稍重', '重', '不良']
    frame_k = []
    for directory in dir_list:
        path = os.path.join(dir_path, directory)
        if os.path.exists(path):
            frame_place_rate = getFramePlaceRate(path, frame)
        else:
            frame_place_rate = 0.0
        frame_k.append(frame_place_rate / 100)
    return frame_k


def getFatherPlaceRate(path, father):
    df = pd.read_csv(os.path.join(path, '種牡馬別成績.csv'), encoding='cp932')
    line = df[df['種牡馬'] == father]
    if len(line) != 0:
        return float(line['複勝率'])
    else:
        return 0.0


def getFatherK(father, dir_path):
    dir_list = ['良', '稍重', '重', '不良']
    father_k = []
    for directory in dir_list:
        path = os.path.join(dir_path, directory)
        if os.path.exists(path):
            father_place_rate = getFatherPlaceRate(path, father)
        else:
            father_place_rate = 0.0
        father_k.append(father_place_rate / 100)
    return father_k


def analysis(directoryName, average_pace_info, course, horse_name, link, main_track, num):
    print(num, horse_name, link)
    site = requests.get(link)
    site.encoding = site.apparent_encoding
    data = BeautifulSoup(site.text, 'html.parser')
    table = data.find(class_='db_h_race_results nk_tb_common')
    table_str = getTable(table)[1]
    start_index = 0
    race_info_list = [[average_pace_info], [
        average_pace_info], [average_pace_info]]
    speed_k_list = []
    pace_k_list = []
    spart_k_list = []
    front_k_list = []
    distance_list = []
    track_list = []
    condition_list = []
    rank_list = []
    weight_list = []
    frame_list = []
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
                level = getLevel(race_name)
                race_info['lap'] = getLap(
                    'https://db.netkeiba.com' + getLink(row_element[1])[1])
            # 枠の取得
            if count == 7:
                frame = int(row_element[1])
            # 着順を取得
            if count == 11:
                rank = row_element[1]
                if rank[0] < '0' or rank[0] > '9':
                    break
            # 騎手取得
            if count == 12:
                jockey = getTitle(row_element[1])[1]
            # 斤量取得
            if count == 13:
                weight = float(row_element[1])
            # 距離取得
            if count == 14:
                if row_element[1][0] != course:
                    break
                race_info['distance'] = int(row_element[1][1:])
            # 馬場取得
            if count == 15:
                condition = row_element[1]
            # タイム取得
            if count == 17:
                time = int(row_element[1][0]) * 60 + float(row_element[1][2:])
            # 着差取得
            if count == 18:
                time_diff = float(row_element[1])
            # レースペース取得
            # if count == 21:
            #     race_pace_str = row_element[1].split('-')
            #     race_pace = map(float, race_pace_str)
            # 上がりタイム取得
            if count == 22:
                spart = float(row_element[1])
            count += 1
        if count == 28:
            if abs(average_pace_info['distance'] - race_info['distance']) <= 400:
                race_info['label'] = day + ' ' + race_name + \
                    '(' + jockey + ',' + condition + ')' + \
                    ' ' + rank + '着 ' + track + str(race_info['distance']) + 'm'
                if rank == '1' or rank == '2':
                    race_info_list[0].append(race_info)
                elif rank == '3' or rank == '4' or rank == '5':
                    race_info_list[1].append(race_info)
                else:
                    race_info_list[2].append(race_info)
            dir_path = os.path.join(os.path.join('競馬場データ', track), str(race_info['distance']) + course)
            speed_k, pace_k, spart_k, front_k = getSpeedK(weight, time, time_diff, spart, race_info['distance'], dir_path, course, level)
            speed_k_list.append(speed_k)
            pace_k_list.append(pace_k)
            spart_k_list.append(spart_k)
            front_k_list.append(front_k)
            condition_list.append(condition)
            distance_list.append(race_info['distance'])
            frame_list.append(frame)
            track_list.append(track)
            rank_list.append(rank)
            weight_list.append(weight)
    dir_path = os.path.join(os.path.join('競馬場データ', main_track), str(average_pace_info['distance']) + course)
    frame_k = getFrameK(num, dir_path)
    father_k = getFatherK(getFather(link), dir_path)
    filename = [horse_name + '連対.png', horse_name + '掲示板.png', horse_name + '凡走.png']
    for i in range(3):
        if race_info_list[i]:
            saveDirectoryPath = os.path.join(directoryName, horse_name)
            os.makedirs(saveDirectoryPath, exist_ok=True)
            writeGraph(saveDirectoryPath, average_pace_info['distance'],
                       race_info_list[i], filename[i])
    with open(os.path.join(saveDirectoryPath, horse_name + '指数表.csv'), 'w', newline='', encoding='cp932') as f:
        writer = csv.writer(f)
        writer.writerow(['スピード指数', 'ペース指数', '上がり指数', '先行指数', '競馬場', '距離', '馬場', '斤量', '枠', '着順'])
        sum_speed_k = sum_pace_k = sum_spart_k = sum_front_k = sum_div_value = 0.0
        for i in range(len(speed_k_list)):
            writer.writerow([speed_k_list[i], pace_k_list[i], spart_k_list[i], front_k_list[i], track_list[i], distance_list[i], condition_list[i], weight_list[i], frame_list[i], rank_list[i]])
            distance_k = 1.0 - abs(average_pace_info['distance'] - distance_list[i]) * 0.01 * 0.05
            if distance_k < 0:
                distance_k = 0.0
            if i < 5:
                recently_k = 1.25 - 0.05 * i
            else:
                recently_k = 1.1 - 0.01 * i
            if recently_k < 0:
                recently_k = 0.0
            sum_div_value += distance_k * recently_k
            sum_speed_k += speed_k_list[i] * distance_k * recently_k
            sum_pace_k += pace_k_list[i] * distance_k * recently_k
            sum_spart_k += spart_k_list[i] * distance_k * recently_k
            sum_front_k += front_k_list[i] * distance_k * recently_k
    with open(os.path.join(directoryName, '平均指数表.csv'), 'a', newline='', encoding='cp932') as f:
        writer = csv.writer(f)
        if sum_div_value != 0:
            ave_speed_k = sum_speed_k / sum_div_value
            ave_pace_k = sum_pace_k / sum_div_value
            ave_spart_k = sum_spart_k / sum_div_value
            ave_front_k = sum_front_k / sum_div_value
        else:
            ave_speed_k = ave_pace_k = ave_spart_k = ave_front_k = 0.0
        writer.writerow([horse_name, len(speed_k_list), ave_speed_k, ave_pace_k, ave_spart_k, ave_front_k, frame_k[0], father_k[0], frame_k[1], father_k[1], frame_k[2], father_k[2], frame_k[3], father_k[3]])
