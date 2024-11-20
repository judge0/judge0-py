import judge0

user_solution = judge0.Submission(
    source_code="""
lower_bound, upper_bound = (int(x) for x in input().strip().split())
while True:
    my_guess = (lower_bound + upper_bound) // 2
    print(my_guess)

    command = input().strip()
    if command == "lower":
        lower_bound, upper_bound = lower_bound, my_guess
    elif command == "higher":
        lower_bound, upper_bound = my_guess, upper_bound
    else:
        break
"""
)

interactive_producer = judge0.Submission(
    source_code="""
#include <stdio.h>

int main(int argc, char **argv) {
    int lower_bound, upper_bound, number_to_guess, max_tries;
    scanf("%d %d %d %d", &lower_bound, &upper_bound, &number_to_guess, &max_tries);

    FILE *user_solution_stdin = fopen(argv[1], "w");
	FILE *user_solution_stdout = fopen(argv[2], "r");

    fprintf(user_solution_stdin, "%d %d\\n", lower_bound, upper_bound);
    fflush(user_solution_stdin);

    int user_guess;
    for (int i = 0; i < max_tries; i++) {
        fscanf(user_solution_stdout, "%d", &user_guess);
        if (user_guess > number_to_guess) {
            fprintf(user_solution_stdin, "lower\\n");
            fflush(user_solution_stdin);
        } else if (user_guess < number_to_guess) {
            fprintf(user_solution_stdin, "higher\\n");
            fflush(user_solution_stdin);
        } else {
            fprintf(user_solution_stdin, "correct\\n");
            fflush(user_solution_stdin);

            printf("User successfully guessed the number.\\n");

            return 0;
        }
    }

    fprintf(user_solution_stdin, "failed\\n");
    fflush(user_solution_stdin);

    printf("User failed to guess the number within %d guesses.\\n", max_tries);

    return 0;
}
""",
    language=judge0.C,
)

result = judge0.run(
    submissions=user_solution,
    interactive_producer=interactive_producer,
    test_cases=judge0.TestCase(input="0 100 42 7", expected_output="User successfully guessed the number.\n"),
)

print(f"Submission status: {result.status}")
print(f"Producer stdout: {result.stdout}")
print(f'User stdout:\n{result.post_execution_filesystem.find("user.stdout")}')
print(f'User stdin:\n{result.post_execution_filesystem.find("user.stdin")}')
