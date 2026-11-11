"""Benchmark an Ollama model: cold load, time to first token, decode tok/s, tool-call sanity."""
import json, sys, time, urllib.request

HOST = "http://127.0.0.1:11434"
MODEL = sys.argv[1] if len(sys.argv) > 1 else "qwen3.5:9b"


def post(path, body, stream=False):
    req = urllib.request.Request(HOST + path, json.dumps(body).encode(), {"Content-Type": "application/json"})
    return urllib.request.urlopen(req, timeout=300)


def chat(messages, tools=None):
    body = {"model": MODEL, "messages": messages, "stream": True, "think": False, "keep_alive": "10m"}
    if tools:
        body["tools"] = tools
    t0 = time.perf_counter()
    ttft = None
    text, calls, final = "", [], None
    with post("/api/chat", body) as r:
        for line in r:
            chunk = json.loads(line)
            msg = chunk.get("message", {})
            if ttft is None and (msg.get("content") or msg.get("tool_calls")):
                ttft = time.perf_counter() - t0
            text += msg.get("content", "")
            calls += msg.get("tool_calls", []) or []
            if chunk.get("done"):
                final = chunk
    return text, calls, ttft, time.perf_counter() - t0, final


# unload first so the first run is a true cold load
post("/api/generate", {"model": MODEL, "keep_alive": 0}).read()
time.sleep(2)

q = [{"role": "user", "content": "In two sentences, why is the sky blue?"}]
for i in range(4):
    text, _, ttft, total, f = chat(q)
    tps = f["eval_count"] / (f["eval_duration"] / 1e9)
    print(f"run {i} {'COLD' if i == 0 else 'warm'}: load={f['load_duration']/1e9:.2f}s "
          f"ttft={ttft:.2f}s total={total:.2f}s decode={tps:.1f} tok/s ({f['eval_count']} tok)")
print("sample:", text.strip()[:200])

tools = [{"type": "function", "function": {
    "name": "set_timer", "description": "Start a countdown timer",
    "parameters": {"type": "object", "properties": {
        "seconds": {"type": "integer"}, "label": {"type": "string"}}, "required": ["seconds"]}}}]
text, calls, ttft, total, _ = chat([{"role": "user", "content": "set a timer for 12 minutes for the pizza"}], tools)
print(f"tool call: ttft={ttft:.2f}s total={total:.2f}s calls={json.dumps([c['function'] for c in calls])} text={text!r}")

with urllib.request.urlopen(HOST + "/api/ps") as r:
    for m in json.load(r)["models"]:
        print(f"ps: {m['name']} size={m['size']/2**30:.2f}GiB vram={m['size_vram']/2**30:.2f}GiB")
