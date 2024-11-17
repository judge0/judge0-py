# judge0-py

Python client library for Judge0

    | submissions      | test_cases     | return           |
    |:-----------------|:---------------|:-----------------|
    | Submission       | TestCase       | Submission       |
    | Submission       | list[TestCase] | list[Submission] |
    | list[Submission] | TestCase       | list[Submission] |
    | list[Submission] | list[TestCase] | list[Submission] |