import judge0

submission = judge0.Submission(
    source_code="print('Hello Judge0')",
    language_id=100,
)

judge0.execute(submissions=submission)

print(submission.stdout)
