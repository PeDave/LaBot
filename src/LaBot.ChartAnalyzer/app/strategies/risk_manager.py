from __future__ import annotations

import logging

from app.api.models import RiskAssessment

logger = logging.getLogger(__name__)


class RiskManager:
    """Position sizing and risk management (1-2% rule)."""

    def calculate(
        self,
        entry_price: float,
        stop_loss: float,
        risk_percent: float = 2.0,
        account_balance: float = 10000.0,
        tp1: float | None = None,
    ) -> RiskAssessment:
        risk_amount = account_balance * (risk_percent / 100.0)
        sl_distance = abs(entry_price - stop_loss)
        position_size = risk_amount / sl_distance if sl_distance > 0 else 0.0
        max_loss = risk_amount
        rr_ratio: float | None = None
        if tp1 is not None:
            reward = abs(tp1 - entry_price)
            rr_ratio = round(reward / sl_distance, 2) if sl_distance > 0 else None

        return RiskAssessment(
            risk_percent=risk_percent,
            account_balance=account_balance,
            risk_amount=round(risk_amount, 2),
            position_size=round(position_size, 6),
            max_loss=round(max_loss, 2),
            rr_ratio=rr_ratio,
        )

