from utils import getAveragePaceInfo

with open('./コース分析.txt', 'r') as f:
    link_list = f.read().split('\n')
distance = int(link_list.pop(0))
average_pace_info = getAveragePaceInfo('./', link_list, distance)
