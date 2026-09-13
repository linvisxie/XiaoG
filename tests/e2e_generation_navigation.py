"""Deterministic local synthetic generation-navigation regression.

The harness uses a local delayed SSE source and an isolated fake Provider. It
protects the synthetic navigation path against a global generation lock and
cross-conversation stream pollution. It does not reproduce, resolve, or rule
out the documented navigation delay in the Product Owner's default Edge
runtime, whose root cause remains unknown.
"""
from __future__ import annotations
import asyncio, json, os, socket, subprocess, sys, tempfile, threading, time
from contextlib import asynccontextmanager
from types import SimpleNamespace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError
from playwright.async_api import async_playwright
import httpx
import uvicorn
ROOT=Path(__file__).resolve().parents[1]; PYTHON=ROOT/".venv"/"Scripts"/"python.exe"; EDGE=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
def mark(name, detail=None): print(json.dumps({"t":round(time.monotonic(),3),"event":name,"detail":detail},ensure_ascii=True),flush=True)
def free_port():
 with socket.socket() as s: s.bind(("127.0.0.1",0)); return s.getsockname()[1]
async def step(name, job, timeout=8):
 mark(name+":begin")
 try: value=await asyncio.wait_for(job,timeout)
 except TimeoutError as exc: mark(name+":timeout"); raise RuntimeError(name) from exc
 mark(name+":end"); return value
def start_mock_sse(details, generation):
 class Handler(BaseHTTPRequestHandler):
  protocol_version = "HTTP/1.1"
  def log_message(self, *_): pass
  def do_POST(self):
   if self.path != "/api/conversations/a/chat": self.send_error(404); return
   generation["started"] = time.monotonic(); mark("A_GENERATION_START")
   self.send_response(200); self.send_header("Content-Type", "text/event-stream"); self.send_header("Cache-Control", "no-cache"); self.send_header("Access-Control-Allow-Origin", "*"); self.send_header("Connection", "close"); self.end_headers()
   def emit(event, data): self.wfile.write(f"event: {event}\ndata: {json.dumps(data)}\n\n".encode("utf-8")); self.wfile.flush()
   emit("meta", {"model":"deepseek", "display_name":"DeepSeek"})
   time.sleep(1); emit("delta", {"content":"FIRST_DELTA "}); generation["first_delta"] = time.monotonic(); mark("A_MOCK_SSE_FIRST_DELTA")
   for index in range(120):
    time.sleep(.01); emit("delta", {"content":"x"})
    if index == 59: generation["intermediate_delta"] = time.monotonic(); mark("A_MOCK_SSE_INTERMEDIATE_DELTA", {"burst_deltas":60})
   time.sleep(1); details["a"]["messages"].append({"id":"a2","role":"assistant","content":"A_RESULT","model":"deepseek","created_at":"2026-01-01T00:00:01+00:00"}); mark("A_MOCK_RESULT_PERSISTED"); emit("done", {}); generation["complete"] = time.monotonic(); mark("A_GENERATION_COMPLETE", {"burst_deltas":120})
 server = ThreadingHTTPServer(("127.0.0.1", 0), Handler); server.daemon_threads = True
 threading.Thread(target=server.serve_forever, daemon=True).start(); base = f"http://127.0.0.1:{server.server_address[1]}"; mark("MOCK_SSE_SERVER_READY", {"base":base}); return server, base
