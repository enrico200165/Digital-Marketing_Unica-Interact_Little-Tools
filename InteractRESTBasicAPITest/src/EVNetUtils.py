#!/usr/bin/env python

import globals as g
import requests
from InteractRESTCore import interactCommands as ic

head = {
    "Cache-Control": "max-age=0"
    ,"Connection" : "keep-alive"
    ,"Content-Length": "469"
    ,"Upgrade-Insecure-Requests": "1"
    ,"Content-Type": "application/json"
    ,"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36"
    ,"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
    ,"Referer" : "http://localhost:9080/interact/jsp/testClient.jsp"
    ,"Accept-Encoding": "gzip, deflate, br"
    ,"Accept-Language" : "en-US,en;q=0.9"
    ,"Cookie" : "Idea-6c97b77a=8c95675d-4caf-44ad-950d-dcc5995749bd; interact=0000IO6tuvPuo3u1iFq2fQde6m4:-1"
     }


def logBanner(m, logit = True):
    s = g.verification_header.format(m)
    if logit:
        g.log.info(g.verification_header.format(m))

def setFiddler(activateIt, proxyDict,UACIUrl):
    '''
    '''
    if (activateIt):
        http_proxy  = "http://127.0.0.1:8888"
        proxyDict["http"] = http_proxy
        part1 = UACIUrl.split("//")[0]
        part2 = UACIUrl.split("//")[1]
        part2 = part2.split("/")[0]
        proxyDict[part1+"//"+part2] = http_proxy
        proxyDict["9080"] = http_proxy
        g.log.info("fiddler proxying active: "+str(activateIt) +"\n"+ str(proxyDict))


def myREST(bodyJson, UACIUrl, verbose):
    global log
    ret = requests.post(UACIUrl, headers=head, data = bodyJson
                        , proxies = g.fiddlerProxy)
    # adjust from bytes to string
    if (not ret.ok):
        g.log.info("error")
    if (verbose or not ret.ok):
        g.log.info("response content:\n");
        g.log.info(ret.content)
    return ret


def callAPI(cmd):
    if not isinstance(cmd, ic.JSONCmd):
        raise TypeError

    resp = myREST(cmd.get_json(), False)
    cmd.set_json_from_rsp(resp)
    if not cmd.OK():
        cmd.dump(True)
        return False
    return True

if __name__ == "__main__":
    pass
