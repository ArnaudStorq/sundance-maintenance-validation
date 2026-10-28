"""Run a list of MCP call_tool requests in one session.

Usage:
  python mcp_batch.py <calls.json>
calls.json: [{"toolset": "...", "tool": "...", "args": {...}}, ...]
"""
import json
import sys
import urllib.request

ENDPOINT = "http://127.0.0.1:8000/mcp"


def post(payload, session=None):
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if session:
        headers["Mcp-Session-Id"] = session
    req = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=900) as resp:
        sid = resp.headers.get("Mcp-Session-Id") or session
        body = resp.read().decode("utf-8", errors="replace")
    if not body.strip():
        return None, sid
    if body.lstrip().startswith("{"):
        return json.loads(body), sid
    for line in body.splitlines():
        if line.startswith("data:") and line[5:].strip():
            return json.loads(line[5:].strip()), sid
    return None, sid


_, SID = post({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
    "protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "cursor-scratch", "version": "1.0"}}})
post({"jsonrpc": "2.0", "method": "notifications/initialized"}, SID)

with open(sys.argv[1], encoding="utf-8") as f:
    calls = json.load(f)

for i, call in enumerate(calls):
    print("#" * 20, call["tool"], json.dumps(call.get("args", {})))
    res, _ = post({"jsonrpc": "2.0", "id": 10 + i, "method": "tools/call", "params": {
        "name": "call_tool", "arguments": {
            "toolset_name": call["toolset"],
            "tool_name": call["tool"].rsplit(".", 1)[-1],
            "arguments": call.get("args", {})}}}, SID)
    result = res.get("result", res) if res else {}
    for content in result.get("content", []):
        if content.get("type") == "text":
            text = content["text"]
            try:
                print(json.dumps(json.loads(text), indent=1))
            except json.JSONDecodeError:
                print(text)
    if res and "error" in res:
        print("ERROR:", json.dumps(res["error"]))
