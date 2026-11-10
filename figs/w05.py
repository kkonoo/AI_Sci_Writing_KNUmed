"""W5 figure: n counts experimental units, not technical replicates."""
from common import scene, save, icon

W = "w05"


def what_n_counts():
    s = scene(h=98, budget=12, alt="n은 실험 단위의 수다. 마우스 여섯 마리가 n = 6이고, 절편 세 장은 기술 반복이다")
    extra = []
    # left: one group, six mice, three sections of mouse 1
    s.box(4, 4, 140, 12, "UUO + compound X 군", style="soft", name_pt=12)
    s.band(4, 21, 140, 30, "실험 단위: 마우스 6마리 (n = 6)", style="faint", name_pt=10.5)
    r, gap = 6.5, 9.6
    mice = []
    for i in range(6):
        cx = 15 + i * (2 * r + gap)
        mice.append(s.circle(cx, 39, r, f"{i + 1}", style="mid" if i else "primary", name_pt=10.5))
    s.band(4, 56, 140, 30, "", style="faint")
    s.text(26, 57.5, 116, 7, "기술 반복: 마우스 1의 절편 3장", bold=True, name_pt=10.5)
    secs = []
    for j in range(3):
        secs.append(s.box(10 + j * 30, 69, 26, 12, f"절편 {j + 1}", name_pt=10.5))
    s.link(mice[0], secs[0], sides="bottom>top", kind="plain")
    s.text(100, 66, 44, 18, "평균을 내서", sub="마우스 1의 값 하나", name_pt=10.5, valign="middle")
    # right: before / after
    s.text(156, 4, 80, 8, "n을 쓰는 법", bold=True, name_pt=12)
    s.box(166, 16, 70, 26, "Before", sub="n = 18 (6 mice × 3 sections)", align="left", name_pt=11.5)
    s.box(166, 50, 70, 31, "After", sub="n = 6 mice per group. For each mouse, values from three sections were averaged.",
          align="left", style="primary", name_pt=11.5)
    extra.append(icon("ban", 156.5, 25.5, 7, "E5484D"))
    extra.append(icon("circle-check", 156.5, 61.5, 7))
    s.text(4, 88, 232, 6, "가상의 예시. 단일세포 데이터에서는 세포 수가 아니라 환자 수가 n이다.", name_pt=10, color="muted")
    return save(s, W, "what_n_counts", extra)


if __name__ == "__main__":
    what_n_counts()
