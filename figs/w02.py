"""W2 figures: where an AI input goes, and the AI traffic light."""
from common import scene, save, icon

W = "w02"


def input_path():
    s = scene(h=94, alt="AI에 입력한 내용이 가는 곳")
    extra = []
    me = s.box(4, 30, 56, 26, "내 컴퓨터", sub="프롬프트, 붙여 넣은 글, 올린 파일")
    srv = s.box(87, 30, 56, 26, "AI 회사 서버", sub="모델이 답을 만든다", style="primary")
    extra += [icon("laptop", 4 + 28 - 4, 20, 8), icon("server", 87 + 28 - 4, 20, 8)]
    s.link(me, srv, sides="right>left", label="입력")
    s.link(srv, me, sides="left>right", label="답")
    outs = [("모델 학습", "개인 계정에서 학습 설정을 켜 두면"),
            ("피드백", "좋아요, 싫어요를 누른 대화 (ChatGPT, Gemini 안내)"),
            ("사람 검토와 보관", "일부 대화를 사람이 검토 (Gemini 안내)")]
    bh, gap = 22, 6
    y0 = 43 - (3 * bh + 2 * gap) / 2
    for i, (name, sub) in enumerate(outs):
        b = s.box(170, y0 + i * (bh + gap), 66, bh, name, sub=sub, align="left")
        s.link(srv, b, sides="right>left", kind="indirect")
    s.text(4, 83, 232, 7, "점선은 설정과 서비스에 따라 일어날 수 있는 일이다. 메뉴와 정책은 기초 용어 페이지에서 확인한다.",
           name_pt=9.5, color="muted")
    return save(s, W, "input_path", extra)


def traffic_light():
    rows = [
        ("자유롭게", "개념과 문법 설명, 공개 논문 읽기 도움, 트랙 B 원고", "faint", "circle-check", "2F343B"),
        ("꼭 검증", "참고문헌, 수치, 통계 방법 추천, 최신 연구, AI가 고친 문장의 뜻", "soft", "search", "2F343B"),
        ("조건부 (트랙 A)", "본인 원고 문장. 지도교수 동의, 학습 제외 설정, 원 데이터와 그림 파일은 넣지 않음", "strong", "lock", "FFFFFF"),
        ("넣지 않기", "환자 정보, 심사 중인 원고와 동료 원고, 과제·특허 전 아이디어, 계정", "accent", "ban", "FFFFFF"),
    ]
    r, step, top = 8.5, 21, 6
    s = scene(h=top * 2 + step * 4 + 2, alt="AI 신호등: 자유롭게, 꼭 검증, 조건부, 넣지 않기")
    s.band(10, top - 2, 26, step * 4 + 2, "", style="primary")
    extra = []
    for i, (name, sub, style, ic, ic_color) in enumerate(rows):
        cy = top + step * i + step / 2
        s.circle(23, cy, r, "", style=style)
        extra.append(icon(ic, 23 - 4, cy - 4, 8, ic_color))
        s.text(46, cy - 8, 190, 16, name, sub=sub, bold=True, name_pt=12.5, valign="middle")
    return save(s, W, "traffic_light", extra)


if __name__ == "__main__":
    input_path()
    traffic_light()
