import json
import os


class SafeJSON:

    @staticmethod
    def load(path, default=None):

        if default is None:
            default = {}

        if not os.path.exists(path):
            return default

        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

        except Exception:
            return default

    @staticmethod
    def save(path, data):

        os.makedirs(os.path.dirname(path), exist_ok=True)

        tmp = path + ".tmp"

        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False
            )

        os.replace(tmp, path)