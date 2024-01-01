from helpers import *
from scheme import channel_schemes
from surf_manager import SurfManager
from chunk_manager import *
from transcribe_model import TranscribeModel

import argparse
import time
import threading

def main():

    parser = argparse.ArgumentParser(description='Download a stream of a TV channel from the elahmad.com website. The script can also transcribed and compress the stream for archival purposes.')
    parser.formatter_class = lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=25)

    channel_ids = list(channel_schemes.keys())

    requiredNamed = parser.add_argument_group('Required Arguments')
    requiredNamed.add_argument('-i', '--channel', choices=channel_ids, required=True, help='Specify the channel id to stream. Allowed values are '+', '.join(channel_ids), metavar='')
    
    parser._optionals.title = 'Optional Arguments'
    parser.add_argument('-c', '--combine', action='store_true', help='Combine the short clips into longer ones (recommended)')
    parser.add_argument('-t', '--transcribe', action='store_true', help='Turn on stream transcription (Speech to Text)')
    parser.add_argument('-z', '--compress', action='store_true', help='Turn on video compress (recommended)')
    parser.add_argument('-o', '--output', default='output', help='Path to output file', metavar='')
    parser.add_argument('-n', '--combine_every', type=int, default=30, help='Every x clips are combined together into a longer one', metavar='')

    args = parser.parse_args()

    channelId = args.channel
    options = {
        'combineActive': args.combine,     
        'transcribeActive': args.transcribe,
        'convertActive': args.compress,
        'outputPath': args.output,
        'combineEvery': args.combine_every,
        'whisperModelSize': "small",
        'whisperLang': "ar",
        'whisperDevice': "cuda",
        'vtt-output': False
    }
    # Initializations
    LastChunkDownloaded = ""
    savedChunksList = []

    # Setting up the Transcriber
    myTranscriber = TranscribeModel(options)

    # Setting up the surf Manager
    mySurfManager = SurfManager(channelId)
    mySurfManager.chunkList = mySurfManager.grabChunkListUrl()

    # Main script loop where the refresh takes place
    print("[INFO] Main Loop Started...")
    batchNo = 0
    while(True):

        #Grab links to newest video chunk
        latestChunks = mySurfManager.getChunkList()
        latestChunk = latestChunks[-1]

        #Download chunk if it is new
        if (latestChunk != LastChunkDownloaded):
            #create a thread and download in it
            savedChunksList.append(latestChunk)
            threading.Thread(target=manageChunksThread, args=(savedChunksList,mySurfManager,myTranscriber,options,batchNo,), name='manageChunksThread').start()
            LastChunkDownloaded = latestChunk 
            
        # Combine clips and convert to mp4 and use speech recognition
        if (len(savedChunksList)%options['combineEvery'] == 0 and len(savedChunksList) != 0):
            savedChunksList=[]
            batchNo = batchNo + 1
        
        if options['combineActive'] == False:
            savedChunksList=[]
            batchNo = 0

        time.sleep(0.5)

if __name__ == "__main__":
    main()