async def browser_stage(base):
 routes=[]; generation={"started":None,"first_delta":None,"intermediate_delta":None,"complete":None}; conversations=[{"id":"a","title":"A","archived_at":None,"deleted_at":None},{"id":"b","title":"B","archived_at":None,"deleted_at":None}]; details={"a":{**conversations[0],"messages":[{"id":"a1","role":"assistant","content":"A_ONLY","model":"deepseek","created_at":"2026-01-01T00:00:00+00:00"}]},"b":{**conversations[1],"messages":[{"id":"b1","role":"assistant","content":"B_ONLY","model":"deepseek","created_at":"2026-01-01T00:00:00+00:00"}]}}
 async with async_playwright() as p:
  browser=await step("BROWSER_LAUNCH",p.chromium.launch(executable_path=EDGE,headless=True,timeout=8000))
  try:
   page=await step("PAGE_CREATE",browser.new_page())
   await page.add_init_script("""window.__e2eClickTrace=[]; document.addEventListener('click', function(e) { window.__e2eClickTrace.push({t: performance.now(), text: (e.target.textContent || '').trim(), id: e.target.id || null}); }, true);""")
   async def route(route):
    path=route.request.url.split(base)[-1]; routes.append((route.request.method,path)); mark("REQUEST_RECEIVED",{"method":route.request.method,"path":path})
    if path=="/api/conversations/a/chat": mark("MOCK_SSE_ROUTE_CONTINUED"); await route.continue_(url=mock_sse_base+"/api/conversations/a/chat"); return
    if path=="/api/conversations": payload=conversations
    elif path=="/api/conversations/default-model-settings": payload={"model_mode":"manual","manual_model":"deepseek","manual_reasoning_effort":"low","manual_reasoning_preferences":{}}
    elif path.startswith("/api/conversations/") and route.request.method=="GET":
     if path=="/api/conversations/b": mark("B_OPEN_HANDLER_AWAIT_BEGIN")
     payload=details[path.rsplit("/",1)[-1]]; mark("GET_CONVERSATION_RESPONDED",path)
    elif path=="/api/settings/personalization": payload={"theme_mode":"light","color_scheme":"green","assistant_avatar":"default","user_avatar":"default","font_scale":"standard","default_model":"deepseek","reasoning_preference":"balanced","manual_reasoning_preferences":{},"chat_density":"comfortable","show_message_time":True,"enter_to_send":True,"animations_enabled":True,"ui_language":"zh-CN"}
    elif path=="/api/settings": payload={"system_prompt":"","user_profile":""}
    elif path=="/api/about": payload={"version":"e2e","name":"XiaoG"}
    elif path=="/api/provider-status": payload={"deepseek":{"available":True},"terra":{"available":False,"message":"off"},"registry":{"providers":[],"models":[]}}
    else: payload={}
    await route.fulfill(json=payload)
    if path=="/api/conversations/b": mark("B_OPEN_HANDLER_AWAIT_RESPONSE_FULFILLED")
    elif path=="/api/conversations/default-model-settings": mark("DRAFT_HANDLER_AWAIT_RESPONSE_FULFILLED")
    elif path in ("/api/settings","/api/about","/api/settings/personalization"): mark("SETTINGS_HANDLER_AWAIT_RESPONSE_FULFILLED",path)
   mock_sse_server, mock_sse_base=start_mock_sse(details, generation)
   await step("ROUTE_INSTALL",page.route("**/api/**",route)); await step("PAGE_GOTO",page.goto(base,wait_until="domcontentloaded",timeout=8000)); buttons=page.locator("#conversation-list button.conversation-name"); await step("LIST_RENDER",buttons.nth(1).wait_for(timeout=8000)); summary=await buttons.evaluate_all("els => els.map((e,i) => ({index:i,text:e.textContent.trim(),title:e.title,aria:e.getAttribute('aria-label'),class:e.className,parent:{tag:e.parentElement.tagName,class:e.parentElement.className,title:e.parentElement.title,aria:e.parentElement.getAttribute('aria-label'),id:e.parentElement.id}}))"); mark("CONVERSATION_LIST_DOM",summary)
   a=buttons.filter(has_text="A",has_not_text="B"); b=buttons.filter(has_text="B",has_not_text="A"); ac,bc=await a.count(),await b.count();
   if (ac,bc)!=(1,1): raise RuntimeError(f"HARNESS_PRECONDITION_FAILED_LOCATOR_COUNTS A={ac} B={bc}")
   mark("DOM_A_FOUND"); mark("CLICK_A"); await step("OPEN_A_CLICK",a.click(),2)
   deadline=time.monotonic()+2
   while ("GET","/api/conversations/a") not in routes and time.monotonic()<deadline: await page.wait_for_timeout(25)
   if ("GET","/api/conversations/a") not in routes: raise RuntimeError("HARNESS_PRECONDITION_FAILED_GET_CONVERSATION_A_MISSING")
   await step("ACTIVE_CONVERSATION_A_CONFIRMED",page.wait_for_function("document.querySelector('#conversation-title').textContent==='A'",timeout=1000),2); await step("A_RENDERED",page.get_by_text("A_ONLY").wait_for(timeout=1000),2)
   mark("SUBMIT_A_MESSAGE"); await step("A_SUBMIT",page.locator("#message-input").fill("go"),2); await step("A_REQUEST",page.locator("#chat-form").evaluate("f=>f.requestSubmit()"),2); await page.wait_for_timeout(150)
   if ("POST","/api/conversations") in routes: raise RuntimeError("HARNESS_PRECONDITION_FAILED_ACTIVE_CONVERSATION_EMPTY")
   if ("POST","/api/conversations/a/chat") not in routes: raise RuntimeError("HARNESS_PRECONDITION_FAILED_CHAT_A_MISSING")
   mark("A_GENERATION_PRECONDITION_CONFIRMED")
   deadline=time.monotonic()+2
   while generation["started"] is None and time.monotonic()<deadline: await page.wait_for_timeout(25)
   if generation["started"] is None: raise RuntimeError("HARNESS_PRECONDITION_FAILED_A_GENERATION_NOT_STARTED")
   mark("CLICK_B_RECEIVED"); await step("CLICK_B",b.click(),2)
   await step("B_ROUTE_COMMIT",page.wait_for_function("document.querySelector('#conversation-title').textContent==='B'",timeout=1500),2)
   if generation["first_delta"] is not None: raise RuntimeError("HARNESS_PREFIRST_FAILED_B_COMMITTED_AFTER_FIRST_DELTA")
   if generation["complete"] is not None: raise RuntimeError("HARNESS_PRECONDITION_FAILED_B_COMMITTED_AFTER_GENERATION")
   mark("CLICK_SETTINGS_RECEIVED"); await step("CLICK_SETTINGS",page.locator("#open-settings").click(),2)
   await step("SETTINGS_OPEN_COMMIT",page.wait_for_function("document.querySelector('#settings-dialog').open === true",timeout=1500),2)
   if generation["first_delta"] is not None: raise RuntimeError("HARNESS_PREFIRST_FAILED_SETTINGS_COMMITTED_AFTER_FIRST_DELTA")
   if generation["complete"] is not None: raise RuntimeError("HARNESS_PRECONDITION_FAILED_SETTINGS_COMMITTED_AFTER_GENERATION")
   mark("CLICK_SETTINGS_CLOSE_RECEIVED"); await step("CLICK_SETTINGS_CLOSE",page.locator("#close-settings").click(),2)
   await step("SETTINGS_CLOSE_COMMIT",page.wait_for_function("document.querySelector('#settings-dialog').open === false",timeout=1500),2)
   mark("CLICK_NEW_CHAT_RECEIVED"); await step("CLICK_NEW_CHAT",page.locator("#new-chat").click(),2)
   await step("DRAFT_COMMIT",page.wait_for_function("document.querySelector('#conversation-title').textContent==='新聊天'",timeout=1500),2)
   if generation["first_delta"] is not None: raise RuntimeError("HARNESS_PREFIRST_FAILED_DRAFT_COMMITTED_AFTER_FIRST_DELTA")
   mark("PRE_FIRST_DELTA_NAVIGATION_COMMITTED")
   deadline=time.monotonic()+2
   while generation["first_delta"] is None and time.monotonic()<deadline: await page.wait_for_timeout(25)
   if generation["first_delta"] is None: raise RuntimeError("HARNESS_PRECONDITION_FAILED_A_FIRST_DELTA_MISSING")
   mark("PRE_FIRST_DELTA_FIRST_DELTA_OBSERVED")
   if generation["complete"] is not None: raise RuntimeError("HARNESS_PRECONDITION_FAILED_DRAFT_COMMITTED_AFTER_GENERATION")
   if ("POST","/api/conversations") in routes: raise RuntimeError("HARNESS_FAILED_DRAFT_CREATED_EMPTY_CONVERSATION")
   remaining=max(0,(generation["started"]+4.4-time.monotonic())*1000); await page.wait_for_timeout(remaining)
   if generation["complete"] is None: raise RuntimeError("HARNESS_PRECONDITION_FAILED_A_GENERATION_NOT_COMPLETE")
   if await page.locator("#messages").get_by_text("A_RESULT",exact=True).count(): raise RuntimeError("HARNESS_FAILED_A_STREAM_POLLUTED_DRAFT")
   await page.wait_for_timeout(150)
   await step("STALE_NAVIGATION_ABSENT",page.wait_for_function("document.querySelector('#conversation-title').textContent==='新聊天' && !document.querySelector('#settings-dialog').open",timeout=1000),2)
   mark("RETURN_A_AFTER_COMPLETE"); await step("RETURN_A_CLICK",a.click(),2); await step("A_RESULT_RENDERED",page.get_by_text("A_RESULT").wait_for(timeout=1500),2)
   clicks=await page.evaluate("window.__e2eClickTrace"); mark("BROWSER_CLICK_TRACE",clicks)
   mark("TIMING_SUMMARY",{"generation":generation,"route_commit_before_generation_complete":generation["complete"] is not None})
  finally:
   mock_sse_server.shutdown(); mock_sse_server.server_close(); mark("MOCK_SSE_SERVER_STOPPED")
   await step("BROWSER_CLOSE",browser.close())
