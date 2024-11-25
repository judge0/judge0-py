from judge0 import Status, Submission, wait


def test_status_before_and_after_submission(request):
    client = request.getfixturevalue("judge0_ce_client")
    submission = Submission(source_code='print("Hello World!")')

    assert submission.status is None

    client.create_submission(submission)
    client.get_submission(submission)

    assert submission.status.__class__ == Status
    assert submission.status >= Status.IN_QUEUE


def test_is_done(request):
    client = request.getfixturevalue("judge0_ce_client")
    submission = Submission(source_code='print("Hello World!")')

    assert submission.status is None

    client.create_submission(submission)
    wait(client=client, submissions=submission)

    assert submission.is_done()
