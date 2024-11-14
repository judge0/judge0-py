import judge0

submission = judge0.Submission(
    source_code="print('Hello Judge0')",
    language=25,
)

# Instead of relying on the CE flavor of judge0, we can use EXTRA_CE.
judge0.run(client=judge0.EXTRA_CE, submissions=submission)

print(submission.stdout)
