"""Run a Python file inside the editor through PythonScriptingTools.execute_python.

Usage:
  python mcp_run_editor_py.py <script.py>
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
    with urllib.request.urlopen(req, timeout=600) as resp:
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

with open(sys.argv[1], encoding="utf-8") as script_file:
    source = script_file.read()

res, _ = post({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
    "name": "call_tool", "arguments": {
        "toolset_name": "editor_toolset.toolsets.python_scripting.PythonScriptingTools",
        "tool_name": "execute_python",
        "arguments": {"script": {"content": source, "language": "Python"}}}}}, SID)
result = res.get("result", res)
for content in result.get("content", []):
    if content.get("type") == "text":
        text = content["text"]
        try:
            print(json.loads(text).get("returnValue", text))
        except json.JSONDecodeError:
            print(text)
if "error" in res:
    print("ERROR:", json.dumps(res["error"]))
