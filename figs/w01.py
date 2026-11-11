"""W1 figures: reading order vs writing order, and choosing a track.

Korean: assets/img/w01/<name>.svg, English: <name>.en.svg.
"""
from common import scene, save, icon

W = "w01"

ORDER = {
    "ko": dict(
        alt="독자가 읽는 순서와 이 수업에서 원고를 쓰는 순서",
        rows=[
            ("독자가 읽는 순서", [("Title", "", "soft"), ("Abstract", "", "soft"), ("그림", "", "plain"),
                             ("Results, Methods", "필요한 부분만", "plain")]),
            ("이 수업에서 원고를 쓰는 순서", [("그림", "W4", "primary"), ("Methods, Legend", "W5", "plain"),
                                    ("Results", "W6", "plain"), ("Introduction", "W9", "plain"),
                                    ("Discussion", "W10", "plain"), ("Abstract, Title", "W11", "soft")]),
        ],
    ),
    "en": dict(
        alt="The order in which readers read a paper, and the order in which this course writes the manuscript",
        rows=[
            ("How readers read", [("Title", "", "soft"), ("Abstract", "", "soft"), ("Figures", "", "plain"),
                                  ("Results, Methods", "Only the parts they need", "plain")]),
            ("How this course writes the manuscript", [("Figures", "W4", "primary"), ("Methods, Legend", "W5", "plain"),
                                                      ("Results", "W6", "plain"), ("Introduction", "W9", "plain"),
                                                      ("Discussion", "W10", "plain"), ("Abstract, Title", "W11", "soft")]),
        ],
    ),
}

TRACKS = {
    "ko": dict(
        alt="트랙 A와 트랙 B를 정하는 기준",
        conds=[
            "그림 3~4개 분량의 결과가 있다",
            "지도교수가 수업에서 쓰는 데 동의했다",
            "동료 리뷰에서 같은 반 학생이 읽어도 된다",
            "과제나 특허 출원 전의 아이디어가 아니다",
        ],
        cond_pt=11,
        a=("트랙 A: 내 원고", "자기 데이터와 그림으로 짧은 원고"),
        b=("트랙 B: 공개 논문 다시 쓰기", "담당교수가 승인한 오픈 액세스 논문"),
        yes="모두 해당", no="하나라도 아님",
        ab_pt=None,
        note="애매하면 이번 주 안에 지도교수와 담당교수에게 묻는다.",
    ),
    "en": dict(
        alt="Criteria for choosing track A or track B",
        conds=[
            "You have results for 3–4 figures",
            "Your supervisor agreed to their use in class",
            "Classmates may read it in peer review",
            "Not ideas yet to be filed in a grant or patent",
        ],
        cond_pt=10.5,
        a=("Track A: your own manuscript", "A short manuscript from your own data and figures"),
        b=("Track B: rewriting a published paper", "An open access paper approved by the instructor"),
        yes="All apply", no="Not all",
        ab_pt=11.5,
        note="If you are unsure, ask your supervisor and the instructor this week.",
    ),
}


def suffix(lang):
    return "" if lang == "ko" else ".en"


def order(lang="ko"):
    t = ORDER[lang]
    s = scene(h=98, alt=t["alt"], budget=20)
    x0, inner = 4, 232
    y = 4
    for label, items in t["rows"]:
        s.text(x0, y, inner, 7, label, bold=True, name_pt=11)
        n, gap = len(items), 4
        w = (inner - (n - 1) * gap) / n
        cy = y + 13
        prev = None
        for i, (name, sub, style) in enumerate(items):
            x = x0 + i * (w + gap)
            c = s.circle(x + w / 2, cy, 4.8, str(i + 1), style="mid", name_pt=10)
            if prev is not None:
                s.link(prev, c, sides="right>left", kind="dots")
            prev = c
            s.box(x, cy + 7, w, 21, name, sub=sub, style=style, name_pt=12 if n < 6 else 11)
        y = cy + 7 + 21 + 8
    return save(s, W, "reading_writing_order" + suffix(lang))


def tracks(lang="ko"):
    t = TRACKS[lang]
    s = scene(h=86, alt=t["alt"])
    bx, bw, bh, gap, y0 = 14, 108, 12, 4, 8
    span = 4 * bh + 3 * gap
    group = s.band(4, 4, 124, span + 8, "", style="faint")
    extra = []
    for i, c in enumerate(t["conds"]):
        y = y0 + i * (bh + gap)
        s.box(bx, y, bw, bh, c, align="left", name_pt=t["cond_pt"])
        extra.append(icon("circle-check", 6.5, y + bh / 2 - 3.5, 7))
    ab_h = (span - 8) / 2
    kw = {"name_pt": t["ab_pt"]} if t["ab_pt"] else {}
    a = s.box(164, y0, 72, ab_h, t["a"][0], sub=t["a"][1], style="primary", **kw)
    b = s.box(164, y0 + span - ab_h, 72, ab_h, t["b"][0], sub=t["b"][1], style="soft", **kw)
    s.link(group, a, sides="right>left", label=t["yes"], mid=154)
    s.link(group, b, sides="right>left", label=t["no"], mid=154)
    s.text(4, 75, 232, 7, t["note"], name_pt=10, color="muted")
    return save(s, W, "choose_track" + suffix(lang), extra)


if __name__ == "__main__":
    for lang in ("ko", "en"):
        order(lang)
        tracks(lang)
