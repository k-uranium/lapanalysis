import requests
from bs4 import BeautifulSoup
import os
import re
import csv
from utils import getRaceDetail, getRaceName, getAveragePaceInfo, getTitle, getLink, getNum, analysis

textFileName = 'レース分析.txt'
with open('./' + textFileName, 'r', encoding='utf-8') as f:
    link_list = f.read().splitlines()
link = link_list.pop(0)
if 'https://race.netkeiba.com/race/shutuba.html?race_id=' not in link:
    print('不正なURLです。' + link)
    exit()
link = link.split('&')[0]
trackId = link[-8:-6]
site = requests.get(link)
site.encoding = site.apparent_encoding
race_data = BeautifulSoup(site.text, 'html.parser')
detail = getRaceDetail(race_data.find('title'))[1]
split_detail = re.split('[年月日]', detail)
race = split_detail[3].replace(' ', '')
race_name = getRaceName(race_data.find(class_='RaceName'))[1]
directoryName = os.path.join(os.path.join('レース分析', split_detail[0] + split_detail[1].zfill(2) + split_detail[2].zfill(2)), race + race_name)
os.makedirs(directoryName, exist_ok=True)
print(race)
with open(os.path.join(directoryName, textFileName), 'w') as f:
    f.write(link + '\n')
    f.write('\n'.join(link_list))
race_data01_class = str(race_data.find_all(class_='RaceData01')).split('m')[0]
distance = int(race_data01_class[-4:])
course = race_data01_class[-5]
horse_tag_list = race_data.find_all(class_='HorseName')
link = link.replace('shutuba', 'data_top')
average_pace_info = getAveragePaceInfo(directoryName, link_list, distance)
track_list = ['札幌', '函館', '福島', '新潟', '東京', '中山', '中京', '京都', '阪神', '小倉']
with open(os.path.join(directoryName, '平均指数表.csv'), 'w', newline='', encoding='cp932') as f:
    writer = csv.writer(f)
    writer.writerow(['馬名', '分析レース数', '平均スピード指数', '平均ペース指数', '平均上がり指数', '平均先行指数', '枠複勝率良', '種牡馬複勝率良', '枠複勝率稍', '種牡馬複勝率稍', '枠有利度重', '種牡馬有利度重', '枠有利度不', '種牡馬有利度不'])
for i, horse_tag in enumerate(horse_tag_list):
    link = getLink(horse_tag)
    horse_name = getTitle(horse_tag)
    num = getNum(i, len(horse_tag_list) - 1)
    if link[0] and horse_name[0]:
        analysis(directoryName, average_pace_info,
                 course, horse_name[1], link[1], track_list[int(trackId) - 1], num)
