import json
import thulac
import re


with open("rmrb1946-2003-delrepeat.txt") as file1:
    rmrbData = file1.readlines()
with open("rmrb_seg.txt") as file2:
    rmrbData2 = file2.readlines()
with open("rmrb_segtag.txt") as file3:
    rmrbData3 = file3.readlines()
rmrbDict = {}
for it in range(len(rmrbData)):
    if int(it) % 1000 == 0:
        print(it)
    rmrbDict[str(it)] = {'text': rmrbData[it],
                         'tokens': rmrbData2[it], 'ptokens': rmrbData3[it]}


with open("rmrb2.json", 'w', encoding='utf-8') as jfile1:
    json.dump(rmrbDict, jfile1, ensure_ascii=False)
print(rmrbDict['0'])
