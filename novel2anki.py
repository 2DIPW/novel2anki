import yaml
from utils import jp_grammar_parser
from utils.dict_parser import MDXDictParser
from utils.anki_adapter import AnkiAdapter
from flask import Flask, send_file
import argparse
import csv
import os
import threading
import re
from tqdm import tqdm
import logging


def count_jp_words(sentence):
    pattern = re.compile(r'[一-龠]|[ぁ-ん]|[ァ-ヴー]')
    matches = pattern.findall(sentence)

    return len(matches)


def about():
    print(r"""
     __               _ ____    _         _    _ 
  /\ \ \_____   _____| |___ \  /_\  _ __ | | _(_)
 /  \/ / _ \ \ / / _ \ | __) |//_\\| '_ \| |/ / |
/ /\  / (_) \ V /  __/ |/ __//  _  \ | | |   <| |
\_\ \/ \___/ \_/ \___|_|_____\_/ \_/_| |_|_|\_\_|
 Anki Card Batch Generator for Visual Novel Text
  Developed by 2DIPW   Licensed under GNU GPLv3
 Open source leads the world to a brighter future!

""")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, default="data.txt",
                        help='Path of input data file, default is data.txt')
    parser.add_argument('-d', '--delimiter', type=str, default="\t",
                        help='Delimiter of input data file, default is \\t')
    parser.add_argument('-v', '--voice_folder', type=str, default="voice/",
                        help='Path of folder contains voice files, default is voice')
    parser.add_argument('-ch', '--character', nargs='+', type=str, default=[],
                        help='Only inputed character names will be processed, separated by spaces, use NULL to represent entries with undefined character name. leave it blank if you want to process all characters.')
    parser.add_argument('-dnv', '--discard_no_voice', action='store_true', default=False,
                        help='Discard entries without voice.')
    parser.add_argument('-c', '--config', type=str, default="config.yaml",
                        help='Path of config yaml file, default is config.yaml')
    args = parser.parse_args()

    characters_include = ["" if item == "NULL" else item for item in list(set(args.character))]

    # 加载配置文件
    with open(args.config, 'r', encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 连接Anki Connect
    anki_adapter = AnkiAdapter(url=config["Anki"]["URL"], api_key=config["Anki"]["Key"])

    if config["Include"]["Sentence_Original"] and config["Include"]["Explanation_For_Word"]:
        dict_parser = MDXDictParser(config["Local_Dict"])  # 加载词典
    else:
        dict_parser = None

    # 启动媒体文件服务器
    if config["Include"]["Voice"]:
        app = Flask(__name__)
        app.logger.setLevel(logging.ERROR)

        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        @app.route('/<filename>', methods=['GET'])
        def provide_file(filename):
            file_path = os.path.join(os.path.abspath(args.voice_folder), filename)
            return send_file(file_path, as_attachment=True)

        def run_flask():
            print(f'Starting media file server on port {config["Anki"]["Media_Server_Port"]} ...')
            app.run(port=config["Anki"]["Media_Server_Port"], debug=False)

        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()

    # 读入数据
    with open(args.input, 'r', encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=args.delimiter)
        rows = list(reader)
        total = len(rows)
        print(f"Input file {args.input} has {total} entries.")

        added_count = 0

        for row in tqdm(rows):
            sentence_ori = row[1]
            sentence_trans = row[2]
            character = row[0]
            voice_name = row[3]

            if characters_include and (character not in characters_include):  # 如果指定了说话人，且当前条目的说话人不在指定中，则跳过
                continue

            if args.discard_no_voice and not voice_name:  # 如果指定了排除无语音，且当前条目无语音，则跳过
                continue

            if not config["Sentence_Length_Limitation"]["Min"] < count_jp_words(sentence_ori) < \
                   config["Sentence_Length_Limitation"]["Max"]:  # 如果句子长度不在限制范围内，则跳过
                continue

            sentence_ori_html = ""
            exp_html = ""
            if config["Include"]["Sentence_Original"]:  # 如果启用语法分析
                for chunk in jp_grammar_parser.parse(sentence_ori):
                    if dict_parser and chunk["part"] in config["Use_Dict_For"]:  # 如果启用词典,且词性在需要使用词典查词的范围内
                        sentence_ori_html += f'<span class="chunk {chunk["part"]} has_exp">{chunk["word"]}</span>'
                        exp = dict_parser.query_dict(chunk["root"])
                        if config["Online_Dict"]:
                            search_link = config["Online_Dict"].replace("%s", chunk["root"])  # 生成在线查词链接
                        exp_html += f'<div id="{chunk["word"]}" class="exp"><a class="search_online" href="{search_link}"></a><span class="word_in_exp">{chunk["root"]}</span> <span class="part_detail">{chunk["part_detail"]}</span><br>{exp}<br></div>'
                    else:
                        sentence_ori_html += f'<span class="chunk {chunk["part"]}">{chunk["word"]}</span>'

            if dict_parser:  # 只有在启用词典时才添加分割线
                exp_html = '<hr class="hr_edge_weak">' + exp_html

            if config["Include"]["Character"] and character:  # 如果启用说话人组分
                character_html = f'<span class="character">{character}</span>'
            else:
                character_html = ""

            if config["Include"]["Sentence_Translated"] and sentence_trans:  # 如果启用译文
                sentence_trans_html = f'<br><span class="sentence_trans">{sentence_trans}</span>'
            else:
                sentence_trans_html = ""

            # 生成卡片背面完整html代码
            back_html = f'<div class="sentence">{character_html}{sentence_ori_html}{sentence_trans_html}</div><div class="exp_group">{exp_html}</div>'

            # 生成字段词典
            fields = {config["Anki"]["Front"]: sentence_ori, config["Anki"]["Back"]: back_html}

            # 准备音频文件
            if config["Include"]["Voice"] and voice_name:
                voice_path = os.path.join(os.path.abspath(args.voice_folder), voice_name)
                if os.path.exists(voice_path):
                    audio = {
                        "url": f'http://127.0.0.1:{config["Anki"]["Media_Server_Port"]}/{voice_name}',
                        "filename": voice_name,
                        "skipHash": False,
                        "fields": [config["Anki"]["Front"]]}
                else:
                    print(f"Voice file {voice_path} for sentence {sentence_ori} not exist, ignored.")
                    audio = None
            else:
                audio = None

            # 准备标签
            tag = []
            if config["Tag"]["Character"]:
                tag.append(character)
            if config["Tag"]["Has_Voice"]:
                tag.append("音声付き" if voice_name else "音声なし")

            # 尝试添加Anki卡片
            try:
                anki_adapter.add_note(config["Anki"]["Deck"], config["Anki"]["Model"], fields, tag, audio,
                                      config["Anki"]["Allow_Duplicate"])
                added_count += 1
            except Exception as e:
                print(f"Error when adding sentence {sentence_ori} to Anki: {repr(e)}")

    print(f"All done! {str(added_count)} cards have been added to Anki.")


if __name__ == "__main__":
    about()
    main()
