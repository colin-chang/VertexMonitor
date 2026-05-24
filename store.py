"""
Vertex Monitor — 双模式计费 + 消费统计
支持手动模式（余额+截止日）和自动循环模式（月重置日+金额）。
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


_DATA_DIR = Path(__file__).parent / "data"
_DATA_DIR.mkdir(exist_ok=True)
STORE_PATH = Path(os.environ.get("STORE_PATH", _DATA_DIR / "store.json"))


@dataclass
class BillingConfig:
    mode: str = "auto_recurring"  # "manual" | "auto_recurring"

    # 手动模式
    manual_balance: float = 10.0
    manual_expires_at: str = ""   # ISO datetime

    # 自动循环模式
    auto_reset_day: int = 1        # 每月几号重置
    auto_monthly_amount: float = 10.0

    @property
    def is_manual(self) -> bool:
        return self.mode == "manual"

    @property
    def is_auto(self) -> bool:
        return self.mode == "auto_recurring"


@dataclass
class ModelStat:
    calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost: float = 0.0


@dataclass
class Store:
    billing: BillingConfig = field(default_factory=BillingConfig)
    spent: float = 0.0                    # 本期已消费
    total_calls: int = 0                   # 本期调用次数
    last_reset_at: str = ""                # 上次重置时间 ISO
    lifetime_spent: float = 0.0
    lifetime_calls: int = 0
    model_stats: dict[str, ModelStat] = field(default_factory=dict)

    # ── 计算属性 ──────────────────────────────────

    @property
    def remaining(self) -> float:
        return max(0.0, self._current_balance - self.spent)

    @property
    def exhausted(self) -> bool:
        return self.remaining <= 0

    @property
    def current_balance(self) -> float:
        """当前预算额度。"""
        if self.billing.is_manual:
            return self.billing.manual_balance
        return self.billing.auto_monthly_amount

    @property
    def _current_balance(self) -> float:
        if self.billing.is_manual:
            return self.billing.manual_balance
        return self.billing.auto_monthly_amount

    @property
    def expires_at(self) -> str:
        """当前截止时间。自动模式返回月末最后时刻。"""
        if self.billing.is_manual and self.billing.manual_expires_at:
            return self.billing.manual_expires_at
        # 自动模式：下个重置日前一天 23:59:59
        return _next_reset_boundary(self.billing.auto_reset_day)

    @property
    def expired(self) -> bool:
        if not self.expires_at:
            return False
        expires = datetime.fromisoformat(self.expires_at)
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) > expires

    @property
    def status_text(self) -> str:
        if self.exhausted:
            return "⚠️ 余额耗尽"
        if self.billing.is_manual and self.expired:
            return "⏰ 已过期"
        if self.spent > self._current_balance * 0.8:
            return "🟡 即将耗尽"
        return "🟢 正常"

    # ── 操作 ──────────────────────────────────────

    def check_and_reset(self):
        """自动循环模式：检测是否跨过重置日，若是则重置 spent。"""
        if not self.billing.is_auto:
            return
        now = datetime.now(timezone.utc)
        reset_day = self.billing.auto_reset_day

        if self.last_reset_at:
            last = datetime.fromisoformat(self.last_reset_at)
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)

            # 计算上次重置的"当月重置日"
            last_reset_date = datetime(last.year, last.month, reset_day, tzinfo=timezone.utc)
            if last < last_reset_date:
                last_reset_date = last  # 手动重置过

            # 计算下次应重置的日期
            if now.day >= reset_day:
                next_reset = datetime(now.year, now.month, reset_day, tzinfo=timezone.utc)
            else:
                # 还没到这个月的重置日
                if now.month == 1:
                    prev_month = 12
                    prev_year = now.year - 1
                else:
                    prev_month = now.month - 1
                    prev_year = now.year
                next_reset = datetime(prev_year, prev_month, reset_day, tzinfo=timezone.utc)

            if last < next_reset:
                self._do_reset()

        # 首次，直接设 last_reset_at
        if not self.last_reset_at:
            self.last_reset_at = now.isoformat()

    def _do_reset(self):
        self.spent = 0.0
        self.total_calls = 0
        self.last_reset_at = datetime.now(timezone.utc).isoformat()

    def consume(self, cost_usd: float) -> float:
        """消费指定金额，返回 0=全部覆盖，>0=未覆盖金额。"""
        self.check_and_reset()

        if self.billing.is_manual and self.expired:
            return cost_usd  # 已过期，全额未覆盖

        remaining_before = self.remaining
        deduct = min(remaining_before, cost_usd)
        self.spent += deduct
        self.spent = round(self.spent, 8)
        self.total_calls += 1
        self.lifetime_spent += deduct
        self.lifetime_calls += 1

        uncovered = round(cost_usd - deduct, 8)
        return uncovered

    def record_model(self, model: str, prompt_tokens: int, completion_tokens: int, cost: float):
        """记录模型统计。"""
        if model not in self.model_stats:
            self.model_stats[model] = ModelStat()
        s = self.model_stats[model]
        s.calls += 1
        s.prompt_tokens += prompt_tokens
        s.completion_tokens += completion_tokens
        s.cost += cost
        s.cost = round(s.cost, 8)

    # ── 配置更新 ──────────────────────────────────

    def update_billing(self, data: dict):
        """从 API 请求更新计费配置。"""
        if "mode" in data:
            self.billing.mode = data["mode"]
        if "manual_balance" in data:
            self.billing.manual_balance = float(data["manual_balance"])
        if "manual_expires_at" in data:
            self.billing.manual_expires_at = data["manual_expires_at"]
            if "T" not in self.billing.manual_expires_at:
                self.billing.manual_expires_at += "T23:59:59"
        if "auto_reset_day" in data:
            day = int(data["auto_reset_day"])
            self.billing.auto_reset_day = max(1, min(28, day))
        if "auto_monthly_amount" in data:
            self.billing.auto_monthly_amount = float(data["auto_monthly_amount"])

        # 切换模式时重置消费
        if "mode" in data:
            self.spent = 0.0
            self.total_calls = 0
            self.last_reset_at = datetime.now(timezone.utc).isoformat()

    def reset_now(self):
        """手动立即重置消费（不影响配置）。"""
        self._do_reset()

    # ── 摘要 ──────────────────────────────────────

    def summary(self) -> dict:
        return {
            "billing": {
                "mode": self.billing.mode,
                "manual_balance": self.billing.manual_balance,
                "manual_expires_at": self.billing.manual_expires_at,
                "auto_reset_day": self.billing.auto_reset_day,
                "auto_monthly_amount": self.billing.auto_monthly_amount,
            },
            "current": {
                "balance": round(self._current_balance, 6),
                "spent": round(self.spent, 6),
                "remaining": round(self.remaining, 6),
                "expires_at": self.expires_at,
                "expired": self.expired,
                "exhausted": self.exhausted,
                "status": self.status_text,
            },
            "period": {
                "total_calls": self.total_calls,
                "last_reset_at": self.last_reset_at,
            },
            "lifetime": {
                "spent": round(self.lifetime_spent, 6),
                "calls": self.lifetime_calls,
            },
            "models": {
                m: {
                    "calls": s.calls,
                    "prompt_tokens": s.prompt_tokens,
                    "completion_tokens": s.completion_tokens,
                    "cost": round(s.cost, 6),
                }
                for m, s in sorted(self.model_stats.items())
            },
        }


# ── 辅助 ──────────────────────────────────────────

def _next_reset_boundary(reset_day: int) -> str:
    """计算下一个重置日前一天的 23:59:59。"""
    now = datetime.now(timezone.utc)
    this_month_reset = datetime(now.year, now.month, reset_day, tzinfo=timezone.utc)

    if now < this_month_reset:
        target = this_month_reset
    else:
        # 下个月
        if now.month == 12:
            target = datetime(now.year + 1, 1, reset_day, tzinfo=timezone.utc)
        else:
            target = datetime(now.year, now.month + 1, reset_day, tzinfo=timezone.utc)

    boundary = target.replace(day=reset_day - 1 if reset_day > 1 else 28,
                              hour=23, minute=59, second=59, microsecond=0)
    return boundary.isoformat()


# ── 持久化 ──────────────────────────────────────────

def _serialize(obj):
    """自定义 JSON 序列化，处理嵌套 dataclass。"""
    if isinstance(obj, (Store, BillingConfig)):
        return asdict(obj)
    if isinstance(obj, ModelStat):
        return asdict(obj)
    raise TypeError(f"Unserializable: {type(obj)}")


def load_store(path: Optional[Path] = None) -> Store:
    p = path or STORE_PATH
    if p.exists():
        raw = json.loads(p.read_text(encoding="utf-8"))
        billing = BillingConfig(**raw.get("billing", {}))
        model_stats = {
            m: ModelStat(**s) for m, s in raw.get("model_stats", {}).items()
        }
        store = Store(
            billing=billing,
            spent=raw.get("spent", 0.0),
            total_calls=raw.get("total_calls", 0),
            last_reset_at=raw.get("last_reset_at", ""),
            lifetime_spent=raw.get("lifetime_spent", 0.0),
            lifetime_calls=raw.get("lifetime_calls", 0),
            model_stats=model_stats,
        )
    else:
        store = Store()
        save_store(store, path=path)
    return store


def save_store(store: Store, path: Optional[Path] = None):
    p = path or STORE_PATH
    p.write_text(
        json.dumps(store, indent=2, ensure_ascii=False, default=_serialize),
        encoding="utf-8",
    )


def record_call(
    prompt_tokens: int,
    completion_tokens: int,
    cost_usd: float,
    model: str = "",
    path: Optional[Path] = None,
) -> Store:
    """记录一次调用：消费扣减 + 模型统计 + 历史。"""
    store = load_store(path)
    uncovered = store.consume(cost_usd)
    store.record_model(model, prompt_tokens, completion_tokens, cost_usd)
    save_store(store, path=path)

    # 调用历史
    history_path = (path or STORE_PATH).with_name("store_history.jsonl")
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "cost": round(cost_usd, 8),
        "uncovered": round(uncovered, 8),
        "remaining": round(store.remaining, 8),
    }
    with open(history_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return store
