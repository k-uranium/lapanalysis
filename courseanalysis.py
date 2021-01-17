from utils import getAveragePaceInfo
import os

textFileName = 'コース分析.txt'
dirctoryPath = './コース分析'
with open('./' + textFileName, 'r', encoding='utf-8') as f:
    link_list = f.read().split('\n')
os.makedirs(dirctoryPath, exist_ok=True)
directoryName = os.path.join(dirctoryPath, link_list.pop(0))
distance = int(link_list.pop(0))
average_pace_info = getAveragePaceInfo('./', link_list, distance, directoryName)
print(average_pace_info)
with open(os.path.join(directoryName, textFileName), 'w') as f:
    f.write('\n'.join(link_list))