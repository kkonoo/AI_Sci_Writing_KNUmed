"""W8 figure: a review comment has a location, a problem and a reason (and a suggestion if any).

Korean: assets/img/w08/comment_parts.svg, English: comment_parts.en.svg.
"""
from common import scene, save

W = "w08"

COMMENT = ["Lines 14–16 (qPCR):", "The reference gene used for normalization is not given.",
           "Without it, a reader cannot repeat the ΔΔCt calculation.", "Please name the gene."]
STYLES = ["primary", "mid", "mid", "soft"]

TEXT = {
    "ko": dict(alt="리뷰 코멘트의 네 부분: 위치, 문제, 이유, 제안", labels=["위치", "문제", "이유", "제안 (있으면)"],
               note="위치가 없으면 저자가 어디를 고칠지 모르고, 이유가 없으면 반영할지 판단할 수 없다."),
    "en": dict(alt="The four parts of a review comment: location, problem, reason, suggestion",
               labels=["Location", "Problem", "Reason", "Suggestion (if any)"],
               note="Without a location, the author does not know where to make the change. Without a reason, the author cannot judge whether to accept it."),
}


def comment_parts(lang="ko"):
    t = TEXT[lang]
    en = lang == "en"
    s = scene(h=68 if en else 64, alt=t["alt"])
    x0, inner, gap = 4, 232, 4
    widths = [36, 62, 62, 60] if en else [42, 66, 66, 46]
    scale = (inner - gap * 3) / sum(widths)
    x = x0
    for label, text, style, w in zip(t["labels"], COMMENT, STYLES, widths):
        w *= scale
        s.pill(x, 4, w, 10, label, style=style, name_pt=11.5 if not en else 11)
        s.box(x, 18, w, 28, text, align="left", valign="middle", name_pt=11, bold=False)
        x += w + gap
    s.text(x0, 50, inner, 12 if en else 8, t["note"], name_pt=10.5 if not en else 10, color="muted")
    return save(s, W, "comment_parts" + ("" if lang == "ko" else ".en"))


if __name__ == "__main__":
    comment_parts("ko")
    comment_parts("en")
