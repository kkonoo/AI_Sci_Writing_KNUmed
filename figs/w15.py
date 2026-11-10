"""W15 figure: the semester at a glance (also used on the home page and in W1).

Korean: assets/img/w15/semester_roadmap.svg, English: semester_roadmap.en.svg.
"""
from common import scene, save

W = "w15"

TEXT = {
    "ko": dict(
        alt="학기 전체 흐름: Part 1 기초, Part 2 원고 쓰기, Part 3 다듬기와 투고",
        parts=[
            ("Part 1 · 기초", "W1–W3", ["트랙 정하기", "AI 신호등과 확인 3가지", "읽히는 문장"], "soft", ""),
            ("Part 2 · 원고 쓰기", "W4–W11", ["Figure 순서 카드", "Methods, Results", "참고문헌 표",
                                         "Introduction, Discussion", "Abstract, Title"], "mid", "동료 리뷰 W8"),
            ("Part 3 · 다듬기와 투고", "W12–W15", ["전체 원고 수정본", "Cover letter", "리뷰어 답변서", "기말 원고와 발표"],
             "primary", "동료 리뷰 W12"),
        ],
        note="기말 제출물: 원고, AI 사용 기록, 트랙 B는 실제 논문과의 비교 메모",
        pill_w=36,
    ),
    "en": dict(
        alt="The semester at a glance: Part 1 Foundations, Part 2 Writing the manuscript, Part 3 Polishing and submission",
        parts=[
            ("Part 1 · Foundations", "W1–W3", ["Choosing a track", "AI rules and checks", "Readable sentences"],
             "soft", ""),
            ("Part 2 · Writing", "W4–W11", ["Figure order cards", "Methods, Results", "Reference table",
                                         "Introduction, Discussion", "Abstract, Title"], "mid", "Peer review W8"),
            ("Part 3 · Polishing, submission", "W12–W15", ["Revised manuscript", "Cover letter", "Response to reviewers",
                                                          "Final manuscript, talk"], "primary", "Peer review W12"),
        ],
        note="Final submission: manuscript, AI use log, and for track B a note comparing with the published paper",
        pill_w=40,
    ),
}


def roadmap(lang="ko"):
    t = TEXT[lang]
    s = scene(h=92, alt=t["alt"])
    ch, gap, y = 20, 2, 6
    inner = 232 + (len(t["parts"]) - 1) * (ch / 2 - gap)
    weights = [4.5, 7, 5.5]
    x = 4
    for (name, weeks, items, style, pill), wt in zip(t["parts"], weights):
        w = inner * wt / sum(weights)
        s.chevron(x, y, w, ch, name, sub=weeks, style=style, name_pt=12 if lang == "ko" else 11)
        tx = x + (ch / 2 if x > 4 else 0)
        s.line(tx, y + ch + 4, tx, y + ch + 8 + 6.5 * len(items))
        for j, it in enumerate(items):
            s.text(tx + 3, y + ch + 5 + j * 6.5, w - ch / 2 - 4, 6, it, name_pt=11)
        if pill:
            s.pill(tx + 3, y + ch + 7 + 6.5 * len(items), t["pill_w"], 9, pill, style="faint", name_pt=10)
        x = x + w - ch / 2 + gap
    s.text(4, 80, 232, 7, t["note"], name_pt=10.5, color="muted")
    return save(s, W, "semester_roadmap" + ("" if lang == "ko" else ".en"))


if __name__ == "__main__":
    roadmap("ko")
    roadmap("en")
