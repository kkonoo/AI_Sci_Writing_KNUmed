"""AI and computer basics figures for W2 and the glossary page, in Korean (*.svg) and English (*.en.svg).

    python3 figs/basics.py
"""
from common import scene, save, icon

W = "basics"
LANGS = ("ko", "en")


def out(name, lang):
    return name if lang == "ko" else name + ".en"


# ---------------------------------------------------------------- next word
NEXT = {
    "ko": dict(alt="언어 모델은 다음에 올 말을 확률로 고른다", prompt_head="지금까지의 글",
               cand_head="다음에 올 말 후보와 확률 (예시 값)", wrong="그럴듯하지만 이 연구에는 틀림",
               note="모델은 사실을 찾아보지 않고 그럴듯한 말을 고른다. 그래서 틀린 말도 자연스러운 문장으로 나온다."),
    "en": dict(alt="A language model picks the next words by probability", prompt_head="Text so far",
               cand_head="Next-word candidates (illustrative probabilities)",
               wrong="plausible, but wrong for this study",
               note="The model does not look up facts. It picks plausible words, so wrong content also comes out as natural sentences."),
}
CANDS = [("UUO kidneys", 0.38), ("mice", 0.27), ("the obstructed kidney", 0.21), ("patients", 0.09)]


def next_word(lang):
    t = NEXT[lang]
    s = scene(h=90, budget=10, alt=t["alt"])
    s.text(4, 4, 80, 7, t["prompt_head"], bold=True, name_pt=11.5)
    p = s.box(4, 13, 80, 49.5, "Compound X reduced the fibrotic area in …", style="soft", align="left", name_pt=12.5, bold=False)
    s.text(100, 4, 136, 7, t["cand_head"], bold=True, name_pt=11.5)
    rows = []
    for i, (w, pr) in enumerate(CANDS):
        y = 13 + i * 13
        wrong = w == "patients"
        b = s.box(100, y, 60, 10.5, w, style="faint" if wrong else "plain", align="left", name_pt=11.5, bold=False)
        s.box(164, y + 2, max(4, 52 * pr / 0.38), 6.5, "", style="mid" if not wrong else "accent")
        s.text(164 + max(4, 52 * pr / 0.38) + 2, y, 14, 10.5, f"{pr:.2f}", name_pt=10.5, valign="middle")
        rows.append(b)
    s.text(100, 64, 136, 7, "↑ " + t["wrong"], name_pt=10, color="muted")
    s.link(p, rows[0], sides="right>left")
    s.text(4, 75, 232, 11, t["note"], name_pt=10, color="muted")
    return save(s, W, out("next_word", lang))


# ---------------------------------------------------------------- what the model uses
SEES = {
    "ko": dict(alt="모델이 답할 때 쓰는 것과 모르는 것", uses="답할 때 쓰는 것", answer="답", lacks="모르는 것",
               src=[("학습한 자료", "지식 시점까지"), ("이번 대화", "컨텍스트 창 안에 있는 내용"), ("웹 검색 결과", "검색 기능을 켰을 때만")],
               no=[("지식 시점 이후의 논문과 규정", "웹 검색을 끄면"), ("다른 대화의 내용", "메모리 기능을 끄면"),
                   ("내 컴퓨터의 파일", "올리거나 열어 주지 않으면")]),
    "en": dict(alt="What a model uses when it answers, and what it does not know", uses="What it uses to answer",
               answer="Answer", lacks="What it does not know",
               src=[("Training data", "up to the knowledge cutoff"), ("This conversation", "what is inside the context window"),
                    ("Web search results", "only when search is on")],
               no=[("Papers and policies after the cutoff", "if web search is off"), ("Other conversations", "if memory is off"),
                   ("Files on your computer", "unless you upload or open them")]),
}


def model_sees(lang):
    t = SEES[lang]
    s = scene(h=88, budget=10, alt=t["alt"])
    s.text(4, 4, 100, 7, t["uses"], bold=True, name_pt=11.5)
    h, gap = 20, 4
    srcs = [s.box(4, 13 + i * (h + gap), 92, h, n, sub=sb, align="left", name_pt=11.5) for i, (n, sb) in enumerate(t["src"])]
    ans = s.box(113, 13 + h + gap, 30, h, t["answer"], style="primary", name_pt=12.5)
    for b in srcs:
        s.link(b, ans, sides="right>left")
    s.text(160, 4, 76, 7, t["lacks"], bold=True, name_pt=11.5)
    for i, (n, sb) in enumerate(t["no"]):
        s.box(160, 13 + i * (h + gap), 76, h, n, sub=sb, style="faint", align="left", name_pt=11)
    return save(s, W, out("model_sees", lang))


