"""W9 figure: the Introduction funnel.

Korean: assets/img/w09/intro_funnel.svg, English: intro_funnel.en.svg.
"""
from common import scene, save

W = "w09"

TEXT = {
    "ko": dict(
        alt="Introduction 깔때기: 배경, 왜 중요한가, 기존 연구와 빈틈, 이 연구",
        stages=[
            ("배경", "무엇에 관한 글인가?  ·  1문단"),
            ("왜 중요한가", "왜 이것을 알아야 하나?  ·  배경 끝이나 1문단"),
            ("기존 연구가 보여 준 것과 못 하는 것", "무엇을 이미 알고, 무엇을 아직 모르나?  ·  1~2문단"),
            ("이 연구", "이 연구는 그 빈틈을 어떻게 메우나?  ·  마지막 1문단"),
        ],
    ),
    "en": dict(
        alt="The Introduction funnel: background, why it matters, what existing work has shown and cannot do, this study",
        stages=[
            ("Background", "What is this about?  ·  1 paragraph"),
            ("Why it matters", "Why do I need to know this?  ·  end of the background, or 1 paragraph"),
            ("What existing work has shown and cannot do", "What is already known, and what is still unknown?  ·  1–2 paragraphs"),
            ("This study", "How does this study fill the gap?  ·  last paragraph"),
        ],
    ),
}


def funnel(lang="ko"):
    t = TEXT[lang]
    h, gap = 18, 4
    s = scene(h=4 + 4 * h + 3 * gap + 4, alt=t["alt"])
    cx, widths = 120, [232, 196, 160, 124]
    for i, ((name, sub), w) in enumerate(zip(t["stages"], widths)):
        s.box(cx - w / 2, 4 + i * (h + gap), w, h, name, sub=sub,
              style="primary" if i == 3 else ("faint", "soft", "mid")[i], name_pt=12.5 if lang == "ko" else 12)
    return save(s, W, "intro_funnel" + ("" if lang == "ko" else ".en"))


if __name__ == "__main__":
    funnel("ko")
    funnel("en")
