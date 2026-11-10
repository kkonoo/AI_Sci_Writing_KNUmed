"""W10 figure: the Discussion mirrors the Introduction."""
from common import scene, save

W = "w10"

INTRO = ["배경", "왜 중요한가", "기존 연구와 빈틈", "이 연구의 질문"]
DISC = ["질문에 대한 답", "기존 연구와 비교", "한계", "다음 단계와 마지막 문장"]


def mirror():
    h, gap, y0 = 12, 3.5, 13
    rows = [y0 + i * (h + gap) for i in range(7)]
    s = scene(h=rows[6] + h + 16, alt="Introduction은 넓은 데서 질문으로 좁아지고, Discussion은 그 질문의 답에서 넓어진다")
    lc, rc = 62, 178
    s.text(lc - 58, 4, 116, 7, "Introduction", bold=True, name_pt=12, align="center")
    s.text(rc - 58, rows[3] - 9, 116, 7, "Discussion", bold=True, name_pt=12, align="center")
    lw, rw = [112, 94, 76, 58], [58, 76, 94, 112]
    left = [s.box(lc - lw[i] / 2, rows[i], lw[i], h, INTRO[i], style="primary" if i == 3 else "plain", name_pt=11.5)
            for i in range(4)]
    right = [s.box(rc - rw[i] / 2, rows[3 + i], rw[i], h, DISC[i], style="primary" if i == 0 else "plain", name_pt=11.5)
             for i in range(4)]
    s.link(left[3], right[0], sides="right>left", label="Results")
    s.link(left[3], right[3], sides="bottom>left", kind="indirect", label="같은 질문")
    s.text(4, rows[6] + h + 4, 232, 7, "첫 문단과 마지막 문장은 모두 Introduction 마지막 문단의 질문에 답한다.",
           name_pt=10, color="muted")
    return save(s, W, "intro_discussion_mirror")


if __name__ == "__main__":
    mirror()