# ---------------------------------------------------------------- tool scope
SCOPE = {
    "ko": dict(alt="도구마다 AI에 들어가는 범위", ai="AI 회사 서버",
               rows=[("Chat (대화형)", "내가 붙여 넣은 글, 올린 파일", "message-square"),
                     ("Cowork, Code (작업형)", "내가 열어 준 폴더의 파일 전부", "folder-open"),
                     ("커넥터, 플러그인", "연결한 서비스 안의 파일", "plug")],
               note="폴더를 열어 주거나 서비스를 연결하는 것은 그 안의 내용을 AI에 넣는 것과 같다."),
    "en": dict(alt="What goes into AI with each kind of tool", ai="AI company server",
               rows=[("Chat", "text you paste, files you upload", "message-square"),
                     ("Cowork, Code (agents)", "every file in the folder you open", "folder-open"),
                     ("Connectors, plugins", "files in the connected service", "plug")],
               note="Opening a folder or connecting a service is the same as putting its content into AI."),
}


def tool_scope(lang):
    t = SCOPE[lang]
    s = scene(h=86, budget=10, alt=t["alt"])
    h, gap = 18, 6
    extra, srcs = [], []
    for i, (mode, what, ic) in enumerate(t["rows"]):
        y = 4 + i * (h + gap)
        s.box(14, y, 62, h, mode, style="soft", align="left", name_pt=11.5)
        extra.append(icon(ic, 4, y + h / 2 - 3.5, 7))
        srcs.append(s.box(84, y, 100, h, what, align="left", name_pt=11, bold=False))
    ai = s.box(192, 4 + h + gap - 6, 44, h + 12, t["ai"], style="primary", name_pt=11.5)
    extra.append(icon("server", 192 + 22 - 3.5, 4 + h + gap - 6 - 9, 7))
    for b in srcs:
        s.link(b, ai, sides="right>left")
    s.text(4, 75, 232, 7, t["note"], name_pt=10, color="muted")
    return save(s, W, out("tool_scope", lang), extra)


# ---------------------------------------------------------------- input path (also used in W2)
INPUT = {
    "ko": dict(alt="AI에 입력한 내용이 가는 곳", me="내 컴퓨터", me_sub="프롬프트, 붙여 넣은 글, 올린 파일", srv="AI 회사 서버",
               srv_sub="모델이 답을 만든다", inp="입력", ans="답",
               outs=[("모델 학습", "개인 계정에서 학습 설정을 켜 두면"), ("피드백", "좋아요, 싫어요를 누른 대화 (ChatGPT, Gemini 안내)"),
                     ("사람 검토와 보관", "일부 대화를 사람이 검토 (Gemini 안내)")],
               note="점선은 설정과 서비스에 따라 일어날 수 있는 일이다. 메뉴와 정책은 기초 용어 페이지에서 확인한다."),
    "en": dict(alt="Where your AI input goes", me="Your computer", me_sub="prompt, pasted text, uploaded files",
               srv="AI company server", srv_sub="the model writes the answer", inp="input", ans="answer",
               outs=[("Model training", "personal accounts, setting on"),
                     ("Feedback", "rated conversations (ChatGPT, Gemini)"),
                     ("Human review", "some conversations (Gemini)")],
               note="Dashed lines are things that can happen depending on settings and service. Check menus and policies in the glossary."),
}


def input_path(lang):
    t = INPUT[lang]
    s = scene(h=98, alt=t["alt"])
    me = s.box(4, 30, 56, 26, t["me"], sub=t["me_sub"])
    srv = s.box(87, 30, 56, 26, t["srv"], sub=t["srv_sub"], style="primary")
    extra = [icon("laptop", 4 + 28 - 4, 20, 8), icon("server", 87 + 28 - 4, 20, 8)]
    s.link(me, srv, sides="right>left", label=t["inp"])
    s.link(srv, me, sides="left>right", label=t["ans"])
    bh, gap = 22, 6
    y0 = 43 - (3 * bh + 2 * gap) / 2
    for i, (name, sub) in enumerate(t["outs"]):
        b = s.box(170, y0 + i * (bh + gap), 66, bh, name, sub=sub, align="left")
        s.link(srv, b, sides="right>left", kind="indirect")
    s.text(4, 84, 232, 10, t["note"], name_pt=9.5, color="muted")
    return save(s, W, out("input_path", lang), extra)


