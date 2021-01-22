from utils import getAveragePaceInfo
import os

textFileName = 'コース分析.txt'
directoryPath = './コース分析'
with open('./' + textFileName, 'r', encoding='utf-8') as f:
    link_list = f.read().split('\n')
os.makedirs(directoryPath, exist_ok=True)
saveDirectoryName = link_list.pop(0)
directoryName = os.path.join(directoryPath, saveDirectoryName)
distance = int(link_list.pop(0))
average_pace_info = getAveragePaceInfo('./', link_list, distance, directoryName)
print(average_pace_info)
with open(os.path.join(directoryName, textFileName), 'w', encoding='UTF-8') as f:
    f.write(saveDirectoryName + '\n')
    f.write(str(distance) + '\n')
    f.write('\n'.join(link_list))
