import requests
from bs4 import BeautifulSoup
import os
import re
import csv
import sys
from utils import getRaceDetail, getRaceName, getTitle, getLink, getNum, getRowElement, getLevel, getTable, getTableRow, getAtag, getAverageTime, getK, getFather, getFatherK, getFrameK


def calc(directoryName, main_distance, course, horse_name, link, main_track, num, horse_weight, main_level):
    print(num, horse_weight, horse_name)
    site = requests.get(link)
    site.encoding = site.apparent_encoding
    data = BeautifulSoup(site.text, 'html.parser')
    table = data.find(class_='db_h_race_results nk_tb_common')
    table_str = getTable(table)[1]
    start_index = 0
    high_time_total_k_list = []
    middle_time_total_k_list = []
    slow_time_total_k_list = []
    time_category_list = []
    div_value_list = []
    front_k_list = []
    stamina_k_list = []
    spart_k_list = []
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
        while(True):
            row_element = getRowElement(table_row[1], start_index_element)
            start_index_element = row_element[2]
            if not row_element[0]:
                break
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
                race_level = getLevel(race_name)
            # 枠の取得
            if count == 7:
                frame = int(row_element[1])
            # 着順を取得
            if count == 11:
                rank = row_element[1].split('(')[0]
                if rank[0] < '0' or rank[0] > '9':
                    break
            # 斤量取得
            if count == 13:
                weight = float(row_element[1])
            # 距離取得
            if count == 14:
                if row_element[1][0] != course:
                    break
                race_distance = int(row_element[1][1:])
            # 馬場取得
            if count == 15:
                condition = row_element[1]
                if condition == '稍':
                    condition += '重'
                if condition == '不':
                    condition += '良'
            # タイム取得
            if count == 17:
                time = int(row_element[1][0]) * 60 + float(row_element[1][2:])
            # 着差取得
            if count == 18:
                time_diff = float(row_element[1])
            # レースペース取得
            if count == 21:
                race_pace_str = row_element[1].split('-')
                race_pace = list(map(float, race_pace_str))
            # 上がりタイム取得
            if count == 22:
                spart = float(row_element[1])
            count += 1
        if count == 28:
            dir_path = os.path.join(os.path.join(
                '競馬場データ', track), str(race_distance) + course)
            race_time = time
            if time_diff > 0:
                race_time -= time_diff
            ave_time = getAverageTime(os.path.join(
                dir_path, condition), race_level)
            if race_distance <= 1200:
                race_pace.insert(1, 0.0)
            else:
                race_pace.insert(1, race_time - race_pace[0] - race_pace[1])
            if race_distance == 1000:
                race_pace[0] = race_time - race_pace[2]
            total_k, front_k, stamina_k, spart_k, div_value = getK(main_track, track, horse_weight, time, time_diff, main_distance, race_distance,
                                                                   spart, weight, int(rank), race_pace, main_level, race_level, num, frame, dir_path)
            if race_time - ave_time < -0.5:
                high_time_total_k_list.append(total_k)
                time_category_list.append('H')
            elif race_time - ave_time < 0.5:
                middle_time_total_k_list.append(total_k)
                time_category_list.append('M')
            else:
                slow_time_total_k_list.append(total_k)
                time_category_list.append('S')
            front_k_list.append(front_k)
            stamina_k_list.append(stamina_k)
            spart_k_list.append(spart_k)
            div_value_list.append(div_value)
            condition_list.append(condition)
            distance_list.append(race_distance)
            frame_list.append(frame)
            track_list.append(track)
            rank_list.append(rank)
            weight_list.append(weight)
    dir_path = os.path.join(os.path.join(
        '競馬場データ', main_track), str(main_distance) + course)
    frame_pk = getFrameK(num, dir_path)
    father_pk = getFatherK(getFather(link), dir_path)
    saveDirectoryPath = os.path.join(directoryName, horse_name)
    os.makedirs(saveDirectoryPath, exist_ok=True)
    with open(os.path.join(saveDirectoryPath, horse_name + '指数表.csv'), 'w', newline='', encoding='cp932') as f:
        writer = csv.writer(f)
        writer.writerow(['トータル指数', 'タイムカテゴリ', '先行指数', 'スタミナ指数', '上がり指数',
                         '競馬場', '距離', '馬場', '斤量', '枠', '着順'])
        sum_total_k = sum_front_k = sum_stamina_k = sum_spart_k = sum_div_value = sum_high_total_k = sum_high_div_value = sum_middle_total_k = sum_middle_div_value = sum_slow_total_k = sum_slow_div_value = 0.0
        high_count = middle_count = slow_count = 0
        for i in range(len(time_category_list)):
            time_category = time_category_list.pop()
            if time_category == 'H':
                total_k = high_time_total_k_list[high_count]
                writer.writerow([total_k, time_category, front_k_list[i], stamina_k_list[i], spart_k_list[i],
                                 track_list[i], distance_list[i], condition_list[i], weight_list[i], frame_list[i], rank_list[i]])
                if high_count < 5:
                    recently_k = 1.25 - 0.05 * high_count
                else:
                    recently_k = 1.1 - 0.01 * high_count
                div_value = div_value_list[i] * recently_k
                sum_high_div_value += div_value
                sum_high_total_k += total_k * div_value
                high_count += 1
            elif time_category == 'M':
                total_k = middle_time_total_k_list[middle_count]
                writer.writerow([total_k, time_category, front_k_list[i], stamina_k_list[i], spart_k_list[i],
                                 track_list[i], distance_list[i], condition_list[i], weight_list[i], frame_list[i], rank_list[i]])
                if middle_count < 5:
                    recently_k = 1.25 - 0.05 * middle_count
                else:
                    recently_k = 1.1 - 0.01 * middle_count
                div_value = div_value_list[i] * recently_k
                sum_middle_div_value += div_value
                sum_middle_total_k += total_k * div_value
                middle_count += 1
            else:
                total_k = slow_time_total_k_list.pop()
                writer.writerow([total_k, time_category, front_k_list[i], stamina_k_list[i], spart_k_list[i],
                                 track_list[i], distance_list[i], condition_list[i], weight_list[i], frame_list[i], rank_list[i]])
                if slow_count < 5:
                    recently_k = 1.25 - 0.05 * slow_count
                else:
                    recently_k = 1.1 - 0.01 * slow_count
                div_value = div_value_list[i] * recently_k
                sum_slow_div_value += div_value
                sum_slow_total_k += total_k * div_value
                slow_count += 1
            if i < 5:
                recently_k = 1.25 - 0.05 * i
            else:
                recently_k = 1.1 - 0.01 * i
            if recently_k < 0:
                recently_k = 0.0
            div_value = div_value_list[i] * recently_k
            sum_div_value += div_value
            sum_total_k += total_k * div_value
            sum_front_k += front_k_list[i] * div_value
            sum_stamina_k += stamina_k_list[i] * div_value
            sum_spart_k += spart_k_list[i] * div_value
    with open(os.path.join(directoryName, '平均指数表.csv'), 'a', newline='', encoding='cp932') as f:
        writer = csv.writer(f)
        if sum_div_value != 0:
            ave_total_k = sum_total_k / sum_div_value
            ave_front_k = sum_front_k / sum_div_value
            ave_stamina_k = sum_stamina_k / sum_div_value
            ave_spart_k = sum_spart_k / sum_div_value
        else:
            ave_total_k = ave_front_k = ave_stamina_k = ave_spart_k = 0.0
        if high_count != 0:
            ave_high_total_k = sum_high_total_k / sum_high_div_value
        else:
            ave_high_total_k = 0.0
        if middle_count != 0:
            ave_middle_total_k = sum_middle_total_k / sum_middle_div_value
        else:
            ave_middle_total_k = 0.0
        if slow_count != 0:
            ave_slow_total_k = sum_slow_total_k / sum_slow_div_value
        else:
            ave_slow_total_k = 0.0
        writer.writerow([horse_name, len(front_k_list), ave_total_k, ave_front_k, ave_stamina_k, ave_spart_k, ave_high_total_k, ave_middle_total_k, ave_slow_total_k, frame_pk[0],
                         father_pk[0], frame_pk[1], father_pk[1], frame_pk[2], father_pk[2], frame_pk[3], father_pk[3]])


