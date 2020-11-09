import json
import thulac
import re
thu2 = thulac.thulac(seg_only=False)
thu1 = thulac.thulac(seg_only=True)


def genTokens(st):
    res = thu1.cut(st, text=True)
    #res = re.sub(r'[，。【】、()（）：:；;\'\"《》！？,.“”]+', "", res)
    res2 = thu2.cut(st, text=True)
    return {'text': st, 'tokens': res, 'ptokens': res2}


with open("rmrb1946-2003-delrepeat.txt") as file1:
    rmrbData = file1.readlines()
print("_______________________")
with open("Sogou0010.txt") as file2:
    sData10 = file2.readlines()
rmrbData.extend(sData10)
print("_______________________")
with open("Sogou0011.txt") as file3:
    sData11 = file3.readlines()
rmrbData.extend(sData11)
print("_______________________")
with open("Sogou0012.txt") as file4:
    sData12 = file4.readlines()
rmrbData.extend(sData12)
print("_______________________")
with open("Sogou0013.txt") as file5:
    sData13 = file5.readlines()
rmrbData.extend(sData13)
print("_______________________")
with open("Sogou0014.txt") as file6:
    sData14 = file6.readlines()
rmrbData.extend(sData14)
print("_______________________")

rmrbDict = dict(zip([it for it in range(len(rmrbData))],
                    [genTokens(it.strip()) for it in rmrbData]))
with open("rmrb.json", 'w', encoding='utf-8') as jfile1:
    json.dump(rmrbDict, jfile1, ensure_ascii=False)