def traced_asgi(app):
 async def wrapped(scope, receive, send):
  if scope["type"] != "http": return await app(scope, receive, send)
  mark("SERVER_RECEIVED", {"method":scope["method"],"path":scope["path"]})
  async def traced_send(message):
   if message["type"] == "http.response.start": mark("SERVER_RESPONSE", {"method":scope["method"],"path":scope["path"],"status":message["status"]})
   await send(message)
  await app(scope, receive, traced_send)
 return wrapped
class DelayedFakeProvider:
 name = "deepseek"
 billing_type = "api"
 def __init__(self, signals): self.signals = signals
 async def health_check(self):
  from backend.providers.base import ProviderStatus
  return ProviderStatus("deepseek", True, "e2e fake available", [{"id":"deepseek-v4-flash"}])
 async def list_models(self): return [{"id":"deepseek-v4-flash"}]
 async def stream_chat(self, _messages, _reasoning_effort=None):
  self.signals["started"].set(); mark("BACKEND_FAKE_PROVIDER_GENERATION_START")
  await asyncio.sleep(3)
  yield {"type":"delta", "content":"BACKEND_RESULT"}
  self.signals["complete"] = time.monotonic(); mark("BACKEND_FAKE_PROVIDER_GENERATION_COMPLETE")
 async def send_message(self, *_args, **_kwargs): return {"content":"BACKEND_RESULT", "usage":None, "model":"deepseek-v4-flash"}
 async def get_usage(self): return None