for raceId in sys.argv[1:]:
    if len(raceId) != 10:
        print('形式が違います。')
        exit()
    for race_count in range(12):
        link = 'https://race.netkeiba.com/race/shutuba.html?race_id=' + raceId + str(race_count + 1).zfill(2)
        trackId = link[-8:-6]
        site = requests.get(link)
        site.encoding = site.apparent_encoding
        race_data = BeautifulSoup(site.text, 'html.parser')
        detail = getRaceDetail(race_data.find('title'))[1]
        split_detail = re.split('[年月日]', detail)
        race = split_detail[3].replace(' ', '')
        race_name = getRaceName(race_data.find(class_='RaceName'))[1]
        directoryName = os.path.join(os.path.join(
            'レース分析', split_detail[0] + split_detail[1].zfill(2) + split_detail[2].zfill(2)), race + race_name)
        os.makedirs(directoryName, exist_ok=True)
        print(race)
        race_level = getLevel(str(race_data.find(class_='RaceData02')))
        textFileName = 'レース分析.txt'
        with open(os.path.join(directoryName, textFileName), 'w') as f:
            f.write(link + '\n')
        race_data01_class = str(race_data.find_all(class_='RaceData01')).split('m')[0]
        distance = int(race_data01_class[-4:])
        course = race_data01_class[-5]
        if course == '障':
            continue
        horse_tag_list = race_data.find_all(class_='HorseName')
        weight_list = race_data.select('td[class="Txt_C"]')
        link = link.replace('shutuba', 'data_top')
        track_list = ['札幌', '函館', '福島', '新潟', '東京', '中山', '中京', '京都', '阪神', '小倉']
        with open(os.path.join(directoryName, '平均指数表.csv'), 'w', newline='', encoding='cp932') as f:
            writer = csv.writer(f)
            writer.writerow(['馬名', '分析レース数', '平均トータル指数', '平均先行指数', '平均スタミナ指数', '平均上がり指数', '高速平均トータル指数', '中速平均トータル指数', '低速平均トータル指数',
                             '枠複勝率良', '種牡馬複勝率良', '枠複勝率稍', '種牡馬複勝率稍', '枠有利度重', '種牡馬有利度重', '枠有利度不', '種牡馬有利度不'])
        for i, horse_tag in enumerate(horse_tag_list):
            link = getLink(horse_tag)
            horse_name = getTitle(horse_tag)
            if i != 0:
                horse_weight = getRowElement(weight_list[i - 1], 0)[1]
                num = getNum(i, len(horse_tag_list) - 1)
            if link[0] and horse_name[0]:
                calc(directoryName, distance, course, horse_name[1], link[1], track_list[int(
                    trackId) - 1], num, float(horse_weight), race_level)
