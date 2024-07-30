import os
import ffmpeg
import time
import opencc
import re
import logging
from logging.handlers import RotatingFileHandler
from logging import StreamHandler
from typing import List, Union
import requests
import pyimgur
import librosa
import pandas as pd
from firebase import firebase
from openai import OpenAI
from linebot import LineBotApi
from linebot.models import TextSendMessage
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.config import *
from utils.whisper import Transcriber
from schema_and_template.template import *
from schema_and_template.markmap_html import generate_html


class MeetingBot_Utils:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.log_file_path = home_dir + f'/audio_log/audio_log_{user_id}.log'
        self.home_dir = home_dir
        self.openai_api_key = openai_api_key
        self.gemini_api_key = gemini_api_key
        self.google_search_api = google_search_api
        self.search_engine_id = search_engine_id
        self.channel_access_token = channel_access_token
        self.model_name = model_name
        # self.ffmpeg = ffmpeg
        # self.fetch_data_url = fetch_data_url
        self.firebase_url = firebase_url
        self.firebase_db = firebase.FirebaseApplication(self.firebase_url, None)
        self.transcriber = Transcriber(model_size, device, compute_type, prompt)
        self.client = OpenAI(api_key=self.openai_api_key)
        self.model_name = model_name
        self.top_p = top_p
        self.temperature = temperature
        # self.markmap_download_dir = markmap_download_dir
        # self.markmap_html_url = markmap_html_url
        self.individual_markmap_html = home_dir + f'/markmap/markmap_{self.user_id}.html'
        self.individual_markmap_screenshot = f'markmap_png/markmap_screenshot_{self.user_id}.png'
        self.ensure_directories_exist('line_whisper.ipynb', ['./audio', './audio_log', './markmap_png', './pptx'])
        
    def ensure_directories_exist(self, base_script: str, sub_dirs: List[str]) -> None:
        """
        確認audio、audio_log、markmap_png、pptx等是否存在資料夾，若不存在就各別建立
        
        參數
        base_script: 用於確定腳本目錄。
        sub_dirs: 子目錄名稱列表。
        """

        script_dir = os.path.dirname(os.path.abspath(base_script))
        directories = [os.path.join(script_dir, sub_dir) for sub_dir in sub_dirs]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print('資料夾不存在，創建資料夾')
            else:
                pass        
        
    def get_logger(self) -> logging.Logger:
        """
        建立Logger，若logger未有handlers，加入 RotatingFileHandler和StreamHandler
        """
        
        log_file_path = self.log_file_path
        logger = logging.getLogger(f'user_logger_{self.user_id}')
        if not logger.handlers:
            rotating_handler = RotatingFileHandler(log_file_path, mode='a', maxBytes=10485760, backupCount=5, encoding='utf-8')
            rotating_handler.setLevel(logging.INFO)
            rotating_handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(levelname)s : %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p'))        
            stream_handler = StreamHandler()
            stream_handler.setLevel(logging.INFO)
            stream_handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(levelname)s : %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p'))
            logger.addHandler(rotating_handler)
            logger.addHandler(stream_handler)
            logger.setLevel(logging.INFO)
        else:
            pass
        return logger

    def extract_image_url(self, url: str) -> str:
        """
        提取圖片網址
        
        參數
        url: 圖片連結
        """
        
        if isinstance(url, list) and len(url) > 0:
            return url[0]['src']
        else:
            pass
        return '無'
    
    def fetch_search_results(self, query: str, total_results: int = 10, num: int = 10, date_restrict: str = '') -> str:
        """
        利用關鍵字搜尋google
        
        參數
        query: 關鍵字
        total_results: 抓取總筆數
        num: 一次抓取筆數
        date_restrict: 抓取日期區間
        """
        
        items = []
        pages = total_results // num
        reminder = total_results % num
        
        for i in range(pages + (1 if reminder > 0 else 0)):
            start = (i * num) + 1
            payload = {
                        'key': self.gemini_api_key,
                        'q': query,
                        'cx': self.search_engine_id,
                        'start': start,
                        'num': num if (i < pages) else reminder,
                        'dateRestrict': date_restrict
                    }
            response = requests.get(self.google_search, params=payload)
            if 200 <= response.status_code < 400:
                items.extend(response.json().get('items', []))
            else:
                raise Exception(f'錯誤: {response.status_code}, {response.text}')

        df = pd.json_normalize(items)[['title', 'snippet', 'link', 'formattedUrl', 'pagemap.cse_image']]
        df['pagemap.cse_image'] = df['pagemap.cse_image'].apply(self.extract_image_url)
        df = df.fillna('無').to_dict('records')
        covert_data = [dict(item) for item in df]
        transfer_data = [', '.join([f'{key}: {value}' for key, value in item.items()]) for item in covert_data]
        api_messages = [{'role': 'assistant', 'content': item} for item in transfer_data]
        messages = [{'role': 'system', 'content': fetch_search_results_template}]
        messages.extend(api_messages)
        response = self.client.chat.completions.create(model=self.model_name, temperature=self.temperature, top_p=self.top_p, messages=messages)
        return response.choices[0].message.content

    def get_audio_duration(self, file_path: str) -> float:
        """
        計算音檔長度
        
        參數
        file_path: 檔案位置
        """
        
        audio_data, sample_rate = librosa.load(file_path, sr=None)
        duration = librosa.get_duration(y=audio_data, sr=sample_rate) 
        return duration

    # def compress_audio(self, input_file: str, output_file: str, logger: logging.Logger, bitrate: str = "32k") -> None:
    #     """
    #     壓縮音檔
        
    #     參數
    #     input_file: 放入的檔案
    #     output_file: 輸出的檔案
    #     bitrate: 位元率
    #     """
        
    #     command = [
    #                 self.ffmpeg, 
    #                 '-i', input_file,
    #                 '-b:a', bitrate,
    #                 '-threads', '4',
    #                 output_file
    #             ]
    #     result = subprocess.run(command, capture_output=True, text=True)
    #     logger.info(f"命令提示字元: {' '.join(command)}")
    #     logger.info(f'輸出: {result.stderr}')
    #     if result.returncode == 0:
    #         logger.info(f'{self.user_id}的音檔成功壓縮檔案並存至 {output_file}')
    #     else:
    #         logger.info(f'{self.user_id}的音檔壓縮失敗')

    def process_file(self, file_path: str, file, logger: logging.Logger) -> None:
        """
        由上傳檔案來處理音檔(超過40MB會先壓縮再將語音轉譯成文字)
        
        參數
        file_path: 檔案位置
        file: 檔案名稱
        """
        
        original_file_size = os.path.getsize(file_path)
        logger.info(f'檔案大小: {original_file_size} bytes')

        if original_file_size > 40 * 1024 * 1024:
            logger.info(f'檔案超過40MB，直接進行壓縮')
            # compressed_file_path = os.path.join('./audio', f'{self.user_id}_compressed_{file.filename}')
            compressed_file_path =  self.home_dir + f'/audio/{self.user_id}_compressed_{file.filename}'
            ffmpeg.input(file_path).output(compressed_file_path, audio_bitrate='32k').run()
            # self.compress_audio(file_path, compressed_file_path, logger)
            file_path_to_upload = compressed_file_path
            logger.info(f'{self.user_id} 音檔壓縮成功')
        else:
            logger.info(f'檔案小於40MB，無須壓縮')
            file_path_to_upload = file_path

        logger.info('音檔轉譯文字中...')
        with open(file_path_to_upload, 'rb') as audio_file:
            audio_bytes = audio_file.read()
        transcriptions = [seg for seg in self.transcriber(audio_bytes)]
        verbatim = ''.join([item for item in transcriptions])
        text = '，'.join([item.split(': ')[1] for item in transcriptions])
        logger.info('轉譯成功')
        # response = requests.post(self.fetch_data_url, files={'file': open(file_path_to_upload, 'rb')})
        # if 200 <= response.status_code < 300:
        #     logger.info('轉譯成功')
        # else:
        #     logger.info('轉譯失敗')
        self.firebase_db.put('/verbatim', self.user_id, verbatim)
        self.firebase_db.put('/content', self.user_id, text)
        
        LineBotApi(self.channel_access_token).push_message(self.user_id, TextSendMessage(text='音檔已處理完畢，請點選以下選單進行後續操作。'))

    # def process_file(file_path, file, user_id):
    #     import time
    #     import datetime
    #     import pandas as pd
    #     from pyannote.audio import Pipeline
    #     from pyannote.core import Segment
    #     import torch
    #     from whisper import Transcriber    

    #     def split_time_segment(row):
    #         time_segment = row.split(': ')[0]
    #         start, end = time_segment.strip('()').split('-')
    #         return start, end

    #     def time_str_to_float(time_str):
    #         x = datetime.datetime.strptime(time_str, '%H:%M:%S')
    #         return x.hour * 3600 + x.minute * 60 + x.second

    #     def format_time(seconds):
    #         td = datetime.timedelta(seconds=seconds)

    #         return str(td)
            
    #     start_time = time.time()
    #     print(f'開始時間：{start_time:.2f} 秒')        
            
    #     pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token="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")
    #     pipeline = pipeline.to(torch.device('cuda'))     
            
    #     logger = get_logger(user_id)
    #     original_file_size = os.path.getsize(file_path)
    #     logger.info(f'檔案大小: {original_file_size} bytes')

    #     if original_file_size > 40 * 1024 * 1024:
    #         logger.info(f'檔案超過40MB，直接進行壓縮')
    #         compressed_file_path = os.path.join('C:/Users/Sam/Desktop/gpt_whisper/audio', f'{user_id}_compressed_{file.filename}')
    #         compress_audio(file_path, compressed_file_path, user_id, logger)
    #         file_path_to_upload = compressed_file_path
    #     else:
    #         file_path_to_upload = file_path

    #     logger.info(f'音檔轉譯文字中...')
        
    #     diarization_result = pipeline(file_path)   
    #     print('完成腳色辨識')
        
    #     fetch_data_url = 'http://127.0.0.1:8080/audio/transcriptions'
    #     response = requests.post(fetch_data_url, files={'file': open(file_path_to_upload, 'rb')})
    #     verbatim = response.json()['verbatim']
    #     text = response.json()['text']
        
    #     print('完成逐字稿')
    #     df = pd.DataFrame(verbatim, columns=['raw', 'text'])
    #     df['start'], df['end'] = zip(*df['raw'].apply(split_time_segment))
    #     df['text'] = df['raw'].apply(lambda x: x.split(': ')[1])
    #     df = df.drop(columns=['raw'])

    #     combined_results = []

    #     for _, row in df.iterrows():
    #         start_float = time_str_to_float(row['start'])
    #         end_float = time_str_to_float(row['end'])
    #         segment = Segment(start_float, end_float)
    #         for turn, _, spk in diarization_result.itertracks(yield_label=True):
    #             if segment.intersects(turn):
    #                 speaker = spk
    #                 break
    #         combined_results.append(f"{speaker} ({format_time(start_float)}-{format_time(end_float)}): {row['text']}")    
        
    #     firebase_db.put('/verbatim', user_id, verbatim)
    #     firebase_db.put('/content', user_id, text)

    #     compute_time = time.time() - start_time
    #     print(f'回覆時間：{compute_time:.2f} 秒')    
        
    #     LineBotApi(channel_access_token).push_message(user_id, TextSendMessage(text='音檔已處理完畢，請點選以下選單進行後續操作。'))   
    
    def process_audio(self, id: str, logger: logging.Logger, check_transcoding: bool = False) -> None:
        """
        由上傳檔案來處理音檔(超過40MB會先壓縮再將語音轉譯成文字)
        
        參數
        id: line的個人識別ID(下載檔案專用)
        check_transcoding: 下載音檔前要先確定類別，如果是訊息類別是audio就要用transcoding，如果訊息種類是file就用content
        """
        
        headers = {'Authorization': f'Bearer {channel_access_token}'}
        
        if check_transcoding:
            while True:
                initial_url = f'https://api-data.line.me/v2/bot/message/{id}/content/transcoding'
                response = requests.get(initial_url, headers=headers)
                status = response.json().get('status')
                if status == 'succeeded':
                    logger.info(f'{self.user_id} 下載音檔成功')
                    break
                elif status == 'failed':
                    logger.info(f'{self.user_id} 下載音檔失敗')
                    return
                elif status == 'processing':
                    logger.info(f'{self.user_id}正在處理中，請稍後...')
                    time.sleep(5)
                else:
                    pass
        else:
            logger.info(f'{self.user_id} 無需檢查轉碼，直接下載音檔')
        
        audio_content_url = f'https://api-data.line.me/v2/bot/message/{id}/content'
        audio_response = requests.get(audio_content_url, headers=headers)
        if 200 <= audio_response.status_code < 400:
            logger.info(f'{self.user_id} 音檔無錯誤')
        else:
            raise Exception(f'錯誤: {audio_response.status_code}, {audio_response.text}')
        
        audio_path = self.home_dir + f'/audio/{self.user_id}_audio.mp3'
        with open(audio_path, 'wb') as audio_file:
            audio_file.write(audio_response.content)
            logger.info(f'{self.user_id} 音檔已儲存')
            original_file_size = os.path.getsize(audio_path)
            logger.info(f'檔案大小: {original_file_size} bytes')
            
            audio_duration = self.get_audio_duration(audio_path)
            estimated_time = round((audio_duration / 3600) * 8)
            logger.info(f'音檔長度：{estimated_time} 分鐘')
            
            LineBotApi(channel_access_token).push_message(self.user_id, TextSendMessage(text=f'音檔已下載完畢，預計處理時間約 {estimated_time} 分鐘。'))
            
        if original_file_size > 40 * 1024 * 1024:
            logger.info(f'{self.user_id} 開始進行音檔壓縮')
            compressed_audio_path = self.home_dir + f'/audio/{self.user_id}_audio_compressed.mp3'
            ffmpeg.input(audio_path).output(compressed_audio_path, audio_bitrate='32k').run()
            # self.compress_audio(audio_path, compressed_audio_path, logger)
            audio_path = compressed_audio_path
            logger.info(f'{self.user_id} 音檔壓縮成功')
        else:
            logger.info(f'{self.user_id} 音檔無須壓縮')
           
        logger.info('音檔轉譯文字中...')
        with open(audio_path, 'rb') as audio_file:
            audio_bytes = audio_file.read()
        transcriptions = [seg for seg in self.transcriber(audio_bytes)]
        verbatim = ''.join([item for item in transcriptions])
        text = '，'.join([item.split(': ')[1] for item in transcriptions])
        logger.info('轉譯成功')
        # response = requests.post(self.fetch_data_url, files={'file': open(audio_path, 'rb')})
        # if 200 <= response.status_code < 300:
        #     logger.info('轉譯成功')
        # else:
        #     raise ConnectionError('轉譯失敗')
        self.firebase_db.put('/verbatim', self.user_id, verbatim)
        self.firebase_db.put('/content', self.user_id, text)
        
        LineBotApi(self.channel_access_token).push_message(self.user_id, TextSendMessage(text='音檔已處理完畢，請點選以下選單進行後續操作。'))

    def format_conversation(self, text: str) -> str:
        """
        匹配逐字稿格式
        
        參數
        text: 逐字稿
        """
        
        pattern = r'\((\d+:\d+:\d+-\d+:\d+:\d+)\):\s*(.*?)\s*(?=\(\d+:\d+:\d+-\d+:\d+:\d+\)|$)'
        matches = re.findall(pattern, text)
        
        formatted_text = ""
        for timestamp, content in matches:
            formatted_text += f"({timestamp}): {content}\n"
        
        return formatted_text.strip()
        
    def split_text_by_length(self, text: str, max_length: int) -> List[str]:
        """
        超過5000字的限制，必須分段切
        
        參數
        text: 所有內容
        max_length: 最大長度
        """
        
        segments = []
        while len(text) > max_length:
            split_point = text.rfind('\n', 0, max_length)
            if split_point == -1:
                split_point = max_length
            segments.append(text[:split_point].strip())
            text = text[split_point:].strip()
        segments.append(text.strip())
        
        return segments

    def gpt_generate(self, line_prompt: str, logger: logging.Logger) -> Union[str, None]:
        """
        將轉譯的文字透過GPT生成會議摘要、逐字稿、相關建議
        
        參數
        line_prompt: line的按鈕
        """
        
        logger.info(f'{self.user_id} 將轉譯文字再進GPT潤飾({line_prompt})')
        revise_content = opencc.OpenCC('s2t')
        
        if line_prompt == '會議摘要':
            origin_content = self.firebase_db.get('/content', self.user_id)
            if not origin_content:
                LineBotApi(channel_access_token).push_message(self.user_id, TextSendMessage(text='請先輸入語音訊息或上傳檔案'))
                return
            else:
                messages = [
                    {'role': 'system', 'content': meeting_summary_prompt_template_v3},
                    {'role': 'assistant', 'content': revise_content.convert(origin_content)}]
                response = self.client.chat.completions.create(model=self.model_name, temperature=self.temperature, top_p=self.top_p, messages=messages)
                
                return response.choices[0].message.content
            
        elif line_prompt == '逐字稿':
            origin_verbatim = self.firebase_db.get('/verbatim', self.user_id)
            origin_verbatim = self.format_conversation(origin_verbatim)
            if not origin_verbatim:
                LineBotApi(channel_access_token).push_message(self.user_id, TextSendMessage(text='請先輸入語音訊息或上傳檔案'))
                return
            else:
                messages = [{'role': 'system', 'content': meeting_verbatim_prompt_template_v1},
                            {'role': 'assistant', 'content': revise_content.convert(origin_verbatim)}]
                response = self.client.chat.completions.create(model=self.model_name, temperature=self.temperature, top_p=self.top_p, messages=messages)
                final_report = f'{response.choices[0].message.content}\n\n 5. **逐字稿完整如下**:\n\n{revise_content.convert(origin_verbatim)}'
                
                return final_report
                
        elif line_prompt == '相關建議':
            origin_content = self.firebase_db.get('/content', self.user_id)
            if not origin_content:
                LineBotApi(channel_access_token).push_message(self.user_id, TextSendMessage(text='請先輸入語音訊息或上傳檔案'))
                return
            
            messages = [
                {'role': 'system', 'content': relevant_suggestion_prompt_template},
                {'role': 'assistant', 'content': revise_content.convert(origin_content)}]
            response = self.client.chat.completions.create(model=self.model_name, temperature=self.temperature, top_p=self.top_p, messages=messages)

            return response.choices[0].message.content

    # def markmap_html(self, content: str, logger: logging.Logger) -> None:
    #     """
    #     生成心智圖(透過selenium在markmap渲染完後再下載html)
        
    #     參數
    #     content: 生成內容
    #     """
        
    #     original_file = os.path.join(self.markmap_download_dir, 'markmap.html')
    #     if os.path.exists(original_file):
    #         os.remove(original_file)
    #     else:
    #         pass
    #     driver = webdriver.Chrome()
    #     wait = WebDriverWait(driver, 10)
    #     driver.get(self.markmap_html_url)        
        
    #     text_area = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.CodeMirror')))
    #     text_area.click()
    #     driver.execute_script('document.querySelector(".CodeMirror").CodeMirror.setValue("")')
    #     driver.execute_script(f'document.querySelector(".CodeMirror").CodeMirror.setValue(`{content}`)')
    #     time.sleep(5)
        
    #     download_button = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'Download as interactive HTML')))
    #     download_button.click()
    #     time.sleep(5)
    #     driver.quit()
        
    #     new_file = os.path.join(self.markmap_download_dir, f'markmap_{self.user_id}.html')
    #     if os.path.exists(new_file):
    #         os.remove(new_file)
    #     else:
    #         pass
    #     if os.path.exists(original_file):
    #         os.rename(original_file, new_file)
    #         logger.info(f'檔案已改名為: {new_file}')
    #     else:
    #         logger.info('沒找到檔案，重新查看下載狀況')

    # def markmap_to_png(self) -> str:
    #     """
    #     將心智圖轉成圖片(透過selenium再截圖成圖片)
    #     """

    #     chrome_options = Options()
    #     chrome_options.add_argument('--headless')
    #     chrome_options.add_argument('--disable-gpu')
    #     chrome_options.add_argument('--no-sandbox')
    #     chrome_options.add_argument('--disable-dev-shm-usage')
    #     driver = webdriver.Chrome(options=chrome_options)
    #     driver.get(self.individual_markmap_html)
    #     time.sleep(2)
    #     driver.save_screenshot(self.individual_markmap_screenshot)
    #     driver.quit()
    #     im = pyimgur.Imgur('c95bec1bd4f157c')
    #     upload_image = im.upload_image(self.individual_markmap_screenshot, title='上傳圖片')
        
    #     return upload_image.link
    
    def markmap_to_png(self, content) -> str:
        """
        將心智圖先透過html渲染後轉成圖片(透過selenium再截圖成圖片)
        
        參數
        content: 會議摘要
        """

        html_content = generate_html(content)
        with open(self.individual_markmap_html, 'w', encoding='utf-8') as file:
            file.write(html_content)

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(self.individual_markmap_html)
        script_element = driver.find_element(By.XPATH, "//script[@type='text/template']")
        driver.execute_script("arguments[0].textContent = arguments[1];", script_element, content)
        time.sleep(2)
        driver.save_screenshot(self.individual_markmap_screenshot)
        driver.quit()
        im = pyimgur.Imgur('c95bec1bd4f157c')
        upload_image = im.upload_image(self.individual_markmap_screenshot, title='上傳圖片')
        
        return upload_image.link