import os

import judge0
from dotenv import load_dotenv

load_dotenv()

sulu_auth_token = os.getenv("SULU_API_KEY")

client_ce = judge0.SuluCEClient(auth_token=sulu_auth_token)
print(client_ce.get_about())
print(client_ce.get_config_info())
print(client_ce.get_statuses())
print(client_ce.get_languages())
print(client_ce.get_languages(language_id=42))

client_extra_ce = judge0.SuluExtraCEClient(auth_token=sulu_auth_token)
print(client_extra_ce.get_about())
print(client_extra_ce.get_config_info())
print(client_extra_ce.get_statuses())
print(client_extra_ce.get_languages())
print(client_extra_ce.get_languages(language_id=24))
