import whisper
from whisper.utils import get_writer
import soundfile as sf
import torch

class TranscribeModel:
    def __init__(self, options):
        
        if options['transcribeActive'] == True:
            self.language = options['whisperLang']
            self.modelSize = options['whisperModelSize']
            self.device = options['whisperDevice']
            self.vtt = options['vtt-output']

            self.model = self.setupWhispherModel()
        else:
            print(f"[INFO] No transcribe model loaded to memory")

    def setupWhispherModel(self):
        # Load model to memory
        print(f"[INFO] Transcribe model (Whisper) is loading to memory with Lang:{self.language} size:{self.modelSize} device:{self.device}")
        torch.cuda.init()
        model = whisper.load_model(self.modelSize).to(self.device)
        return model

    def transcribe(self, inputFile, outputFile):
        # Transcribe
        result = self.model.transcribe(inputFile, language=self.language, fp16=False)

        # Save as an SRT file
        srt_writer = get_writer("srt", outputFile)
        srt_writer(result, inputFile)

        if(self.vtt):
            # Save as a VTT file
            vtt_writer = get_writer("vtt", outputFile)
            vtt_writer(result, inputFile)
    
