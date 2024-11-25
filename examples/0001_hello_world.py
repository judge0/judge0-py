import judge0

submission = judge0.Submission(
    source_code="print('Hello Judge0')",
    language=100,
)

# Run submission on CE flavor of judge0.
submission = judge0.run(submissions=submission)

print(submission.stdout)
