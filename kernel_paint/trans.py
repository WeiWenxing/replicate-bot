from googletrans import Translator
import re
import xml.etree.ElementTree as ET
import logging


def translate_file(input_file, output_file, dest_lang='zh-CN'):
    translator = Translator(service_urls=['translate.google.com'])

    with open(input_file, 'r', encoding='utf-8') as file:
        text = file.read()

    translation = translator.translate(text, dest=dest_lang)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(translation.text)

    return output_file


def translate_xml(input_file, output_file, dest_lang='zh-CN'):
    translator = Translator(service_urls=['translate.google.com'])

    with open(input_file, 'r', encoding='utf-8') as file:
        xml_text = file.read()

    # translated_text = re.sub(r'<string name="(.*?)">(.*?)</string>', lambda match: f'<string name="{match.group(1)}">{translator.translate(match.group(2), dest="{dest_lang}").text}</string>', xml_text)
    # translated_text = re.sub(
    #     r'<string name="(.*?)">(.*?)</string>',
    #     lambda match: f'<string name="{match.group(1)}">{translator.translate(match.group(2), dest="zh-CN").text}</string>',
    #     xml_text
    # )

    root = ET.fromstring(xml_text)
    text_dict = {}
    for string_elem in root.iter('string'):
        text = string_elem.text
        text_dict[text] = None

    texts = list(text_dict.keys())
    # logging.info(texts)
    txt = '\n\n'.join(texts)
    translation = translator.translate(txt, dest=dest_lang)
    translated_txts = translation.text.split('\n\n')
    # logging.info(translated_txts)

    # 将翻译结果更新到字典中
    for translation, text in zip(translated_txts, text_dict.keys()):
        text_dict[text] = translation

    # 遍历<string>元素，更新文本内容
    for string_elem in root.iter('string'):
        text = string_elem.text
        translated_text = text_dict[text]
        string_elem.text = translated_text

    # 将修改后的XML转换为字符串
    translated_xml = ET.tostring(root, encoding='utf-8').decode('utf-8')
    xml_header = r'<?xml version="1.0" encoding="utf-8"?>'
    translated_xml = f'{xml_header}\n{translated_xml}'

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(translated_xml)

    return output_file



