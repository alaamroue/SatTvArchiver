from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Util.strxor import strxor
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import base64
import json
import requests
import subprocess
import shlex
import time
import threading
import os

# Strings used for look up
# Used for grabbing encryption key and Channel Key
ADA_BEGIN_LOOKUP = "var ada_taa = "
ADA_END_LOOKUP = ";"
CRYPT_KEY_BEGIN_LOOKUP = "res_ponse.link_url_4, '"
CRYPT_KEY_END_LOOKUP = "',"
IV = "www.elahmad.net/"
COMBINE_EVERY = 30

embed_result_74_list = ["nbn", "lbc_1", "otv_lb1", "manartv1", "almayadeen1", "teleliban"]

#Perform Aes Decrpytion
def decrypt_aes(message, key, iv):
    key = key.encode('utf-8')
    iv = iv.encode('utf-8')
    message = base64.b64decode(message)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    decrypted_data = unpad(cipher.decrypt(message), AES.block_size)
    return decrypted_data.decode('utf-8')

def getLinkUrl4(ChannelValue):
    if ChannelValue == "lbc":
        return "link_4"
    else:
        return "link_url_4"
        
#Remove lines starting with #
def cleanComments(input_string):
    lines = input_string.split('\n')
    lines_without_comments = [line for line in lines if not line.startswith('#')]
    output_string = '\n'.join(lines_without_comments)
    return output_string

def watchTvPost(ChannelName):
    MainChannelUrl = "https://elahmad.com/tv/watchtv.php?id=" + ChannelName
    MainChannelUrlResponseTxt = requests.post(url=MainChannelUrl).text
    
    #Find And parse ChannelKey and AesKey
    #    Find postions
    adaBeginAdres = MainChannelUrlResponseTxt.find(ADA_BEGIN_LOOKUP)+len(ADA_BEGIN_LOOKUP)
    adaEndAdres = MainChannelUrlResponseTxt[adaBeginAdres:].find(ADA_END_LOOKUP)+adaBeginAdres
    cryptKeyBeginAdres = MainChannelUrlResponseTxt.find(CRYPT_KEY_BEGIN_LOOKUP)+len(CRYPT_KEY_BEGIN_LOOKUP)
    cryptKeyEndAdres = MainChannelUrlResponseTxt[cryptKeyBeginAdres:].find(CRYPT_KEY_END_LOOKUP)+cryptKeyBeginAdres
    #     Parse json line containing Channel key and Channel Value
    dataReqAda = MainChannelUrlResponseTxt[adaBeginAdres:adaEndAdres]
    dataReqAdaJson = json.loads(dataReqAda.replace("'", "\""))
    #     Parse Channel key and value from json line
    ChannelKey = next(iter(dataReqAdaJson))
    ChannelValue = dataReqAdaJson[ChannelKey]
    #     Parse crpyt key based on postion
    AesKey = MainChannelUrlResponseTxt[cryptKeyBeginAdres:cryptKeyEndAdres]
    
    return ChannelKey, ChannelValue, AesKey

def nbnTvPost(nbnurl):
    url = "https://www.elahmad.com/tv/result/embed_result_74.php"
    headers = {
        'Host': 'www.elahmad.com',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.105 Safari/537.36',
        'Referer': 'https://www.elahmad.com/tv/watchtv.php',
        'Cache-Control': 'no-cache'
    }
    data = { "id" : nbnurl};
    x1 = requests.post(url=url, headers=headers, data=data)
    indexFileLinkEnc = json.loads(x1.text)['link'] # Response from watchtv.php which is encrypted with key found previously
    decoded_bytes = base64.b64decode(indexFileLinkEnc)
    decoded_string = decoded_bytes.decode('utf-8')
    result = decoded_string.replace('&amp;', '&')
    return result

#Grabs ChannelKey, ChannelValue, AesKey from the main channel html based on the channel name (watchtv.php?id=)
def getEncryptionKeyFromChannel(ChannelName):
    # Request the MainChannel Html
    ChannelKey, ChannelValue, AesKey = watchTvPost(ChannelName)

    #return ChannelKey, ChannelValue, AesKey
    return ChannelKey, ChannelValue, AesKey

#Setting up the watch.php request with the correct ada
# Using:
#       ChannelKey
#       ChannelValue
def grabVidIndexFileLinkEnc(ChannelKey, ChannelValue):
    if ChannelValue == "lbc":
        url = "https://elahmad.com/tv/mpegts_player.php"
    else:
        url = "https://elahmad.com/tv/watchtv.php"
    headers = {
        'Host': 'www.elahmad.com',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.105 Safari/537.36',
        'Referer': 'https://www.elahmad.com/tv/watchtv.php',
        'Cache-Control': 'no-cache'
    }
    data = { ChannelKey: ChannelValue};
    x1 = requests.post(url=url, headers=headers, data=data)
    print(x1.text)
    indexFileLinkEnc = json.loads(x1.text)[getLinkUrl4(ChannelValue)] # Response from watchtv.php which is encrypted with key found previously
    
    return indexFileLinkEnc

def getMonoFileFromIndexFileUrl(indexFileUrl):
    index_m3u8 = requests.get(url=indexFileUrl).text
    index_m3u8 = cleanComments(index_m3u8)[:-1]
    return index_m3u8

def getUpdatedMono(baseUrlOfClips, url):
    video_urls = cleanComments(requests.get(url=baseUrlOfClips+url).text)[:-1]
    video_urls_array = video_urls.split("\n")
    for i in range(len(video_urls_array)):
        video_urls_array[i] = baseUrlOfClips + video_urls_array[i]
    return video_urls_array

