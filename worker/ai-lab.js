/**
 * Cloudflare Worker: 교재 페이지의 AI 실습 창을 Claude API에 잇는다.
 *
 * 페이지는 대화 내용과 수업 코드만 보낸다. 모델, 답 길이 상한, 설정은 이 파일에서 정하고
 * 페이지에서는 바꿀 수 없다. 시스템 프롬프트는 일부러 넣지 않는다. 학생이 AI가 흔히 하는
 * 실수를 직접 잡는 것이 실습 목적이라서, 답을 조심스럽게 길들이지 않는다.
 *
 * 배포 순서는 worker/README.md에 있다.
 *
 * Secret 두 개가 필요하다 (Settings → Variables and Secrets, Type: Secret).
 *   ANTHROPIC_API_KEY  수업용 API 키
 *   CLASS_CODE         학생에게 따로 공지하는 수업 코드
 *
 * 학생이 보낸 글은 어디에도 저장하지 않는다. 요청 본문을 console.log로 찍지 않는다.
 */

// 해마다 바꿀 수 있는 값. 교재 본문에는 모델 이름을 적지 않는다.
const MODEL = "claude-sonnet-5-5";
const EFFORT = "low";        // 글쓰기 실습이라 생각을 짧게 한다. 답이 빨리 온다.
const MAX_TOKENS = 4096;     // 답 하나의 길이 상한. 150단어 문단과 점검 표에는 넉넉하다.

// 한 번 요청의 상한. 넘으면 페이지에서 새 대화를 시작하게 한다.
const MAX_MESSAGES = 20;     // 질문과 답을 합친 개수
const MAX_TEXT_CHARS = 40000; // 질문과 답의 글자 수 합
const MAX_BODY_BYTES = 300000;

const ALLOWED_ORIGINS = [
  "https://kkonoo.github.io",
  "http://localhost:4321", // quarto preview --port 4321
];

// 앞선 답을 되돌려 보낼 때 받아 주는 블록 종류. 도구는 쓰지 않으므로 tool_use는 없다.
const ASSISTANT_BLOCK_TYPES = new Set(["text", "thinking", "redacted_thinking", "fallback"]);

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    if (!ALLOWED_ORIGINS.includes(origin)) {
      return reply({ error: "origin_not_allowed" }, 403, null);
    }
    if (request.method === "OPTIONS") return reply(null, 204, origin);
    if (request.method !== "POST") return reply({ error: "method_not_allowed" }, 405, origin);

    if (!env.ANTHROPIC_API_KEY || !env.CLASS_CODE) {
      return reply({ error: "not_configured" }, 500, origin);
    }
    if (request.headers.get("X-Class-Code") !== env.CLASS_CODE) {
      return reply({ error: "wrong_class_code" }, 401, origin);
    }

    const raw = await request.text();
    if (raw.length > MAX_BODY_BYTES) return reply({ error: "too_long" }, 413, origin);
    let body;
    try {
      body = JSON.parse(raw);
    } catch {
      return reply({ error: "bad_request" }, 400, origin);
    }

    const messages = checkMessages(body && body.messages);
    if (messages === "too_long") return reply({ error: "too_long" }, 413, origin);
    if (!messages) return reply({ error: "bad_request" }, 400, origin);

    let apiRes;
    try {
      apiRes = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-api-key": env.ANTHROPIC_API_KEY,
          "anthropic-version": "2026-10-21",
          // 안전 분류기가 거절하면 서버가 다른 모델로 한 번 더 돌린다.
          "anthropic-beta": "server-side-fallback-2026-07-01",
        },
        body: JSON.stringify({
          model: MODEL,
          max_tokens: MAX_TOKENS,
          output_config: { effort: EFFORT },
          fallbacks: "default",
          messages,
        }),
      });
    } catch {
      return reply({ error: "upstream_unreachable" }, 502, origin);
    }

    const data = await apiRes.json().catch(() => null);
    if (!apiRes.ok || !data) {
      // 429(호출 한도), 529(과부하)는 잠시 뒤에 다시 보내면 된다.
      const busy = apiRes.status === 429 || apiRes.status === 529;
      return reply(
        { error: busy ? "busy" : "upstream_error", detail: data && data.error ? data.error.message : null },
        busy ? 503 : 502,
        origin
      );
    }

    // 페이지에는 필요한 것만 돌려준다. content는 다음 요청에 그대로 되돌려 보낸다.
    return reply({ content: data.content, stop_reason: data.stop_reason, model: data.model }, 200, origin);
  },
};

// 질문(user)과 답(assistant)이 번갈아 오고 질문으로 끝나는지 본다.
// 질문은 글자열만 받는다. 답은 앞서 이 Worker가 돌려준 블록을 그대로 받는다.
function checkMessages(messages) {
  if (!Array.isArray(messages) || messages.length === 0 || messages.length > MAX_MESSAGES) return null;
  if (messages.length % 2 === 0) return null;

  let chars = 0;
  const out = [];
  for (let i = 0; i < messages.length; i++) {
    const m = messages[i];
    if (i % 2 === 0) {
      if (!m || m.role !== "user" || typeof m.content !== "string" || !m.content.trim()) return null;
      chars += m.content.length;
      out.push({ role: "user", content: m.content });
    } else {
      if (!m || m.role !== "assistant" || !Array.isArray(m.content)) return null;
      for (const block of m.content) {
        if (!block || !ASSISTANT_BLOCK_TYPES.has(block.type)) return null;
        if (block.type === "text") chars += String(block.text || "").length;
      }
      out.push({ role: "assistant", content: m.content });
    }
  }
  return chars > MAX_TEXT_CHARS ? "too_long" : out;
}

function reply(body, status, origin) {
  const headers = { "Content-Type": "application/json", Vary: "Origin" };
  if (origin) {
    headers["Access-Control-Allow-Origin"] = origin;
    headers["Access-Control-Allow-Methods"] = "POST, OPTIONS";
    headers["Access-Control-Allow-Headers"] = "Content-Type, X-Class-Code";
    headers["Access-Control-Max-Age"] = "86400";
  }
  return new Response(body === null ? null : JSON.stringify(body), { status, headers });
}
