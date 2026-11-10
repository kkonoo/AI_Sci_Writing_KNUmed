"""W13 figure: the six parts of a cover letter."""
from common import scene, save, icon

W = "w13"

PARTS = [
    ("받는 사람과 첫 문단", "편집자 이름, 원고 제목, 논문 유형"),
    ("연구 질문과 중요성", "1~2문장"),
    ("주요 결과", "2~3문장. Abstract와 같은 수치, 같은 주장 강도"),
    ("왜 이 저널의 독자인가", "Aims & Scope의 구체적인 문장, DOI를 확인한 관련 논문"),
    ("필요한 진술", "중복 투고 아님, 저자 동의, 이해 상충, preprint, AI 사용"),
    ("추천·제외 리뷰어", "저널이 요구할 때만"),
]


def cover_letter():
    h, gap, y0 = 15, 3, 14
    rows = [y0 + i * (h + gap) for i in range(6)]
    s = scene(h=rows[5] + h + 10, budget=14, alt="Cover letter의 여섯 부분")
    s.band(4, 4, 152, rows[5] + h + 2, "Cover letter (1쪽 안팎)", style="faint", name_pt=12)
    for i, ((name, sub), y) in enumerate(zip(PARTS, rows)):
        s.circle(15, y + h / 2, 4.8, str(i + 1), style="mid", name_pt=10)
        s.box(24, y, 126, h, name, sub=sub, align="left", style="primary" if i == 2 else "plain", name_pt=11.5)
    s.text(166, 10, 70, 10, "규칙", bold=True, name_pt=12.5)
    s.box(166, 22, 70, 30, "칭찬과 형용사 대신", sub="편집자가 확인할 수 있는 사실을 쓴다", style="soft", name_pt=12)
    s.box(166, 58, 70, 30, "지어내지 않는다", sub="저널에 관한 사실과 관련 논문은 직접 확인한 것만", style="soft", name_pt=12)
    return save(s, W, "cover_letter", [icon("file-text", 146, 5.5, 7)])


if __name__ == "__main__":
    cover_letter()
