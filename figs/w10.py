"""W10 figure: the Discussion mirrors the Introduction.

Korean: assets/img/w10/intro_discussion_mirror.svg, English: intro_discussion_mirror.en.svg.
"""
from common import scene, save

W = "w10"

TEXT = {
    "ko": dict(
        alt="Introduction은 넓은 데서 질문으로 좁아지고, Discussion은 그 질문의 답에서 넓어진다",
        intro=["배경", "왜 중요한가", "기존 연구와 빈틈", "이 연구의 질문"],
        disc=["질문에 대한 답", "기존 연구와 비교", "한계", "다음 단계와 마지막 문장"],
        same="같은 질문", pt=11.5,
        note="첫 문단과 마지막 문장은 모두 Introduction 마지막 문단의 질문에 답한다.",
    ),
    "en": dict(
        alt="The Introduction narrows from the broad context to the question, and the Discussion widens from the answer",
        intro=["Background", "Why it matters", "Existing work and the gap", "This study's question"],
        disc=["Answer to the question", "Comparison with earlier studies", "Limitations", "Next steps and the last sentence"],
        same="Same question", pt=10.5,
        note="The first paragraph and the last sentence both answer the question in the last paragraph of the Introduction.",
    ),
}


def mirror(lang="ko"):
    t = TEXT[lang]
    h, gap, y0 = 12, 3.5, 13
    rows = [y0 + i * (h + gap) for i in range(7)]
    s = scene(h=rows[6] + h + 16, alt=t["alt"])
    lc, rc = 62, 178
    s.text(lc - 58, 4, 116, 7, "Introduction", bold=True, name_pt=12, align="center")
    s.text(rc - 58, rows[3] - 9, 116, 7, "Discussion", bold=True, name_pt=12, align="center")
    lw, rw = [112, 94, 76, 58], [58, 76, 94, 112]
    left = [s.box(lc - lw[i] / 2, rows[i], lw[i], h, t["intro"][i], style="primary" if i == 3 else "plain", name_pt=t["pt"])
            for i in range(4)]
    right = [s.box(rc - rw[i] / 2, rows[3 + i], rw[i], h, t["disc"][i], style="primary" if i == 0 else "plain", name_pt=t["pt"])
             for i in range(4)]
    s.link(left[3], right[0], sides="right>left", label="Results")
    s.link(left[3], right[3], sides="bottom>left", kind="indirect", label=t["same"])
    s.text(4, rows[6] + h + 4, 232, 7, t["note"], name_pt=10, color="muted")
    return save(s, W, "intro_discussion_mirror" + ("" if lang == "ko" else ".en"))


if __name__ == "__main__":
    mirror("ko")
    mirror("en")
