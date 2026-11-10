"""W2 figure: the AI traffic light. (Where an AI input goes is in figs/basics.py.)"""
from common import scene, save, icon

W = "w02"


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
    traffic_light()
