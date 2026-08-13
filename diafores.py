import sys


def read_lines(path: str) -> set[str]:
    with open(path, encoding="utf-8") as source:
        return {line.strip() for line in source if line.strip()}


def main() -> None:
    left_path = sys.argv[1]
    right_path = sys.argv[2]
    left = read_lines(left_path)
    right = read_lines(right_path)

    print(f"ΜΟΝΟ ΣΤΟ {left_path}")
    for line in sorted(left - right):
        print(line)

    print()
    print(f"ΜΟΝΟ ΣΤΟ {right_path}")
    for line in sorted(right - left):
        print(line)

    print()
    print(f"ΙΔΙΕΣ: {len(left & right)}")


main()
