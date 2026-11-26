"""W3 figure: the end of one sentence leads into the start of the next.

Korean: assets/img/w03/old_to_new.svg, English: old_to_new.en.svg.
"""
from common import scene, save

W = "w03"

# The "After" example in principle 2 of W3, split into the start and the new information.
SENTENCES = [
    ("We divided fibroblasts", "into four subtypes."),
    ("One of these subtypes, MF2,", "was more common in patients with fibrosis."),
    ("In these patients, MF2 made up", "a median of 24% of fibroblasts, compared with 7% in controls (P = 0.008)."),
]

TEXT = {
    "ko": dict(alt="앞 문장의 끝에 나온 말이 다음 문장의 첫머리로 이어진다",
               start="첫머리: 앞 문장에서 받은 말", end="끝: 이 문장의 새 정보",
               note="가상의 예시. 화살표는 앞 문장의 끝에서 다음 문장의 첫머리로 이어지는 말을 가리킨다."),
    "en": dict(alt="The end of one sentence leads into the start of the next",
               start="Start: from the sentence before", end="End: this sentence's new information",
               note="Fictional example. Each arrow points from the end of one sentence to the start of the next."),
}


def old_to_new(lang="ko"):
    t = TEXT[lang]
    s = scene(h=92, alt=t["alt"])
    lx, lw, rx, rw = 17, 86, 112, 124
    s.text(lx, 4, lw, 7, t["start"], bold=True, name_pt=11)
    s.text(rx, 4, rw, 7, t["end"], bold=True, name_pt=11)
    bh, gap = 15, 10
    starts, ends = [], []
    for i, (start, end) in enumerate(SENTENCES):
        y = 14 + i * (bh + gap)
        s.circle(9.5, y + bh / 2, 4.8, str(i + 1), style="mid", name_pt=10)
        starts.append(s.box(lx, y, lw, bh, start, style="soft", align="left", valign="middle", name_pt=10.5, bold=False))
        ends.append(s.box(rx, y, rw, bh, end, align="left", valign="middle", name_pt=10.5, bold=False))
    for i in range(len(SENTENCES) - 1):
        s.link(ends[i], starts[i + 1], sides="bottom>top")
    s.text(4, 82, 232, 6, t["note"], name_pt=9.5, color="muted")
    return save(s, W, "old_to_new" + ("" if lang == "ko" else ".en"))


if __name__ == "__main__":
    old_to_new("ko")
    old_to_new("en")
