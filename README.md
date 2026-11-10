# AI활용 영어학술논문작성법 @ KNUmed

https://kkonoo.github.io/AI_Sci_Writing_KNUmed/

대학원 강의 "AI활용 영어학술논문작성법"의 교재 사이트다. 영어판과 한국어판이 있고, 라이트 모드와 다크 모드를 지원한다.

이 리포를 고치기 전에 [CLAUDE.md](CLAUDE.md)를 먼저 읽는다. Codex를 쓰면 같은 내용이 [AGENTS.md](AGENTS.md)에 있다.

## 구조

- 영어판은 `index.qmd`, `ai_rules.qmd`, `glossary.qmd`, `resources.qmd`, `phrases.qmd`, `chapters/`에 있다.
- 한국어판은 같은 이름으로 `ko/` 아래에 있다.
- 주차 페이지 파일 이름은 `wNN_주제.qmd`다. 예: `chapters/w01_orientation.qmd`, `ko/chapters/w01_orientation.qmd`.
- 그림은 `figs/wNN.py`(도식)와 `figs/plots.R`(데이터 그래프)로 만들어 `assets/img/wNN/`에 SVG로 저장한다.
- 테마는 `assets/html.css`, EN/KO 전환 버튼은 `assets/language-switch.html`에 있다. 구성은 다른 HaLab 수업 교재 사이트와 같다.
- main에 push하면 GitHub Actions가 렌더해서 GitHub Pages에 올린다.

## 담당표

자기 담당 주차만 고친다. 담당이 정해지면 이 표를 채운다.

| 주 | 주제 | 담당 | 비고 |
|---|---|---|---|
| 1 | 오리엔테이션 | | |
| 2 | AI 기본기 | | |
| 3 | 읽히는 영어 문장 | | |
| 4 | Figure 스토리보드 | | |
| 5 | Methods와 Figure legend | | |
| 6 | Results | | |
| 7 | 문헌 찾기와 인용 | | |
| 8 | 중간 점검 | | |
| 9 | Introduction | | |
| 10 | Discussion | | |
| 11 | Abstract와 Title | | |
| 12 | 다듬기 | | |
| 13 | 투고 준비 | | |
| 14 | 리뷰어 답변 | | |
| 15 | 기말 | | |
| - | 강의 소개, AI 사용 규칙, 참고자료 | | |

## 로컬에서 미리 보기

[Quarto](https://quarto.org/docs/get-started/)를 설치한 뒤 리포 루트에서 실행한다.

```bash
quarto preview
```

push하기 전에는 `quarto render`로 전체 사이트가 오류 없이 렌더되는지 확인한다.
