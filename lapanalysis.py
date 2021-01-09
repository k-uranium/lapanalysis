import requests
from bs4 import BeautifulSoup
import os
import re
from utils import getRaceDetail, getRaceName, getAveragePaceInfo, getTitle, getLink, analysis

with open('./raceanalysis.txt', 'r') as f:
    link_list = f.read().splitlines()
link = link_list.pop(0)
if 'https://race.netkeiba.com/race/shutuba.html?race_id=' not in link:
    print('不正なURLです。' + link)
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
with open(os.path.join(directoryname, 'raceanalysis.txt'), 'w') as f:
    f.write(link + '\n')
    f.write('\n'.join(link_list))
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
