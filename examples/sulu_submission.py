import os
import time

import judge0

from dotenv import load_dotenv

load_dotenv()

sulu_auth_token = os.getenv("SULU_API_KEY")

client_ce = judge0.SuluCEClient(auth_token=sulu_auth_token)
submission = judge0.SingleFileSubmission(
    source_code=b"print(f'Hello Judge0')",
    language_id=100,
    expected_output=b"Hello Judge0",
)
submission.submit(client_ce)
time.sleep(1)
submission.check(client_ce)

print(submission.status)
print(submission.stdout)
