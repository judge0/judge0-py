"""Separate file containg tests related to test case functionality."""

import judge0
import pytest
from judge0 import Status, Submission, TestCase
from judge0.api import create_submissions_from_test_cases


@pytest.mark.parametrize(
    "submissions,test_cases,expected_type",
    [
        [Submission(""), TestCase(), Submission],
        [[Submission("")], TestCase(), list],
        [Submission(""), [TestCase()], list],
        [[Submission("")], [TestCase()], list],
    ],
)
def test_create_submissions_from_test_cases_return_type(
    submissions, test_cases, expected_type
):
    output = create_submissions_from_test_cases(submissions, test_cases)
    assert type(output) == expected_type


@pytest.mark.parametrize(
    "source_code_or_submissions,test_cases,expected_status",
    [
        [
            "print(f'Hello, {input()}')",
            [TestCase("Judge0", "Hello, Judge0")],
            [Status.ACCEPTED],
        ],
        [
            "print(f'Hello, {input()}')",
            [
                TestCase("Judge0", "Hello, Judge0"),
                TestCase("pytest", "Hello, pytest"),
            ],
            [Status.ACCEPTED, Status.ACCEPTED],
        ],
        [
            Submission("print(f'Hello, {input()}')"),
            [
                TestCase("Judge0", "Hello, Judge0"),
            ],
            [Status.ACCEPTED],
        ],
        [
            Submission("print(f'Hello, {input()}')"),
            [
                TestCase("Judge0", "Hello, Judge0"),
                TestCase("pytest", "Hi, pytest"),
            ],
            [Status.ACCEPTED, Status.WRONG_ANSWER],
        ],
        [
            [
                Submission("print(f'Hello, {input()}')"),
                Submission("print(f'Hello,  {input()}')"),
            ],
            [
                TestCase("Judge0", "Hello, Judge0"),
                TestCase("pytest", "Hello, pytest"),
            ],
            [
                Status.ACCEPTED,
                Status.ACCEPTED,
                Status.WRONG_ANSWER,
                Status.WRONG_ANSWER,
            ],
        ],
    ],
)
def test_create_submissions_from_test_cases_from_run(
    source_code_or_submissions, test_cases, expected_status, request
):
    client = request.getfixturevalue("judge0_ce_client")

    if isinstance(source_code_or_submissions, str):
        submissions = judge0.run(
            client=client,
            source_code=source_code_or_submissions,
            test_cases=test_cases,
        )
    else:
        submissions = judge0.run(
            client=client,
            submissions=source_code_or_submissions,
            test_cases=test_cases,
        )

    assert [submission.status for submission in submissions] == expected_status
