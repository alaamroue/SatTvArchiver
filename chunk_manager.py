import os
import subprocess
import shlex
import requests

#ffmpeg
import ffmpeg

from helpers import *

global whisperModelWait
global whisperModelGlobal

def manageChunksThread(savedChunks, surfManager, myTranscriber, options, batchNo):
    chunkManager = ChunkManager()
    chunkManager.manageChunks(savedChunks, surfManager, myTranscriber, options, batchNo)

class ChunkManager:

    def populateOptions(self, options, surfManager):

        self.combineActive = options['combineActive']
        self.transcribeActive = options['transcribeActive']
        self.convertActive = options['convertActive']
        self.combineEvery = options['combineEvery']

        self.outputPath = addSlash(options['outputPath']) + surfManager.channel.id + "/"
        self.outputPathChunks = self.outputPath + "chunks" + "/"

        createOutDir(self.outputPath)
        createOutDir(self.outputPathChunks)

    def manageChunks(self, savedChunks, surfManager, myTranscriber, options, batchNo):
        index = len(savedChunks)
        self.populateOptions(options, surfManager)

        LatestChunk = savedChunks[-1]
        saveAsFilename = extractFileName(surfManager.channel.id, LatestChunk)

        # Download and save the Chunk
        print(f"[INFO] Batch:{batchNo} id:{index} Downloading {saveAsFilename}")
        response = requests.get(LatestChunk)

        with open(self.outputPathChunks + saveAsFilename, 'wb') as f:
            f.write(response.content)
        print(f"[INFO] Batch:{batchNo} id:{index} Downloading {saveAsFilename} Completed")

        # Combine, Transcribe, and Convert
        if (index%self.combineEvery == 0 and index != 0) or self.combineActive == False :

            if(self.combineActive):
                combinedFileName = self.outputPath + removeExtension(saveAsFilename) + "c" + getExtension(saveAsFilename)
                combinedFileNameMp4 = self.outputPath + removeExtension(saveAsFilename) + "c.mp4"

                print(f"[INFO] Batch:{batchNo} id:{index} Combing multiple chunks into a bigger chunk: {combinedFileName}...")
                with open(combinedFileName, 'wb') as combinedFile:
                    for savedChunk in savedChunks:
                        chunkName = extractFileName(surfManager.channel.id, savedChunk)
                        chunkPath = self.outputPathChunks + chunkName
                        with open(chunkPath, 'rb') as file:
                            combinedFile.write(file.read())
                        print(f"[INFO] Batch:{batchNo} removing: " + chunkName)
                        os.remove(chunkPath)
            else:
                combinedFileName = self.outputPath + saveAsFilename

            if(self.transcribeActive):
                print(f"[INFO] Batch:{batchNo} id:{index} Transcribing the file: {combinedFileName}...")
                myTranscriber.transcribe(combinedFileName, self.outputPath)

            if(self.convertActive):
                print(f"[INFO] Batch:{batchNo} id:{index} Converting to chunks into mp4: {combinedFileNameMp4}...")
                #Equivelant to: ffmpeg -i {combinedFileName} -vcodec libx265 -crf 28 {combinedFileNameMp4}
                ffmpeg.input(combinedFileName).output(combinedFileNameMp4, vcodec='libx265').run(quiet=True)
                os.remove(combinedFileName)

            print(f"[INFO] Batch:{batchNo} id:{index} Batch has finished...")