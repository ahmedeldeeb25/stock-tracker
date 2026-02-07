"""Data models for the stock tracker application."""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime, date


@dataclass
class Stock:
    """Stock model."""
    id: Optional[int] = None
    symbol: str = ""
    company_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Target:
    """Price target model."""
    id: Optional[int] = None
    stock_id: Optional[int] = None
    target_type: str = ""  # Buy, Sell, DCA, Trim
    target_price: float = 0.0
    trim_percentage: Optional[float] = None
    alert_note: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None


@dataclass
class Tag:
    """Tag model."""
    id: Optional[int] = None
    name: str = ""
    color: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class Note:
    """Note/Analysis model."""
    id: Optional[int] = None
    stock_id: Optional[int] = None
    title: str = ""
    content: str = ""
    note_date: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class AlertHistory:
    """Alert history model."""
    id: Optional[int] = None
    stock_id: Optional[int] = None
    target_id: Optional[int] = None
    current_price: float = 0.0
    target_price: float = 0.0
    target_type: str = ""
    alert_note: Optional[str] = None
    email_sent: bool = False
    triggered_at: Optional[datetime] = None


@dataclass
class StockWithDetails:
    """Stock with all related data."""
    stock: Stock
    tags: List[Tag]
    targets: List[Target]
    notes: List[Note]
    notes_count: int = 0
    current_price: Optional[float] = None
    price_change: Optional[float] = None
    price_change_percent: Optional[float] = None