def getFilenameFromUrl(channelId, url):
    #Remove get data from url
    url = url[:url.rfind("?")]
    #Leave only last 6 slash and replace them with _
    if "smil:" in url:
        url = link[link.rfind("/")+1:]
    else:
        url = url.split("/")[-6:]
        url = "_".join(url)
    return channelId + "_" + url
        
def grabMonoLink(ChannelName):
    print("Request channel url... ")
    if ChannelName not in embed_result_74_list:
        ChannelKey, ChannelValue, AesKey = getEncryptionKeyFromChannel(ChannelName)
        print("ChannelKey: " + ChannelKey)
        print("ChannelValue: " + ChannelValue)
        print("AesKey: " + AesKey)
        
        print("")
        print("Request link to index file (encrpyted)")
        indexFileLinkEnc = grabVidIndexFileLinkEnc(ChannelKey, ChannelValue)
        print("indexFileLinkEnc: " + indexFileLinkEnc)
        
        print("")
        print("Decypting index file link")
        indexFileLinkDec = decrypt_aes(indexFileLinkEnc, AesKey, IV)
    else:
        indexFileLinkDec = nbnTvPost(ChannelName)
    baseUrlOfClips = indexFileLinkDec[:indexFileLinkDec.rfind("/")+1]
    print("indexFileLinkDec: " + indexFileLinkDec)
    print("baseUrlOfClips: " + baseUrlOfClips)
    
    print("")
    print("Geting mono file url")
    monoFileLink = getMonoFileFromIndexFileUrl(indexFileLinkDec)
    print("monoFileLink: " + baseUrlOfClips + monoFileLink)

    return baseUrlOfClips, monoFileLink

def combineConvertSrt(filesToCombine, outputFolder):
    #Combine Part
    combinedFilePathTs = outputFolder+"/"+filesToCombine[0][:-9]+"c.ts"
    combinedFilePathMp4 = combinedFilePathTs[:-3]+".mp4"
    print(f"Combing multiple .ts into {combinedFilePathTs}...")
    with open(combinedFilePathTs, 'wb') as output:
        for fileToCombine in filesToCombine:
            with open(outputFolder+"/"+fileToCombine, 'rb') as file:
                output.write(file.read())
            print("removing: " + fileToCombine)
            os.remove(outputFolder+"/"+fileToCombine)
    #Srt Part
    print("Speech recognition...")
    command_string = f"whisper {combinedFilePathTs} --language Arabic --model small --output_dir {outputFolder}"
    speechProccess = subprocess.run(shlex.split(command_string), capture_output = False, text = False)
    print(f"Converting to mp4 into {combinedFilePathMp4}...")
    command_string = f"ffmpeg -i {combinedFilePathTs} -vcodec libx265 -crf 28 {combinedFilePathMp4}"
    subprocess.run(shlex.split(command_string), capture_output = False, text = False)
    os.remove(combinedFilePathTs)
    print("Batch Finished...")

def getAndSaveClip(clip_url, saved_clips_list, clips_saved, filename, outputFolder):
    print("Downloading " + filename)
    response = requests.get(clip_url)
    with open(outputFolder+"/"+filename, 'wb') as f:
        f.write(response.content)
    if clips_saved%COMBINE_EVERY == 0 and clips_saved != 0:
        combineConvertSrt(saved_clips_list,outputFolder)
        saved_clips_list=[]
        
def createDirectory(foldername):
    if not os.path.exists(foldername):
        os.makedirs(foldername)

def checkLatestUrlsValid(urlsList):
    if(urlsList[-1][-9:]=='Not found'):
        return False
    return True

#channelId = "nbn"          #embed_result_74.php
channelId = "mtv_lebanon"   #uses watchtv.php and link_url_4 
#channelId = "aljadeed"     #uses watchtv.php and link_url_4 
#channelId = "lbc_1"        #embed_result_74.php
#channelId = "otv_lb1"      #embed_result_74.php
#channelId = "lbc"          #(NoSupport) Continous Stream: uses mpegts_player.php and link_4 
#channelId = "manartv1"     #(NoSupport)embed_result_74.php
#channelId = "almayadeen1"  #embed_result_74.php
#channelId = "teleliban"    #embed_result_74.php

createDirectory(channelId)
baseUrlOfClips, monoFileLink = grabMonoLink(channelId)

last_finished = ""
clips_saved = 0
saved_clips_list = []

print("Main Loop Started...")
while(True):
    latest_urls = getUpdatedMono(baseUrlOfClips, monoFileLink)
    #Check MonoLink is valid and update it
    if not checkLatestUrlsValid(latest_urls):
        baseUrlOfClips, monoFileLink = grabMonoLink(channelId)
        continue
    #Download new clips
    if (latest_urls[-1]!=last_finished):
        #Define the new clip url
        clips_saved += 1
        last_finished = latest_urls[-1] #Clip to Download
        saveAsFilename = getFilenameFromUrl(channelId, last_finished)
        
        #create a thread and download in it
        saved_clips_list.append(saveAsFilename)
        threading.Thread(target=getAndSaveClip, args=(last_finished,saved_clips_list, clips_saved,saveAsFilename,channelId,), name='saveClipThread').start()
    #Combine clips and convert to mp4 and use speech recoginition
    if clips_saved%COMBINE_EVERY == 0 and clips_saved != 0:
        saved_clips_list=[]
    time.sleep(1)

