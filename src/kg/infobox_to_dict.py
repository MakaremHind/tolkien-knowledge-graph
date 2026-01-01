def load_infobox_dict(path="data/elrond_infobox.txt"):
    infobox = {}

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("|") and "=" in line:
                key, value = line[1:].split("=", 1)
                infobox[key.strip()] = value.strip()

    return infobox


if __name__ == "__main__":
    box = load_infobox_dict()
    for k, v in box.items():
        print(f"{k}: {v}")
