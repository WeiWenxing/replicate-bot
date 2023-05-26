from googletrans import Translator


def translate_file(input_file, output_file, dest_lang='zh-CN'):
    # 创建 Translator 对象
    translator = Translator(service_urls=['translate.google.com'])

    # 打开输入文件并读取文本内容
    with open(input_file, 'r', encoding='utf-8') as file:
        text = file.read()

    # 翻译文本
    translation = translator.translate(text, dest=dest_lang)

    # 将翻译结果写入输出文件
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(translation.text)

    return output_file

# 示例用法
# input_file = 'input.txt'  # 输入文件路径
# output_file = 'output.txt'  # 输出文件路径
# dest_lang = 'zh-CN'  # 目标语言，默认为中文简体
#
# translate_file(input_file, output_file, dest_lang)

