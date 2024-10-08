import os
import time

import judge0

from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("SULU_API_KEY")


def run_example(client_class, language_id):
    client = client_class(api_key=api_key)
    submission = judge0.SingleFileSubmission(
        source_code="print('Hello Judge0')",
        language_id=language_id,
        expected_output="Hello Judge0",
    )

    client.create_submission(submission)
    time.sleep(1)
    client.get_submission(submission)

    print(f"{submission.status=}")
    print(f"{submission.stdout=}")


def main():
    run_example(judge0.SuluJudge0CE, 100)
    run_example(judge0.SuluJudge0ExtraCE, 25)


if __name__ == "__main__":
    main()
