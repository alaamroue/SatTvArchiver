import json
from helpers import *

# Contants that define lookup values in the html
ADA_BEGIN_LOOKUP = "var ada_taa = "
ADA_END_LOOKUP = ";"
CRYPT_KEY_BEGIN_LOOKUP = "res_ponse.link_url_4, '"
CRYPT_KEY_END_LOOKUP = "',"

# Dictionary to track which schemes use encryption
scheme_enc_list = {
    "embed_result_74.php": False,
    "watchtv.php": True
}

# Dictionary to track which scheme each channel uses
channel_schemes = {
    "aljadeed":     "watchtv.php",
    "mtv_lebanon":  "watchtv.php",
    "lbc_1":        "embed_result_74.php",
    "otv_lb1":      "embed_result_74.php",
    "nbn":          "embed_result_74.php",
#   "manartv1":     "embed_result_74.php",
#   "alittihad":    "embed_result_74.php",
    "almayadeen1":  "embed_result_74.php",
    "teleliban":    "embed_result_74.php",
#    "aljazeer_ar1": "embed_result_74.php"
}

# Class to manage scheme related things such as using encryption or what lookup values to use
class Scheme:
    def __init__(self, ChannelId):
        self.ChannelId = ChannelId
        self.schemeId = channel_schemes.get(ChannelId)
        self.encrypt = scheme_enc_list.get(self.schemeId)

        if self.schemeId == None:
            Error().report("Channel Scheme Type couldn't be found", "channel_schemes.get(ChannelId)", True)

        if self.encrypt == None:
            Error().report("Encryption Scheme Type couldn't be found", "scheme_enc_list.get(ChannelId)", True)


        self.mainReqUrl = "https://elahmad.com/tv/watchtv.php?id=" + self.ChannelId

    def findAesKey(self, response):
        print(f"[INFO]: To find AES in the response the following values are used: [{CRYPT_KEY_BEGIN_LOOKUP}] & [{CRYPT_KEY_BEGIN_LOOKUP}]")
        cryptKeyBeginAdr = response.find(CRYPT_KEY_BEGIN_LOOKUP)+len(CRYPT_KEY_BEGIN_LOOKUP)
        cryptKeyEndAdr = response[cryptKeyBeginAdr:].find(CRYPT_KEY_END_LOOKUP)+cryptKeyBeginAdr
        print(f"[INFO]: To find AES in the response positions are: {cryptKeyBeginAdr} -> {cryptKeyEndAdr}")
        print(f"[INFO]: To find AES in the response area looks like this: {response[cryptKeyBeginAdr-5:cryptKeyEndAdr+5]}")
        
        aesKey = response[cryptKeyBeginAdr:cryptKeyEndAdr]
        
        return aesKey

    def getIndexFatherUrl(self):
        if self.schemeId == "embed_result_74.php?id":
            return "https://elahmad.com/tv/watchtv.php?id=" + self.ChannelId

        if self.encrypt == False :
            return "https://www.elahmad.com/tv/result/embed_result_74.php"
        else:
            return "https://elahmad.com/tv/watchtv.php"

        
    def findRequestParameters(self, response):
        
        paramBeginAdr = response.find(ADA_BEGIN_LOOKUP)+len(ADA_BEGIN_LOOKUP)
        paramEndAdr = response[paramBeginAdr:].find(ADA_END_LOOKUP)+paramBeginAdr
        
        #Parse json line containing Channel key and Channel Value
        dataReqAda = response[paramBeginAdr:paramEndAdr]
        dataReqAdaJson = json.loads(dataReqAda.replace("'", "\""))

        #Parse Channel key and value from json line
        ChannelKey = next(iter(dataReqAdaJson))
        ChannelValue = dataReqAdaJson[ChannelKey]
        
        return { ChannelKey: ChannelValue}
