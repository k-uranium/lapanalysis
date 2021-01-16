from utils import getAveragePaceInfo

textfilename = 'courseanalysis.txt'
with open('./' + textfilename, 'r') as f:
    link_list = f.read().split('\n')
distance = int(link_list.pop(0))
average_pace_info = getAveragePaceInfo('./', link_list, distance)
print(average_pace_info)
with open('./過去レース/' + textfilename, 'w') as f:
    f.write('\n'.join(link_list))