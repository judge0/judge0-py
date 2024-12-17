import judge0
from judge0 import File, Filesystem

print("Subexample 1")
result = judge0.run(source_code="print('hello, world')")
fs = Filesystem(content=result.post_execution_filesystem)
for f in fs:
    print(f.name)
    print(f)
    print()


print("Subexample 2")
fs = Filesystem(content=File(name="my_file.txt", content="hello, world"))
result = judge0.run(
    source_code="print(open('my_file.txt').read())", additional_files=fs
)
print(result.stdout)
for f in Filesystem(content=result.post_execution_filesystem):
    print(f.name)
    print(f)
    print()


print("Subexample 3")
fs = Filesystem(content=File(name="my_file.txt", content="hello, world"))
result = judge0.run(
    source_code="print(open('my_file.txt').read())", additional_files=fs
)
print(result.stdout)
for f in result.post_execution_filesystem:
    print(f.name)
    print(f)
    print()

print("Subexample 4")
fs = Filesystem(
    content=[
        File(name="my_file.txt", content="hello, world"),
        File(name="./dir1/dir2/dir3/my_file2.txt", content="hello, world2"),
    ]
)
result = judge0.run(source_code="find .", additional_files=fs, language=46)
print(result.stdout)
for f in Filesystem(content=result.post_execution_filesystem):
    print(f.name)
    print(f)
    print()
