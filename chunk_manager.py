import os
import subprocess
import shlex
import requests

from helpers import *


def manageChunksThread(savedChunks, surfManager, options):
    chunkManager = ChunkManager()
    chunkManager.manageChunks(savedChunks, surfManager, options)

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

        
    def manageChunks(self, savedChunks, surfManager, options):
        self.populateOptions(options, surfManager)

        LatestChunk = savedChunks[-1]
        saveAsFilename = extractFileName(surfManager.channel.id, LatestChunk)

        # Download and save the Chunk
        print(f"[INFO] Downloading {saveAsFilename}")
        response = requests.get(LatestChunk)

        with open(self.outputPathChunks + saveAsFilename, 'wb') as f:
            f.write(response.content)

        # Combine, Transcribe, and Convert
        if (len(savedChunks)%self.combineEvery == 0 and len(savedChunks) != 0) or self.combineActive == False :

            if(self.combineActive):
                combinedFileName = self.outputPath + removeExtension(saveAsFilename) + "c" + getExtension(saveAsFilename)
                combinedFileNameMp4 = self.outputPath + removeExtension(saveAsFilename) + "c.mp4"

                print(f"[INFO] Combing multiple chunks into a bigger chunk: {combinedFileName}...")
                with open(combinedFileName, 'wb') as combinedFile:
                    for savedChunk in savedChunks:
                        chunkName = extractFileName(surfManager.channel.id, savedChunk)
                        chunkPath = self.outputPathChunks + chunkName
                        with open(chunkPath, 'rb') as file:
                            combinedFile.write(file.read())
                        print("[INFO] removing: " + chunkName)
                        os.remove(chunkPath)
            else:
                combinedFileName = self.outputPath + saveAsFilename

            if(self.transcribeActive):
                print(f"[INFO] Transcribing the file: {combinedFileName}...")
                command_string = f"whisper {combinedFileName} --language Arabic --model small --output_dir {self.outputPath}"
                subprocess.run(shlex.split(command_string), capture_output = False, text = False)

            if(self.convertActive):
                print(f"[INFO] Converting to chunks into mp4: {combinedFileNameMp4}...")
                command_string = f"ffmpeg -i {combinedFileName} -vcodec libx265 -crf 28 {combinedFileNameMp4}"
                subprocess.run(shlex.split(command_string), capture_output = False, text = False)
                os.remove(combinedFileNameMp4)

            print(f"[INFO] Batch has finished...")