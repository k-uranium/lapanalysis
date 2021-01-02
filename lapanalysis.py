import requests
from bs4 import BeautifulSoup
import os
import re
import math
import matplotlib.pyplot as plt
import datetime


def getContent(string, left_str, right_str, index):
    canFind = True
    start_index = string.find(left_str, index) + len(left_str)
    end_index = string.find(right_str, start_index)
    if start_index < len(left_str):
        canFind = False
    return canFind, string[start_index:end_index], end_index + len(right_str)


def getLink(span):
    return getContent(str(span), 'href="', '"', 0)


def getRaceName(div):
    return getContent(str(div), '>', '\n', 0)


def getRaceDetail(title):
    return getContent(str(title), '| ', ' レース情報', 0)


def getTitle(span):
    return getContent(str(span), 'title="', '"', 0)


def getTable(table):
    return getContent(str(table), '>', '</tbody>', 0)


def getTableRow(table, index):
    return getContent(str(table), '<tr>', '</tr>', index)


def getRowElement(table, index):
    return getContent(str(table), '>', '</td>', index)


def getAtag(row_element):
    return getContent(str(row_element), '>', '</a>', 0)


def getLap(link):
    site = requests.get(link)
    site.encoding = site.apparent_encoding
    data = BeautifulSoup(site.text, 'html.parser')
    lap = data.find(class_='race_lap_cell')
    lap_str = getRowElement(lap, 0)[1]
    # 取得したラップの文字列を分割し、数値に変換したリストの作成
    return list(map(float, lap_str.split(' - ')))


def writeGraph(directoryname, distance, race_info_list, filename):
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
            x = [race_info['distance'] / 200 +
                 i for i in range(int(race_info['distance'] / 200) + 1)]
        plt.plot(x, race_info['lap'], label=race_info['label'])
        if count == 10:
            break
    lg = plt.legend(bbox_to_anchor=(1.01, 0.5, 0.5, .100),
                    loc='lower left', prop={'family': fontname, 'size': 8})
    figure.savefig(os.path.join(directoryname, filename),
                   bbox_extra_artists=(lg,), bbox_inches='tight')


def getAveragePaceInfo(directoryname, link_list, distance):
    average_lap = [0 for i in range(int(distance / 200))]
    race_info_list = []
    if distance % 200 != 0:
        average_lap.append(0)
    year = datetime.datetime.now().year
    count = 1
    for link in link_list:
        if count == 6:
            break
        lap = getLap(link)
        race_info = {'label': str(year - count),
                     'lap': lap, 'distance': distance}
        race_info_list.append(race_info)
        for i in range(len(average_lap)):
            average_lap[i] += lap[i]
        count += 1
    for i in range(len(average_lap)):
        average_lap[i] /= 5
    average_pace_info = {'label': '平均ペース',
                         'lap': average_lap, 'distance': distance}
    race_info_list.insert(0, average_pace_info)
    savedirectorypath = os.path.join(directoryname, '平均ペース')
    os.makedirs(savedirectorypath, exist_ok=True)
    filename = '過去レース.png'
    writeGraph(savedirectorypath, distance, race_info_list, filename)
    return average_pace_info


def analysis(directoryname, average_pace_info, course, horse_name, link):
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
            # 競馬場チェック
            if count == 1:
                track = getAtag(row_element[1])[1]
                if track[0] < '0' or track[0] > '9':
                    break
            # レース名取得
            if count == 4:
                race_info['lap'] = getLap(
                    'https://db.netkeiba.com' + getLink(row_element[1])[1])
                race_name = getTitle(row_element[1])[1]
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
                ' ' + rank + '着'
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
            savedirectorypath = os.path.join(directoryname, horse_name)
            os.makedirs(savedirectorypath, exist_ok=True)
            writeGraph(savedirectorypath, average_pace_info['distance'],
                       race_info_list[i], filename[i])


with open('./平均ペース分析.txt', 'r') as f:
    link_list = f.read().split('\n')
link = link_list.pop(0)
if 'https://race.netkeiba.com/race/shutuba.html?race_id=' not in link:
    print('不正なURLです。')
    exit()
andPosition = link.find('&')
if andPosition != -1:
    link = link[:andPosition]
site = requests.get(link)
site.encoding = site.apparent_encoding
race_data = BeautifulSoup(site.text, 'html.parser')
detail = getRaceDetail(race_data.find('title'))[1]
split_detail = re.split('[年月日]', detail)
directoryname = './' + split_detail[0] + split_detail[1].zfill(2) + split_detail[2].zfill(
    2) + split_detail[3].replace(' ', '') + getRaceName(race_data.find(class_='RaceName'))[1]
os.makedirs(directoryname, exist_ok=True)
race_data01_class = str(race_data.find_all(class_='RaceData01'))
m_position = race_data01_class.find('m')
distance = int(race_data01_class[m_position-4:m_position])
course = race_data01_class[m_position-5]
horse_tag_list = race_data.find_all(class_='HorseName')
link = link.replace('shutuba', 'data_top')
average_pace_info = getAveragePaceInfo(directoryname, link_list, distance)
for horse_tag in horse_tag_list:
    link = getLink(horse_tag)
    horse_name = getTitle(horse_tag)
    if link[0] and horse_name[0]:
        analysis(directoryname, average_pace_info,
                 course, horse_name[1], link[1])
