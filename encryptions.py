from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

import base64

DEFAULT_IV = "www.elahmad.net/"

#Perform Aes Decrpytion
def decryptAes(message, key, iv = DEFAULT_IV):
    key = key.encode('utf-8')
    iv = iv.encode('utf-8')
    message = base64.b64decode(message)
    
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    decrypted_data = unpad(cipher.decrypt(message), AES.block_size)
    return decrypted_data.decode('utf-8')