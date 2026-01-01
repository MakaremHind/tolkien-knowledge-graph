infobox = {}

with open("data/elrond_infobox.txt", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line.startswith("|") and "=" in line:
            key, value = line[1:].split("=", 1)
            infobox[key.strip()] = value.strip()

for k, v in infobox.items():
    print(f"{k}: {v}")
