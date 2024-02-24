import json
import requests


class AnkiAdapter:
    def __init__(self, url, api_key=None, timeout=10):
        self.api_url = url
        self.api_key = api_key
        self.timeout = timeout
        request_permission_request = {"action": "requestPermission", "version": 6}
        response = requests.post(self.api_url, json=request_permission_request, timeout=self.timeout)
        response.raise_for_status()
        result = json.loads(response.text)
        if result["result"]["permission"] == "denied":
            raise ConnectionRefusedError("Anki Connect permission denied.")
        self.require_api_key = result["result"]["requireApikey"]

    def _add_api_key_param(self, ori):
        if self.require_api_key:
            ori["key"] = self.api_key
        return ori

    def add_note(self, deck_name, model_name, fields, tags, audio, allow_duplicate=False):
        note_data = {
            "deckName": deck_name,
            "modelName": model_name,
            "fields": fields,
            "options": {
                "allowDuplicate": allow_duplicate
            },
            "tags": tags,
            "audio": [audio],
        }

        request = {
            "action": "addNote",
            "version": 6,
            "params": {
                "note": note_data
            }
        }
        response = requests.post(self.api_url, json=self._add_api_key_param(request), timeout=self.timeout)
        response.raise_for_status()
        result = json.loads(response.text)

        if result["error"]:
            raise RuntimeError(result["error"])

        return result["result"]

    def model_names(self):
        request = {"action": "modelNames", "version": 6}
        response = requests.post(self.api_url, json=self._add_api_key_param(request), timeout=self.timeout)
        response.raise_for_status()
        result = json.loads(response.text)

        if result["error"]:
            raise RuntimeError(result["error"])

        return result["result"]

    def deck_names(self):
        request = {"action": "deckNames", "version": 6}
        response = requests.post(self.api_url, json=self._add_api_key_param(request), timeout=self.timeout)
        response.raise_for_status()
        result = json.loads(response.text)

        if result["error"]:
            raise RuntimeError(result["error"])

        return result["result"]

    def model_field_names(self, model_name):
        request = {"action": "modelFieldNames", "version": 6, "params": {"modelName": model_name}}
        response = requests.post(self.api_url, json=self._add_api_key_param(request), timeout=self.timeout)
        response.raise_for_status()
        result = json.loads(response.text)

        if result["error"]:
            raise RuntimeError(result["error"])

        return result["result"]

    def create_deck(self, deck):
        request = {"action": "createDeck", "version": 6, "params": {"deck": deck}}
        response = requests.post(self.api_url, json=self._add_api_key_param(request), timeout=self.timeout)
        response.raise_for_status()
        result = json.loads(response.text)

        if result["error"]:
            raise RuntimeError(result["error"])

        return result["result"]

    def create_model(self, model_name, fields, front, back, css=None, is_cloze=False):
        card_templates = {
            "Front": front,
            "Back": back
            }

        request = {
                "action": "createModel",
                "version": 6,
                "params": {
                    "modelName": model_name,
                    "inOrderFields": fields,
                    "css": css,
                    "isCloze": is_cloze,
                    "cardTemplates": [card_templates]
                }
            }

        response = requests.post(self.api_url, json=self._add_api_key_param(request), timeout=self.timeout)
        response.raise_for_status()
        result = json.loads(response.text)

        if result["error"]:
            raise RuntimeError(result["error"])

        return result["result"]
