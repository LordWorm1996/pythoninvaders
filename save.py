import hashlib
import hmac
import json
import os

from cryptography.fernet import Fernet

import variables

SAVE_FILE = variables.save_path
SECRET_KEY = variables.SECRET_KEY

DEFAULT_DATA = variables.DEFAULT_DATA


def save_game(data: dict):
    fernet = Fernet(SECRET_KEY)
    json_data = json.dumps(data).encode()
    encrypted = fernet.encrypt(json_data)

    hmac_hash = hmac.new(SECRET_KEY, encrypted, hashlib.sha256).hexdigest()

    save_payload = {"data": encrypted.decode(), "hmac": hmac_hash}

    with open(SAVE_FILE, "w") as f:
        json.dump(save_payload, f)


def load_game():
    if not os.path.exists(SAVE_FILE):
        return DEFAULT_DATA.copy()

    try:
        with open(SAVE_FILE, "r") as f:
            save_payload = json.load(f)

        encrypted = save_payload["data"].encode()
        stored_hmac = save_payload["hmac"]

        expected_hmac = hmac.new(SECRET_KEY, encrypted, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(stored_hmac, expected_hmac):
            raise ValueError("Save file was modified!")

        fernet = Fernet(SECRET_KEY)
        decrypted = fernet.decrypt(encrypted)

        return json.loads(decrypted)

    except Exception as e:
        os.remove(SAVE_FILE)
        return DEFAULT_DATA.copy()
