import judge0
from judge0 import Flavor

submission = judge0.Submission(
    source_code="print('Hello Judge0')",
    language_id=25,
)

# Instead of relying on the CE flavor of judge0, we can use EXTRA_CE.
judge0.run(client=Flavor.EXTRA_CE, submissions=submission)

print(submission.stdout)