class UnavailableFakeProvider:
 name = "terra"
 billing_type = "subscription"
 async def health_check(self):
  from backend.providers.base import ProviderStatus
  return ProviderStatus("openai_codex", False, "e2e fake unavailable", [])
 async def list_models(self): return []
 async def stream_chat(self, *_args, **_kwargs):
  if False: yield {}
 async def send_message(self, *_args, **_kwargs): return {}
 async def get_usage(self): return None
async def real_backend_concurrency_stage():
 import backend.database.db as database
 import backend.main as real_main
 from backend.services.conversation_service import conversation_service
 original_database_settings, original_lifespan = database.settings, real_main.app.router.lifespan_context
 original_deepseek, original_terra = real_main.model_router.deepseek, real_main.model_router.terra
 original_providers = dict(real_main.model_router.registry._providers)
 signals={"started":asyncio.Event(), "complete":None}
 async with _isolated_backend_server(database, real_main, conversation_service, signals, original_database_settings, original_lifespan, original_deepseek, original_terra, original_providers) as base:
  async def consume_generation():
   async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, read=10.0)) as client:
    mark("CLIENT_GENERATION_REQUEST_START")
    async with client.stream("POST", base+"/api/conversations/"+signals["a_id"]+"/chat", json={"content":"hold", "model_preference":"deepseek", "reasoning_effort":"high"}) as response:
     if response.status_code != 200: raise RuntimeError(f"BACKEND_CHAT_STATUS_{response.status_code}")
     mark("CLIENT_GENERATION_RESPONSE_HEADERS")
     async for line in response.aiter_lines():
      if line.startswith("event:"): mark("CLIENT_GENERATION_SSE_EVENT", line[6:].strip())
  generation_task=asyncio.create_task(consume_generation())
  try:
   await asyncio.wait_for(signals["started"].wait(), timeout=3)
   mark("BACKEND_CONCURRENCY_WINDOW_OPEN")
   async def probe(label, path):
    mark("CLIENT_REQUEST_START", {"label":label,"path":path})
    def request_in_independent_thread():
     with urlopen(base+path, timeout=3) as response: return response.status
    status=await asyncio.to_thread(request_in_independent_thread)
    mark("CLIENT_RESPONSE", {"label":label,"path":path,"status":status})
    if status != 200: raise RuntimeError(f"BACKEND_PROBE_{label}_{status}")
    if signals["complete"] is not None: raise RuntimeError(f"BACKEND_CONCURRENCY_FAILED_{label}_AFTER_GENERATION_COMPLETE")
   await asyncio.gather(
    probe("HEALTH", "/health"),
    probe("CONVERSATION_B", "/api/conversations/"+signals["b_id"]),
    probe("DEFAULTS", "/api/conversations/default-model-settings"),
    probe("SETTINGS", "/api/settings"),
    probe("PERSONALIZATION", "/api/settings/personalization"),
    probe("PROVIDER_STATUS", "/api/provider-status"),
   )
   mark("BACKEND_CONCURRENCY_PROBES_COMPLETE_BEFORE_GENERATION")
   await asyncio.wait_for(generation_task, timeout=6)
  finally:
   if not generation_task.done(): generation_task.cancel()