# ---------------------------------------------------------------- file path
PATHS = {
    "ko": dict(alt="폴더 구조와 파일 경로", tree="폴더 구조", path="경로로 쓰면", ext="확장자가 알려 주는 것",
               exts=[(".tif", "그림 파일"), (".docx", "문서 파일 (서식 포함)"), (".csv, .txt, .md", "텍스트 파일 (AI가 가장 정확히 읽음)")]),
    "en": dict(alt="Folder structure and file paths", tree="Folders", path="Written as a path", ext="What the extension tells you",
               exts=[(".tif", "image file"), (".docx", "document file (with formatting)"),
                     (".csv, .txt, .md", "text file (read most accurately by AI)")]),
}


def file_path(lang):
    t = PATHS[lang]
    s = scene(h=96, budget=12, alt=t["alt"])
    extra = []
    s.text(4, 4, 90, 7, t["tree"], bold=True, name_pt=11.5)
    levels = [("C:", 0, "folder"), ("Users", 1, "folder"), ("me", 2, "folder"), ("paper", 3, "folder-open"),
              ("figure1.tif", 4, "file"), ("manuscript.docx", 4, "file-text"), ("data.csv", 4, "file-text")]
    for i, (name, lvl, ic) in enumerate(levels):
        y = 13 + i * 10.5
        x = 6 + lvl * 9
        extra.append(icon(ic, x, y + 1, 7, "3F6A92" if name == "figure1.tif" else "2F343B"))
        s.text(x + 9, y, 50, 9, name, name_pt=11, bold=name == "figure1.tif", valign="middle")
    s.text(108, 4, 128, 7, t["path"], bold=True, name_pt=11.5)
    s.box(108, 13, 128, 15, "C:\\Users\\me\\paper\\figure1.tif", sub="Windows", style="soft", align="left", name_pt=11, bold=False)
    s.box(108, 32, 128, 15, "/Users/me/paper/figure1.tif", sub="macOS", style="soft", align="left", name_pt=11, bold=False)
    s.text(108, 52, 128, 7, t["ext"], bold=True, name_pt=11.5)
    for i, (e, what) in enumerate(t["exts"]):
        y = 61 + i * 10
        s.text(108, y, 40, 9, e, name_pt=11, bold=True, valign="middle")
        s.text(150, y, 86, 9, what, name_pt=10.5, valign="middle")
    return save(s, W, out("file_path", lang), extra)


# ---------------------------------------------------------------- cloud and sync
CLOUD = {
    "ko": dict(alt="클라우드와 동기화", me="내 컴퓨터", me_sub="동기화 폴더", cloud="클라우드 저장소", cloud_sub="Google Drive, OneDrive",
               other="다른 기기", other_sub="노트북, 휴대폰", sync="동기화", ai="AI 채팅 서비스", ai_sub="이것도 회사 서버(클라우드)에서 돈다",
               note="동기화 폴더에 넣은 파일은 클라우드에도 올라간다. AI에 입력한 내용도 내 컴퓨터를 떠난다."),
    "en": dict(alt="The cloud and sync", me="Your computer", me_sub="synced folder", cloud="Cloud storage", cloud_sub="Google Drive, OneDrive",
               other="Other devices", other_sub="laptop, phone", sync="sync", ai="AI chat service",
               ai_sub="also runs on company servers (the cloud)",
               note="Files in a synced folder are uploaded to the cloud too. What you type into AI also leaves your computer."),
}


def cloud_sync(lang):
    t = CLOUD[lang]
    s = scene(h=86, alt=t["alt"])
    me = s.box(4, 22, 58, 24, t["me"], sub=t["me_sub"])
    cl = s.box(91, 22, 58, 24, t["cloud"], sub=t["cloud_sub"], style="primary")
    ot = s.box(178, 22, 58, 24, t["other"], sub=t["other_sub"])
    extra = [icon("monitor", 4 + 29 - 4, 12, 8), icon("cloud", 91 + 29 - 4, 12, 8), icon("smartphone", 178 + 29 - 4, 12, 8)]
    s.link(me, cl, sides="right>left", label=t["sync"])
    s.link(cl, me, sides="left>right")
    s.link(cl, ot, sides="right>left", label=t["sync"])
    s.link(ot, cl, sides="left>right")
    s.box(91, 52, 58, 20, t["ai"], sub=t["ai_sub"], style="faint", name_pt=11)
    s.text(4, 75, 232, 7, t["note"], name_pt=10, color="muted")
    return save(s, W, out("cloud_sync", lang), extra)


