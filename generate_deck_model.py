import yaml
import argparse
from utils.anki_adapter import AnkiAdapter


def generate(config):
    anki_adapter = AnkiAdapter(url=config["Anki"]["URL"], api_key=config["Anki"]["Key"])

    with open("./template/script.js", 'r', encoding="utf-8") as f:
        script = f'\n<script>{f.read()}</script>'

    with open("./template/style.css", 'r', encoding="utf-8") as f:
        style = f.read()

    if config["Local_Dict_CSS"]:
        with open(config["Local_Dict_CSS"], 'r', encoding="utf-8") as f:
            dict_css = f'<style>{f.read()}</style>\n'
    else:
        print("Local Dict CSS not specified, ignored.")
        dict_css = ""

    deck_name = config["Anki"]["Deck"]
    try:
        anki_adapter.create_deck(deck_name)
        print(f"Succeed in creating deck {deck_name} to Anki.")
    except Exception as e:
        print(f"Error when creating deck {deck_name} to Anki: {repr(e)}")

    model_name = config["Anki"]["Model"]
    fields = [config["Anki"]["Front"], config["Anki"]["Back"]]

    front = "{{" + config["Anki"]["Front"] + "}}"
    back = dict_css + "{{FrontSide}}\n\n<hr id=answer>\n\n{{" + config["Anki"]["Back"] + "}}" + script

    try:
        anki_adapter.create_model(model_name, fields, front, back, style)
        print(f"Succeed in creating model {model_name} to Anki.")
    except Exception as e:
        print(f"Error when creating model {model_name} to Anki: {repr(e)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type=str, default="config.yaml",
                        help='Path of config yaml file, default is config.yaml')
    args = parser.parse_args()

    with open(args.config, 'r', encoding="utf-8") as f:
        config = yaml.safe_load(f)

    generate(config)


if __name__ == "__main__":
    main()
