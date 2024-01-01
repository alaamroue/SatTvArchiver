import os
import requests
import json
import base64

from encryptions import decryptAes
from channel import Channel
from helpers import *

# Manager class for web connection and function routing
# All requests are made from this function based on the scheme
class SurfManager:
    def __init__(self, channelId):
        self.channel = Channel(channelId)
        self.aesKey = ""
        self.requestParams = {}
        self.indexFile = ""
        self.baseUrl = ""
        self.chunkListUrl = ""

    # Request the parameters that need to be POST-requested to get the index file (which in turn includes link to chunk file)
    def getReqsParams(self):
        MainUrl = self.channel.scheme.mainReqUrl

        print("[INFO]: Request being made to: " + MainUrl)
        response = requests.post(url=MainUrl).text
        if "not found" in response.lower():
            print(f"[WARNING]: Response from {MainUrl} has 'Not Found' in it")
        
        self.aesKey        = self.channel.scheme.findAesKey(response)
        self.requestParams = self.channel.scheme.findRequestParameters(response)
        print("[INFO]: AES Key Extracted: " + self.aesKey)
        print("[INFO]: Request Params Extracted: " + json.dumps(self.requestParams))

    # Request the index file (which in turn includes link to chunk file)
    def getIndexFile(self):

        url = self.channel.scheme.getIndexFatherUrl()
        print(f"[INFO]: Requesting link to index file from {url}")

        headers = {
            'Host': 'www.elahmad.com',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.105 Safari/537.36',
            'Referer': 'https://www.elahmad.com/tv/watchtv.php',
            'Cache-Control': 'no-cache'
        }

        response = requests.post(url=url, headers=headers, data=self.requestParams).text
        if "not found" in response.lower():
            print(f"[WARNING]: Response from {url} has 'Not Found' in it")
        
        jsonResponse = json.loads(response) 
        print(f"[INFO]: Response was: {response}")
        link = next(iter(jsonResponse.values()))
        print(f"[INFO]: Index File data was found: {link}")

        if self.channel.scheme.encrypt:
            linkClean = decryptAes(link, self.aesKey)
            print(f"[INFO]: Index File url was decrypted: {linkClean}")
        else:
            decoded_bytes = base64.b64decode(link)
            decoded_string = decoded_bytes.decode('utf-8')
            linkClean = decoded_string.replace('&amp;', '&')
            print(f"[INFO]: Index File parameter was cleaned: {linkClean}")

        return linkClean
    
    # Request chunk file url which contains the latest chunks available (the server refreshes this file for us)
    # This file will always contain the latest chunk of the stream at the time of the request  
    def getChunkListUrl(self):
        print("[INFO]: Requesting url to the chunk file list is (File that automatically updated with new clips) ... ")
        response = requests.get(url=self.indexFile).text
        chunksUrl = cleanCommentsAndLines(response)
        chunksUrl = self.baseUrl + chunksUrl
        print(f"[INFO]: Chunk file extracted: {chunksUrl}")
        return chunksUrl

    # Request the parameters, use them to request the index file url, use it to request the chunk file url
    def grabChunkListUrl(self):
        print("[INFO]: Requesting channel url ")

        if self.channel.scheme.encrypt == True:
            print("[INFO]: Scheme is encrypted... ")
            self.getReqsParams()
        else:
            print("[INFO]: Scheme is not encrypted... ")
            if self.channel.id == "aljadeed":
                self.getReqsParams()
            else:
                self.requestParams = { "id" : self.channel.id}
            
        self.indexFile = self.getIndexFile()
        self.baseUrl = self.indexFile[:self.indexFile.rfind("/")+1]
        print(f"[INFO]: Baseurl was extracted: {self.baseUrl}")

        self.chunkListUrl = self.getChunkListUrl()

    def getChunkList(self, trail=0):
        response = requests.get(self.chunkListUrl).text

        # Check response valid
        if("not found" in response.lower()):
            self.grabChunkListUrl()
            if trail < 5:
                print(f"[INFO]: Url to Chunk List File returned 'not found'. Will try to update")
                return self.getChunkList(trail+1)
            else:
                print(f"[ERROR]: Url to Chunk List File returned 'not found'. Exiting after 5 tries")
                exit()

        chunkFileContent = cleanComments(response)[:-1]
        chunkFileContentArray = chunkFileContent.split("\n")
        for i in range(len(chunkFileContentArray)):
            chunkFileContentArray[i] = self.baseUrl + chunkFileContentArray[i]
        return chunkFileContentArray