# ---------------------------------------------------------------- git
GIT = {
    "ko": dict(alt="git의 커밋, push, pull", mine="내 컴퓨터의 저장소", remote="GitHub 저장소 (클라우드)", peer="동료의 컴퓨터",
               commits=["Figure 2 수정", "Methods 보충", "Results 2단락"], push="push", pull="pull",
               note="커밋마다 무엇을 왜 바꿨는지 한 줄을 남긴다. 예전 커밋으로 언제든 돌아갈 수 있다."),
    "en": dict(alt="git commits, push and pull", mine="Repository on your computer", remote="GitHub repository (cloud)",
               peer="A colleague's computer", commits=["Fix Figure 2", "Add Methods detail", "Results paragraph 2"],
               push="push", pull="pull",
               note="Each commit keeps a one-line note of what changed and why. You can go back to any earlier commit."),
}


def git_flow(lang):
    t = GIT[lang]
    s = scene(h=80, budget=10, alt=t["alt"])
    s.band(4, 4, 112, 62, t["mine"], style="faint", name_pt=11)
    prev = None
    for i, c in enumerate(t["commits"]):
        cx = 20 + i * 36
        n = s.circle(cx, 30, 5, "", style="primary" if i == 2 else "mid")
        s.text(cx - 16, 38, 32, 14, c, name_pt=10, align="center")
        if prev is not None:
            s.link(prev, n, sides="right>left", kind="plain")
        prev = n
    rem = s.box(140, 10, 96, 22, t["remote"], style="primary", name_pt=11.5)
    peer = s.box(140, 44, 96, 22, t["peer"], name_pt=11.5)
    s.link(prev, rem, sides="right>left", label=t["push"])
    s.link(rem, peer, sides="bottom>top", label=t["pull"])
    s.text(4, 70, 232, 6, t["note"], name_pt=10, color="muted")
    return save(s, W, out("git_flow", lang), [icon("cloud", 228, 12, 6, "FFFFFF")])


# ---------------------------------------------------------------- extensions
EXT = {
    "ko": dict(alt="스킬, 커넥터, 플러그인, API가 Claude와 이어지는 방식", req="내 요청", req_sub="chat, Cowork, Code",
               claude="Claude", plugin="플러그인: 한 번에 설치하는 묶음 (선택)",
               skill="스킬", skill_sub="일하는 방법을 적은 지시문. 필요할 때 읽는다",
               conn="커넥터", conn_sub="서비스의 MCP 서버에 연결",
               svc="외부 서비스", svc_sub="파일, 캘린더, 이슈 관리",
               api="내 코드 (API)", api_sub="채팅 화면 없이 모델을 부른다",
               read="읽는다", act="읽고 작업한다"),
    "en": dict(alt="How skills, connectors, plugins and the API connect to Claude", req="Your request",
               req_sub="chat, Cowork, Code", claude="Claude", plugin="Plugin: a package installed in one go (optional)",
               skill="Skill", skill_sub="written instructions for a task, read when needed",
               conn="Connector", conn_sub="connects to the service's MCP server",
               svc="External service", svc_sub="files, calendar, issue tracker",
               api="Your code (API)", api_sub="calls the model without a chat screen",
               read="reads", act="reads, acts"),
}


def extensions(lang):
    t = EXT[lang]
    s = scene(h=104, budget=10, alt=t["alt"])
    req = s.box(4, 36, 46, 24, t["req"], sub=t["req_sub"], name_pt=11.5)
    cl = s.box(66, 36, 40, 24, t["claude"], style="primary", name_pt=13)
    s.link(req, cl, sides="right>left")
    s.band(122, 4, 72, 86, t["plugin"], style="faint", name_pt=10)
    sk = s.box(128, 16, 60, 28, t["skill"], sub=t["skill_sub"], name_pt=11.5)
    cn = s.box(128, 54, 60, 28, t["conn"], sub=t["conn_sub"], name_pt=11.5)
    sv = s.box(204, 54, 32, 28, t["svc"], sub=t["svc_sub"], name_pt=10.5, sub_pt=9.5)
    s.link(sk, cl, sides="left>right")
    s.link(cl, cn, sides="right>left")
    s.link(cn, sv, sides="right>left")
    api = s.box(4, 70, 46, 28, t["api"], sub=t["api_sub"], style="soft", name_pt=11)
    s.link(api, cl, sides="right>bottom")
    return save(s, W, out("extensions", lang), [icon("code", 4 + 23 - 3.5, 64, 7)])


if __name__ == "__main__":
    for lang in LANGS:
        for f in (next_word, model_sees, tool_scope, input_path, file_path, cloud_sync, git_flow, extensions):
            print(f"== {f.__name__} {lang}")
            f(lang)
