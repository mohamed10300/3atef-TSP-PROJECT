import uuid
from datetime import date, datetime
from sqlalchemy import (
    Boolean, Column, Date, DateTime, Float, ForeignKey,
    Integer, String, Text, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


def _uuid():
    return str(uuid.uuid4())


class Event(Base):
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=_uuid)
    name = Column(String(500), nullable=False)
    type = Column(String(100), nullable=False)  # medical, pharma, tech, industrial, business
    country = Column(String(200), nullable=False)
    city = Column(String(200), nullable=False)
    venue_name = Column(String(500))
    venue_address = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    source = Column(String(50), default="manual")  # email, web_scrape, manual, excel
    status = Column(String(20), default="pending")  # pending, approved, rejected
    score = Column(Float, default=0.0)
    risk_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    hotels = relationship("Hotel", back_populates="event", cascade="all, delete-orphan")
    decisions = relationship("ApprovalDecision", back_populates="event", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="event", cascade="all, delete-orphan")


class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(String(36), primary_key=True, default=_uuid)
    event_id = Column(String(36), ForeignKey("events.id"), nullable=False)
    name = Column(String(500), nullable=False)
    address = Column(Text)
    distance_from_venue_km = Column(Float, default=0.0)
    rating = Column(Float, default=0.0)
    room_type = Column(String(200))
    market_price = Column(Float, default=0.0)
    vendor_price = Column(Float, default=0.0)
    competitor_price = Column(Float, default=0.0)
    price_difference = Column(Float, default=0.0)  # market_price - vendor_price
    is_cheaper_than_vendor = Column(Boolean, default=False)
    refund_policy = Column(Text)
    cancellation_penalty = Column(Text)
    no_show_policy = Column(Text)
    availability = Column(Boolean, default=True)
    booking_url = Column(Text)
    collected_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="hotels")
    price_snapshots = relationship("PriceSnapshot", back_populates="hotel", cascade="all, delete-orphan")


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id = Column(String(36), primary_key=True, default=_uuid)
    hotel_id = Column(String(36), ForeignKey("hotels.id"), nullable=False)
    price = Column(Float, nullable=False)
    source = Column(String(100))  # booking.com, expedia, agoda, vendor, competitor
    captured_at = Column(DateTime, default=datetime.utcnow)

    hotel = relationship("Hotel", back_populates="price_snapshots")


class ApprovalDecision(Base):
    __tablename__ = "approval_decisions"

    id = Column(String(36), primary_key=True, default=_uuid)
    event_id = Column(String(36), ForeignKey("events.id"), nullable=False)
    decision = Column(String(20), nullable=False)  # approved, rejected
    hotels_cheaper_count = Column(Integer, default=0)
    min_price_difference = Column(Float, default=0.0)
    rule_triggered = Column(String(100))  # "3_hotels_4_dollar_rule" or manual
    decided_at = Column(DateTime, default=datetime.utcnow)
    decided_by = Column(String(100), default="system")

    event = relationship("Event", back_populates="decisions")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=_uuid)
    event_id = Column(String(36), ForeignKey("events.id"), nullable=False)
    report_type = Column(String(100))  # approved_events, rejected_events, competitor_analysis, hotel_profitability, risk_summary
    content = Column(JSON)
    pdf_url = Column(Text)
    generated_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="reports")
