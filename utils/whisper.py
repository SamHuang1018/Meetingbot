from io import BytesIO
import typing
import asyncio
from datetime import timedelta
from faster_whisper import WhisperModel
# from concurrent.futures import ThreadPoolExecutor


# class Transcriber:
#     _instance = None

#     def __new__(cls, *args, **kwargs):
#         if cls._instance is None:
#             cls._instance = super(Transcriber, cls).__new__(cls)
#         return cls._instance

#     def __init__(self, model_size: str, device: str = "auto", compute_type: str = "default", prompt: str = "使用繁體中文") -> None:
#         super().__init__()
#         self.model_size = model_size
#         self.device = device
#         self.compute_type = compute_type
#         self.prompt = prompt

#     def __enter__(self) -> 'Transcriber':
#         self._model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
#         return self

#     def __exit__(self, exc_type, exc_value, traceback) -> None:
#         pass

#     def format_time(self, seconds):
#         time = str(timedelta(seconds=seconds))
#         if '.' in time:
#             time = time.split('.')[0]
#         return time


#     def __call__(self, audio: bytes) -> typing.Generator[str, None, None]:
#         segments, _ = self._model.transcribe(BytesIO(audio), initial_prompt=self.prompt, vad_filter=False)
#         for segment in segments:
#             text = segment.text
#             start = segment.start
#             end = segment.end

#             if self.prompt in text.strip():
#                 continue
#             if text.strip().replace('.', ''):
#                 verbatim = f"({self.format_time(start)}-{self.format_time(end)}): {text}"
#                 yield verbatim, text



class Transcriber:
    _instance = None

    def __init__(self, model_size: str, device: str = "auto", compute_type: str = "default", prompt: str = "使用繁體中文") -> None:
        if not hasattr(self, '_initialized'):
            self.model_size = model_size
            self.device = device
            self.compute_type = compute_type
            self.prompt = prompt
            self._model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
            self._initialized = True

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Transcriber, cls).__new__(cls)
        return cls._instance

    def format_time(self, seconds):
        time = str(timedelta(seconds=seconds))
        if '.' in time:
            time = time.split('.')[0]
        return time

    def __call__(self, audio: bytes) -> typing.Generator[str, None, None]:
        segments, _ = self._model.transcribe(BytesIO(audio), initial_prompt=self.prompt,vad_filter=False)
        for segment in segments:
            text = segment.text
            start = segment.start
            end = segment.end

            if self.prompt in text.strip():
                continue
            if text.strip().replace('.', ''):
                verbatim = f"({self.format_time(start)}-{self.format_time(end)}): {text}"
                yield verbatim