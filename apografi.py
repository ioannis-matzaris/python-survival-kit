import os

SITE_PACKAGES = "site-packages"


def main() -> None:
    print("ΤΙ ΕΧΕΙΣ")
    for entry in sorted(os.listdir(SITE_PACKAGES)):
        print(entry)


main()
