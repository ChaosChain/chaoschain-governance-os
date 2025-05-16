"""
Reputation System Database Models

This module defines the SQLAlchemy models for the Reputation System.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

from chaoscore.core.common.db import Base


class ReputationScoreModel(Base):
    """
    SQLAlchemy model for reputation scores.
    """
    __tablename__ = "reputation_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, index=True, nullable=False)
    overall_score = Column(Float, nullable=False)
    component_scores = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    computation_details = Column(JSON, nullable=True)
    
    # Add relationship to history table
    history = relationship("ReputationHistoryModel", back_populates="score")


class ReputationHistoryModel(Base):
    """
    SQLAlchemy model for reputation history.
    
    This table stores historical reputation scores for agents.
    """
    __tablename__ = "reputation_history"
    
    id = Column(Integer, primary_key=True, index=True)
    score_id = Column(Integer, ForeignKey("reputation_scores.id"), nullable=False)
    agent_id = Column(String, index=True, nullable=False)
    overall_score = Column(Float, nullable=False)
    component_scores = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Add relationship to score table
    score = relationship("ReputationScoreModel", back_populates="history") 