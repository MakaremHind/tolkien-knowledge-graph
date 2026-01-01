def infobox_to_dict(infobox_text: str) -> dict:
    """
    Converts raw infobox text into a Python dictionary.
    """
    data = {}

    for line in infobox_text.splitlines():
        line = line.strip()

        if not line or line.startswith("|") is False:
            continue

        # remove leading |
        line = line[1:]

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()

    return data


# Optional standalone test
if __name__ == "__main__":
    with open("data/elrond_infobox.txt", encoding="utf-8") as f:
        infobox = f.read()

    d = infobox_to_dict(infobox)

    for k, v in d.items():
        print(f"{k}: {v}")
