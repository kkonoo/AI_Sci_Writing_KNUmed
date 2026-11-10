"""W1 figures: reading order vs writing order, and choosing a track."""
from common import scene, save, icon

W = "w01"


def order():
    s = scene(h=98, alt="독자가 읽는 순서와 이 수업에서 원고를 쓰는 순서", budget=20)
    x0, inner = 4, 232
    rows = [
        ("독자가 읽는 순서", [("Title", "", "soft"), ("Abstract", "", "soft"), ("그림", "", "plain"),
                         ("Results, Methods", "필요한 부분만", "plain")]),
        ("이 수업에서 원고를 쓰는 순서", [("그림", "W4", "primary"), ("Methods, Legend", "W5", "plain"),
                                ("Results", "W6", "plain"), ("Introduction", "W9", "plain"),
                                ("Discussion", "W10", "plain"), ("Abstract, Title", "W11", "soft")]),
    ]
    y = 4
    for label, items in rows:
        s.text(x0, y, inner, 7, label, bold=True, name_pt=11)
        n, gap = len(items), 4
        w = (inner - (n - 1) * gap) / n
        cy = y + 13
        circles, prev = [], None
        for i, (name, sub, style) in enumerate(items):
            x = x0 + i * (w + gap)
            c = s.circle(x + w / 2, cy, 4.8, str(i + 1), style="mid", name_pt=10)
            if prev is not None:
                s.link(prev, c, sides="right>left", kind="dots")
            prev = c
            s.box(x, cy + 7, w, 21, name, sub=sub, style=style, name_pt=12 if n < 6 else 11)
        y = cy + 7 + 21 + 8
    return save(s, W, "reading_writing_order")


def tracks():
    s = scene(h=86, alt="트랙 A와 트랙 B를 정하는 기준")
    conds = [
        "그림 3~4개 분량의 결과가 있다",
        "지도교수가 수업에서 쓰는 데 동의했다",
        "동료 리뷰에서 같은 반 학생이 읽어도 된다",
        "과제나 특허 출원 전의 아이디어가 아니다",
    ]
    bx, bw, bh, gap, y0 = 14, 108, 12, 4, 8
    span = 4 * bh + 3 * gap
    group = s.band(4, 4, 124, span + 8, "", style="faint")
    extra = []
    for i, c in enumerate(conds):
        y = y0 + i * (bh + gap)
        s.box(bx, y, bw, bh, c, align="left", name_pt=11)
        extra.append(icon("circle-check", 6.5, y + bh / 2 - 3.5, 7))
    ab_h = (span - 8) / 2
    a = s.box(164, y0, 72, ab_h, "트랙 A: 내 원고", sub="자기 데이터와 그림으로 짧은 원고", style="primary")
    b = s.box(164, y0 + span - ab_h, 72, ab_h, "트랙 B: 공개 논문 다시 쓰기", sub="담당교수가 승인한 오픈 액세스 논문", style="soft")
    s.link(group, a, sides="right>left", label="모두 해당", mid=154)
    s.link(group, b, sides="right>left", label="하나라도 아님", mid=154)
    s.text(4, 75, 232, 7, "애매하면 이번 주 안에 지도교수와 담당교수에게 묻는다.", name_pt=10, color="muted")
    return save(s, W, "choose_track", extra)


if __name__ == "__main__":
    order()
    tracks()
