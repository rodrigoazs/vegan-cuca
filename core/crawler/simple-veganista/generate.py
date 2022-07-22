import json
import os

import pandas as pd

PATH = "data/simple-veganista/"

data = []
entries = os.listdir(PATH)
for entry in entries:
    file_path = f"{PATH}{entry}"
    with open(file_path) as json_file:
        json_data = json.load(json_file)
        data.append(
            [
                json_data["href"],
                json_data["title"],
                str(json_data["ingredients"]),
                str(json_data["preparation"]),
            ]
        )

df = pd.DataFrame(data, columns=["href", "title", "ingredients", "preparation"])
df.to_csv("simple-veganista.csv")
