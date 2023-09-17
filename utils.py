import logging

def log_error(error_message):
    logging.error(error_message)

def log_info(info_message):
    logging.info(info_message)
def translator(text):
    text = text.replace(',','')
    if '億' in text:
        text = float(text.replace('億',''))*100000000
    elif '千萬' in text:
        text = float(text.replace('千萬',''))*10000000
    elif '百萬' in text:
        text = float(text.replace('百萬',''))*1000000
    elif '萬' in text:
        text = float(text.replace('萬',''))*10000
    return text