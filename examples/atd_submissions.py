import os

import judge0

from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ATD_API_KEY")


def run_example(client_class, lang_id_python, lang_id_c):
    client = client_class(api_key=api_key)
    submission1 = judge0.Submission(
        source_code="print('Hello Judge0')",
        language_id=lang_id_python,
        expected_output="Hello Judge0",
    )
    submission2 = judge0.Submission(
        source_code='#include <stdio.h>\n\nint main() {\n  printf("Hello World!");\n  return 0;\n}',
        language_id=lang_id_c,
        expected_output="Hello World!",
    )

    submissions = [submission1, submission2]
    judge0.execute(client=client, submissions=submissions)

    for submission in submissions:
        print(f"{submission.status=}")
        print(f"{submission.stdout=}")


def main():
    run_example(judge0.ATDJudge0CE, 100, 103)
    run_example(judge0.ATDJudge0ExtraCE, 25, 1)


if __name__ == "__main__":
    main()
