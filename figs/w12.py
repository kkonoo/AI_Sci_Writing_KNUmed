"""W12 figure: polish from the largest unit to the smallest."""
from common import scene, save

W = "w12"


def big_to_small():
    s = scene(h=92, alt="다듬기 순서: 내용과 그림 순서, 단락, 문장, 단어와 문법")
    s.band(4, 4, 148, 84, "1. 내용과 그림 순서", style="faint", name_pt=12)
    s.band(14, 18, 128, 62, "2. 단락", style="soft", name_pt=12)
    s.band(24, 32, 108, 40, "3. 문장", style="mid", name_pt=12)
    s.box(34, 46, 88, 18, "4. 단어와 문법", style="plain", name_pt=12)
    s.text(162, 6, 74, 10, "바깥부터 안으로 다듬는다", bold=True, name_pt=12.5)
    s.text(162, 18, 74, 26, "문장부터 다듬으면 나중에 단락을 빼거나 옮길 때 그 수고가 버려진다.", name_pt=11)
    s.box(162, 50, 74, 38, "먼저 볼 것", sub="각 Figure의 결론 문장이 Results 첫 문장, Abstract, Title에 같은 강도로 들어 있는가",
          style="primary", align="left", name_pt=12)
    return save(s, W, "big_to_small")


if __name__ == "__main__":
    big_to_small()
