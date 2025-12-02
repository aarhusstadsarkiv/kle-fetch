from kle_fetch.structure import get_emner


if __name__ == "__main__":
    emner = get_emner()

    for emne in emner:
        if emne.emne.udgaaetdato:
            print(emne)
            input()
