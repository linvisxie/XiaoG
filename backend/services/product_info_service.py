"""Read only, sanitized XiaoG product status."""
from __future__ import annotations
import json
import subprocess
from pathlib import Path

class ProductInfoService:
    _status_terms = ("版本", "phase", "阶段", "能力", "能做", "不能做", "限制", "更新", "changelog", "开发到", "联网搜索", "web search", "what can", "what can't", "version", "recent")
    def __init__(self, path: Path): self.path = path
    def public_info(self) -> dict:
        try: raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): raw = {}
        info = {key: raw.get(key, [] if key in {"models","capabilities","limitations","changelog"} else "") for key in ("name","version","phase","models","capabilities","limitations","changelog")}
        info["commit"] = self._git_commit()
        return info
    def context_for(self, user_message: str) -> str:
        info = self.public_info(); base = f"\n\n小G产品身份（实时项目状态）：版本 {info['version'] or '未知'}；阶段 {info['phase'] or '未知'}。产品状态问题必须以此信息为准，不能猜测或宣称未列出的能力。"
        normalized = user_message.casefold()
        if not any(term in normalized for term in self._status_terms): return base
        capabilities = "；".join(map(str, info["capabilities"]))
        limitations = "；".join(map(str, info["limitations"]))
        updates = "；".join(f"{item.get('version','')} {item.get('title','')}: {'；'.join(map(str, item.get('items', [])))}" for item in info["changelog"][:3] if isinstance(item, dict))
        return base + f"\n用户正在询问产品状态。权威公开状态：\nCommit：{info['commit']}\n已实现：{capabilities}\n尚未实现/限制：{limitations}\n最近更新：{updates}\n回答应简洁、准确，并明确区分已实现与预留能力。"
    def _git_commit(self) -> str:
        try:
            result = subprocess.run(["git", "-c", f"safe.directory={self.path.parent.as_posix()}", "rev-parse", "HEAD"], cwd=self.path.parent, capture_output=True, text=True, timeout=1, check=True)
            return result.stdout.strip()
        except (OSError, subprocess.SubprocessError): return "unavailable"

product_info_service = ProductInfoService(Path(__file__).resolve().parents[2] / "product_info.json")