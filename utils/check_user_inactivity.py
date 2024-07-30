import re
import os

# def UserInactivity():
#     markmap_html_dir = 'C:/Users/Sam/Desktop/gpt_whisper/markmap'
#     for filename in os.listdir(markmap_html_dir):
#         if re.compile(r'^markmap_[A-Za-z0-9]+\.html$').match(filename):
#             os.remove(markmap_html_dir + filename)
#             print(f'已刪除 {filename}')
#         else:
#             pass

def UserInactivity():
    directories = {
        'markmap': 'C:/Users/Sam/Desktop/gpt_whisper/markmap',
        'markmap_png': 'C:/Users/Sam/Desktop/gpt_whisper/markmap_png',
        'audio_log': 'C:/Users/Sam/Desktop/gpt_whisper/audio_log'
    }
    
    patterns = {
        'markmap': re.compile(r'^markmap_[A-Za-z0-9]+$'),
        'markmap_png': re.compile(r'^markmap_screenshot_[A-Za-z0-9]+$'),
        'audio_log': re.compile(r'^audio_log_[A-Za-z0-9]+$')
    }
    
    for dir_name, dir_path in directories.items():
        for filename in os.listdir(dir_path):
            if patterns[dir_name].match(filename):
                os.remove(os.path.join(dir_path, filename))
                print(f'已刪除 {filename} 在 {dir_path}')
            else:
                pass