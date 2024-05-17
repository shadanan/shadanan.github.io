#!/usr/bin/env python3
import colorsys
import re
import string

import pandas as pd

pd.set_option("display.max_rows", 200)

df = pd.read_csv("tkcolors.csv")
cmap = pd.read_csv("colormap.csv")


def camelcase(text: str):
    if text[0] in string.ascii_uppercase:
        return text.replace("Grey", "Gray")
    return "".join([w.capitalize().replace("Grey", "Gray") for w in text.split()])


def hls(row):
    r, g, b = row["red"] / 255, row["green"] / 255, row["blue"] / 255
    return colorsys.rgb_to_hls(r, g, b)


def hex(row):
    return f"#{row['red']:02x}{row['green']:02x}{row['blue']:02x}"


def base(colors: list[str]) -> str:
    for src, dst in cmap.itertuples(index=False, name=None):
        if src in ", ".join(colors).lower():
            return dst
    raise Exception(f"Failed to determine base color for {colors}")


def canonical(colors: list[str]) -> str:
    colors = sorted([camelcase(c) for c in colors], key=len)
    unnumbered_colors = [c for c in colors if not re.search(r"[0-9]", c)]
    if len(unnumbered_colors) > 0:
        unnumbered_colors.sort(key=len)
        return unnumbered_colors[0]
    return colors[0]


def gn(row) -> tuple[str, int]:
    name = row["name"]
    if m := re.match(r"([a-zA-Z]+)(\d+)", name):
        return m.group(1), int(m.group(2))
    return name, 0


def mono(base: str) -> int:
    if base == "mono":
        return 0
    if base == "cream":
        return 1
    return 2


df = pd.read_csv("tkcolors.csv")
df = (
    df.groupby(["red", "green", "blue"])
    .agg(base=("name", base), name=("name", canonical), all=("name", list))
    .reset_index()
)
df["hex"] = df.apply(hex, axis=1)
df[["g", "n"]] = df.apply(gn, axis=1, result_type="expand")
df[["h", "l", "s"]] = df.apply(hls, axis=1, result_type="expand")
base_df = df.groupby("base")["h"].median().reset_index(name="base_hue")
df = df.merge(base_df, on="base")
df["mono"] = df["base"].apply(mono)
df = df.sort_values(["mono", "base_hue", "g", "n"])

# print(df[df["all"].apply(len) > 1].head(120))

html = []
for row in df.itertuples(index=False):
    fg = "white" if row.l < 0.4 else "black"  # type: ignore
    html.append(
        f'<div class="color" style="color: {fg}; background: {row.hex}">{row.name}</div>'
    )

with open("index.html.template", "r") as fp:
    template = fp.read()
with open("index.html", "w") as fp:
    fp.write(template.replace("{}", "\n".join(html)))
