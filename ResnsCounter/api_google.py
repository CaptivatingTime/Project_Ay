import os
from google.cloud import translate_v2 as translate

def translateMsg(msg):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/ZK00138/source/repos/ResnsCounter/ResnsCounter/API/velvety-mason-383416-af8ad8fa3a59.json'
    translate_client = translate.Client()

    # Detect the language of the input message
    detected_language = translate_client.detect_language(msg)['language']

    # Check if the detected language is English
    if detected_language == 'en':
        # Return the input message without translation
        return msg
    else:
        result = translate_client.translate(msg, source_language='lv', target_language='en')
        msg_en = result['translatedText']
        return msg_en
