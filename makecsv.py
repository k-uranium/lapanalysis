import os
import sys
from utils import getDirecoryList, makeCsv

if len(sys.argv) == 1:
    track_dir_list = getDirecoryList('競馬場データ')
    for track_dir in track_dir_list:
        track_dir_path = os.path.join('競馬場データ', track_dir)
        course_dir_list = getDirecoryList(track_dir_path)
        for course_dir in course_dir_list:
            course_dir_path = os.path.join(track_dir_path, course_dir)
            main_dir_list = getDirecoryList(course_dir_path)
            for main_dir in main_dir_list:
                dir_path = os.path.join(course_dir_path, main_dir)
                makeCsv(dir_path)
exit()
if len(sys.argv) != 5:
    print('入力は[競馬場 距離 コース 馬場]で入力してください。')
    exit()
track_list = ['札幌', '函館', '福島', '新潟', '東京', '中山', '中京', '京都', '阪神', '小倉']
track = sys.argv[1]
if track not in track_list:
    print('競馬場が存在しません。')
    exit()
distance = sys.argv[2]
if len(distance) != 4:
    print('距離が正しくありません。')
    exit()
course = sys.argv[3]
if course == 'ダート':
    course = 'ダ'
if '障' in course:
    print('障害レースは分析していません。')
condition = sys.argv[4]
dir_path = os.path.join(os.path.join(os.path.join('競馬場データ', track), distance + course), condition)
makeCsv(dir_path)