@asynccontextmanager
async def _isolated_backend_server(database, real_main, conversation_service, signals, original_database_settings, original_lifespan, original_deepseek, original_terra, original_providers):
 with tempfile.TemporaryDirectory(prefix="xiaog-e2e-backend-") as temp_dir:
  database.settings=SimpleNamespace(database_path=Path(temp_dir)/"isolated.db")
  @asynccontextmanager
  async def isolated_lifespan(_app):
   database.initialize_database(); yield
  real_main.app.router.lifespan_context=isolated_lifespan
  fake=DelayedFakeProvider(signals); real_main.model_router.deepseek=fake; real_main.model_router.terra=UnavailableFakeProvider(); real_main.model_router.registry._providers={"deepseek":fake,"terra":real_main.model_router.terra}
  database.initialize_database(); a=conversation_service.create_conversation("A", {"model_mode":"manual","manual_model":"deepseek","manual_reasoning_effort":"high","manual_reasoning_preferences":{"deepseek":"high"}}); b=conversation_service.create_conversation("B", {"model_mode":"manual","manual_model":"deepseek","manual_reasoning_effort":"high","manual_reasoning_preferences":{"deepseek":"high"}}); signals["a_id"],signals["b_id"]=a["id"],b["id"]
  port=free_port(); server=uvicorn.Server(uvicorn.Config(traced_asgi(real_main.app), host="127.0.0.1", port=port, log_level="warning", access_log=False)); server_task=asyncio.create_task(server.serve()); base=f"http://127.0.0.1:{port}"; last=""
  try:
   async with httpx.AsyncClient(timeout=1) as client:
    for _ in range(40):
     try:
      if (await client.get(base+"/health")).status_code==200: mark("BACKEND_SERVER_READY_HTTP_200", {"base":base}); break
     except httpx.HTTPError as exc: last=repr(exc)
     await asyncio.sleep(.1)
    else: raise RuntimeError("BACKEND_SERVER_READINESS_TIMEOUT "+last)
   yield base
  finally:
   server.should_exit=True
   try: await asyncio.wait_for(server_task, timeout=5)
   finally:
    database.settings=original_database_settings; real_main.app.router.lifespan_context=original_lifespan; real_main.model_router.deepseek=original_deepseek; real_main.model_router.terra=original_terra; real_main.model_router.registry._providers=original_providers
    mark("BACKEND_SERVER_STOPPED")
async def all_diagnostics(base):
 await browser_stage(base)
 await real_backend_concurrency_stage()
def main():
 port=free_port(); base=f"http://127.0.0.1:{port}"; server=subprocess.Popen([str(PYTHON),"-m","uvicorn","backend.main:app","--host","127.0.0.1","--port",str(port)],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf-8",errors="replace"); mark("SERVER_START",{"pid":server.pid,"base":base}); last=""
 try:
  for _ in range(75):
   if server.poll() is not None: raise RuntimeError(f"SERVER_EXIT {server.poll()} {server.stdout.read()!r}")
   try:
    if urlopen(base+"/health",timeout=1).status==200: mark("SERVER_READY_HTTP_200",{"pid":server.pid,"base":base}); return asyncio.run(all_diagnostics(base))
   except (URLError,OSError) as exc: last=repr(exc)
   time.sleep(.2)
  raise RuntimeError(f"SERVER_READINESS_TIMEOUT pid={server.pid} last={last}")
 finally:
  if server.poll() is None: server.terminate(); server.wait(timeout=5)
if __name__=="__main__": main()
