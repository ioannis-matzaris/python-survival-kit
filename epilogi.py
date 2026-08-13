import json

RELEASED = "ekdoseis.json"
CONSTRAINTS = "constraints.txt"


def allows(version: str, rule: str) -> bool:
    if rule.startswith(">="):
        return version >= rule[2:]
    if rule.startswith("=="):
        return version == rule[2:]
    if rule.startswith("<"):
        return version < rule[1:]
    return True


def split_constraint(line: str) -> tuple[str, list[str]]:
    for index, char in enumerate(line):
        if char in "~><=!":
            return line[:index], line[index:].split(",")
    return line, []


def read_constraints() -> list[str]:
    lines: list[str] = []
    with open(CONSTRAINTS, encoding="utf-8") as source:
        for raw in source:
            line = raw.strip()
            if line and not line.startswith("#"):
                lines.append(line)
    return lines


def main() -> None:
    with open(RELEASED, encoding="utf-8") as source:
        released: dict[str, list[str]] = json.load(source)

    for line in read_constraints():
        name, rules = split_constraint(line)
        versions = released[name]
        allowed = [version for version in versions if all(allows(version, rule) for rule in rules)]
        chosen = max(allowed) if allowed else "-"
        print(f"{line:<22} {chosen:<10} {len(allowed)}/{len(versions)}")


main()
