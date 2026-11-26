# AI 실습 창 Worker

교재 페이지의 AI 실습 창은 이 Worker를 거쳐 Claude API를 부른다. API 키는 Worker에만 있고, 공개 리포와 페이지에는 없다.

- `ai-lab.js`: Cloudflare Worker 코드. 모델, 답 길이 상한, 설정을 여기서 정한다.
- `../assets/ai-lab.html`: 페이지 쪽 실습 창. 맨 위 `WORKER_URL`에 Worker 주소를 넣는다.

Worker는 Cloudflare 대시보드에 코드를 붙여 넣어 배포한다. 리포의 `ai-lab.js`가 원본이다. 고칠 때는 리포 파일을 고치고 대시보드에 다시 붙여 넣는다.

## 처음 배포하기

1. Anthropic Console에서 이 과목에만 쓸 API 키를 만든다. 같은 Console에서 월 사용 한도도 정한다. 이 한도가 비용을 막는 마지막 장치다.
2. Cloudflare 대시보드의 Workers & Pages에서 새 Worker를 만든다. BI 교재 Worker를 만들 때와 같은 순서다.
3. 코드 편집 화면에 `ai-lab.js` 내용을 모두 붙여 넣고 배포한다.
4. Worker 설정의 Variables and Secrets에서 Secret 두 개를 넣는다.
   - `ANTHROPIC_API_KEY`: 1에서 만든 키
   - `CLASS_CODE`: 학생에게 따로 공지할 수업 코드
5. Worker 주소(`https://이름.계정.workers.dev`)를 `assets/ai-lab.html`의 `WORKER_URL`에 넣고 커밋한다. 주소가 비어 있는 동안에는 실습 창이 페이지에 보이지 않는다.
6. 리포 루트에서 `quarto preview --port 4321`을 실행하고 W3 페이지에서 한 번 보내 본다. Worker는 GitHub Pages 주소와 `localhost:4321`에서 온 요청만 받는다.

## 해마다 할 일

- 학기마다 `CLASS_CODE`를 바꾼다. 수업 코드가 밖으로 퍼지면 그때 바로 바꾼다.
- 모델을 바꾸려면 `ai-lab.js`의 `MODEL`만 고친다. 교재 본문에는 모델 이름을 적지 않는다. 학생은 답 아래에 나오는 모델 이름을 AI 사용 기록에 적는다.

## 이 Worker가 막는 것과 막지 않는 것

- 수업 코드가 없으면 Claude API를 부르지 않는다.
- 페이지가 모델, 답 길이, 시스템 프롬프트를 보내도 쓰지 않는다. Worker에 정한 값만 쓴다.
- 대화는 20개 메시지, 글자 수 합 40,000자까지 받는다. 넘으면 페이지에서 새 대화를 시작하게 한다.
- 학생이 보낸 글은 저장하지 않는다. 요청 본문을 로그로 남기는 코드를 넣지 않는다.
- 분당 호출 수는 제한하지 않는다. 학교 와이파이에서는 수강생이 같은 IP 주소를 함께 쓴다. 그래서 IP마다 제한을 걸면 수업 중에 반 전체가 막힐 수 있다. 수업 코드와 Console의 월 사용 한도로 비용을 막는다.
