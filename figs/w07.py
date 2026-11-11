"""W7 figure: five steps to check a reference.

Korean: assets/img/w07/verify_reference.svg, English: verify_reference.en.svg.
"""
from common import scene, save

W = "w07"

TEXT = {
    "ko": dict(
        alt="참고문헌을 확인하는 다섯 단계",
        steps=[
            ("DOI", "doi.org에서 열어 본다"),
            ("데이터베이스", "PubMed에서 제목으로 찾고 PMID를 맞춘다"),
            ("서지 대조", "저자, 연도, 제목, 저널, 권과 쪽"),
            ("주장 확인", "내 문장을 받치는 그림, 표, 문장을 본문에서 찾는다"),
            ("상태 확인", "철회와 정정, preprint인지"),
        ],
        name_pt=12.5,
        note="DOI가 열려도 끝이 아니다. 가장 잡기 어려운 오류는 논문은 있는데 내 문장을 받치지 않는 경우다(4단계).",
    ),
    "en": dict(
        alt="Five steps to check a reference",
        steps=[
            ("DOI", "Open it at doi.org"),
            ("Database", "Find the title in PubMed and match the PMID"),
            ("Citation details", "Authors, year, title, journal, volume and pages"),
            ("Claim", "Find the figure, table or sentence that supports your sentence"),
            ("Status", "Retraction, correction, preprint or not"),
        ],
        name_pt=11.5,
        note="An open DOI is not the end. The hardest error to catch is a real paper that does not support your sentence (step 4).",
    ),
}
KEY = 3  # the claim check is the step students skip


def verify_reference(lang="ko"):
    t = TEXT[lang]
    en = lang == "en"
    s = scene(h=74 if en else 70, budget=10, alt=t["alt"])
    x0, inner, gap = 4, 232, 4
    n = len(t["steps"])
    w = (inner - (n - 1) * gap) / n
    prev = None
    for i, (name, sub) in enumerate(t["steps"]):
        x = x0 + i * (w + gap)
        c = s.circle(x + w / 2, 10, 5, str(i + 1), style="mid", name_pt=10)
        if prev is not None:
            s.link(prev, c, sides="right>left", kind="dots")
        prev = c
        s.box(x, 19, w, 34, name, sub=sub, style="primary" if i == KEY else "plain", name_pt=t["name_pt"])
    s.text(x0, 57, inner, 12 if en else 8, t["note"], name_pt=10, color="muted")
    return save(s, W, "verify_reference" + ("" if lang == "ko" else ".en"))


if __name__ == "__main__":
    verify_reference("ko")
    verify_reference("en")
