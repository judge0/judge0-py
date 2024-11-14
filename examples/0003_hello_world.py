import judge0

submission = judge0.Submission(
    source_code="print('Hello Judge0')",
    language=judge0.PYTHON,
)

judge0.run(submissions=submission)

print(submission.stdout)
