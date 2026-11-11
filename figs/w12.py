"""W12 figure: polish from the largest unit to the smallest.

Korean: assets/img/w12/big_to_small.svg, English: big_to_small.en.svg.
"""
from common import scene, save

W = "w12"

TEXT = {
    "ko": dict(
        alt="다듬기 순서: 내용과 그림 순서, 단락, 문장, 단어와 문법",
        levels=["1. 내용과 그림 순서", "2. 단락", "3. 문장", "4. 단어와 문법"],
        head="바깥부터 안으로 다듬는다",
        why="문장부터 다듬으면 나중에 단락을 빼거나 옮길 때 그 수고가 버려진다.",
        first=("먼저 볼 것", "각 Figure의 결론 문장이 Results 첫 문장, Abstract, Title에 같은 강도로 들어 있는가"),
        pt=12,
    ),
    "en": dict(
        alt="Order of polishing: content and figure order, paragraphs, sentences, words and grammar",
        levels=["1. Content and figure order", "2. Paragraphs", "3. Sentences", "4. Words and grammar"],
        head="Polish from the outside in",
        why="If you polish sentences first, that work is lost when you later cut or move a paragraph.",
        first=("Check first", "Does each figure's conclusion sentence appear, with the same strength, in the first "
                               "Results sentence, the Abstract and the Title?"),
        pt=11.5,
    ),
}


def big_to_small(lang="ko"):
    t = TEXT[lang]
    pt = t["pt"]
    s = scene(h=92, alt=t["alt"])
    s.band(4, 4, 148, 84, t["levels"][0], style="faint", name_pt=pt)
    s.band(14, 18, 128, 62, t["levels"][1], style="soft", name_pt=pt)
    s.band(24, 32, 108, 40, t["levels"][2], style="mid", name_pt=pt)
    s.box(34, 46, 88, 18, t["levels"][3], style="plain", name_pt=pt)
    s.text(162, 6, 74, 10, t["head"], bold=True, name_pt=12.5 if lang == "ko" else 12)
    s.text(162, 18, 74, 26, t["why"], name_pt=11 if lang == "ko" else 10.5)
    s.box(162, 50, 74, 38, t["first"][0], sub=t["first"][1], style="primary", align="left",
          name_pt=12 if lang == "ko" else 11.5, **({} if lang == "ko" else {"sub_pt": 9.5}))
    return save(s, W, "big_to_small" + ("" if lang == "ko" else ".en"))


if __name__ == "__main__":
    big_to_small("ko")
    big_to_small("en")
