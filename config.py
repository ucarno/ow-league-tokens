import json


class Config:
    def __init__(self):
        self.config = self.load()

    def load(self) -> dict:
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                old_config = json.loads(f.read())

                # checking for old config
                if 'account_id' in old_config:
                    config = self.get_default()
                    config['accounts'][old_config['account_id']] = {
                        'username': 'UNKNOWN',
                        'platform': 'UNKNOWN',
                        'level': 'UNKNOWN',
                    }
                else:
                    config = old_config

                f.close()

        except (FileNotFoundError, json.JSONDecodeError):
            # fresh start, using default config
            config = self.get_default()

        return config

    def save(self):
        with open('config.json', 'w+', encoding='utf-8') as f:
            f.write(json.dumps(self.config))
            f.close()

    @staticmethod
    def get_default():
        return {
            'accounts': {},
            'earn_owl': True,
            'earn_owc': True
        }
