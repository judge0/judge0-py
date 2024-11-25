"""Separate file containg tests related to test case functionality."""

import judge0
import pytest
from judge0 import Status, Submission, TestCase
from judge0.api import create_submissions_from_test_cases


@pytest.mark.parametrize(
    "submissions,test_cases,expected_type",
    [
        [Submission(source_code=""), TestCase(), Submission],
        [[Submission(source_code="")], TestCase(), list],
        [Submission(source_code=""), [TestCase()], list],
        [[Submission(source_code="")], [TestCase()], list],
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
            Submission(source_code="print(f'Hello, {input()}')"),
            [
                TestCase("Judge0", "Hello, Judge0"),
            ],
            [Status.ACCEPTED],
        ],
        [
            Submission(source_code="print(f'Hello, {input()}')"),
            [
                TestCase("Judge0", "Hello, Judge0"),
                TestCase("pytest", "Hi, pytest"),
            ],
            [Status.ACCEPTED, Status.WRONG_ANSWER],
        ],
        [
            [
                Submission(source_code="print(f'Hello, {input()}')"),
                Submission(source_code="print(f'Hello,  {input()}')"),
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
def test_test_cases_from_run(
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


@pytest.mark.parametrize(
    "submissions,expected_status",
    [
        [
            Submission(
                source_code="print(f'Hello, {input()}')",
                stdin="Judge0",
                expected_output="Hello, Judge0",
            ),
            Status.ACCEPTED,
        ],
        [
            [
                Submission(
                    source_code="print(f'Hello, {input()}')",
                    stdin="Judge0",
                    expected_output="Hello, Judge0",
                ),
                Submission(
                    source_code="print(f'Hello, {input()}')",
                    stdin="pytest",
                    expected_output="Hello, pytest",
                ),
            ],
            [Status.ACCEPTED, Status.ACCEPTED],
        ],
    ],
)
def test_no_test_cases(submissions, expected_status, request):
    client = request.getfixturevalue("judge0_ce_client")

    submissions = judge0.run(
        client=client,
        submissions=submissions,
    )

    if isinstance(submissions, list):
        assert [submission.status for submission in submissions] == expected_status
    else:
        assert submissions.status == expected_status


@pytest.mark.parametrize("n_submissions", [42, 84])
def test_batched_test_cases(n_submissions, request):
    client = request.getfixturevalue("judge0_ce_client")
    submissions = [
        Submission(source_code=f"print({i})", expected_output=f"{i}")
        for i in range(n_submissions)
    ]

    results = judge0.run(client=client, submissions=submissions)

    assert len(results) == n_submissions
    assert all([result.status == Status.ACCEPTED for result in results])
