from utils import getAveragePaceInfo
import os

textFileName = 'コース分析.txt'
with open('./' + textFileName, 'r') as f:
    link_list = f.read().split('\n')
directoryName = link_list.pop(0)
distance = int(link_list.pop(0))
average_pace_info = getAveragePaceInfo('./', link_list, distance)
print(average_pace_info)
with open('./コース分析/' + os.path.join(directoryName, textFileName), 'w') as f:
    f.write('\n'.join(link_list))