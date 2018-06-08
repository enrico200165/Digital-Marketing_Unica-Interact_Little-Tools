
import datetime

def timeStamp():
    s = datetime.datetime.utcnow().strftime('%m%d %H:%M:%S.%f')[:-3]
    return s


def tstampAudienceID(prefix = ""):
    return prefix+timeStamp()


def genAudienceIDs(n, prefix = ""):
    ids = []
    for i in range(1,n+1):
        nr =  '{nr:03d}'.format(nr=i)
        id = tstampAudienceID()+"-"+nr
        ids.append(id)
    return ids

