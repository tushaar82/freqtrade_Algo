"""
Seed Data Script
VELOX Trading Platform
"""
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared.schemas.database.user import User, UserRole
from shared.schemas.database.instrument import Instrument, Exchange, InstrumentType
from shared.schemas.database.strategy import Strategy, StrategyStatus, TradingMode
from services.dashboard-api-service.src.auth.password import hash_password

DATABASE_URL = "postgresql://velox:velox123@localhost:5432/velox_trading"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def seed_data():
    """Seed initial data"""
    db = SessionLocal()
    
    try:
        # Create admin user
        admin = User(
            id=uuid4(),
            email="admin@velox.com",
            password_hash=hash_password("admin123"),
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        
        # Create sample instruments
        instruments = [
            Instrument(
                id=uuid4(),
                symbol="RELIANCE",
                exchange=Exchange.NSE,
                instrument_type=InstrumentType.EQUITY,
                lot_size=1,
                tick_size=0.05,
                is_active=True
            ),
            Instrument(
                id=uuid4(),
                symbol="TCS",
                exchange=Exchange.NSE,
                instrument_type=InstrumentType.EQUITY,
                lot_size=1,
                tick_size=0.05,
                is_active=True
            ),
            Instrument(
                id=uuid4(),
                symbol="INFY",
                exchange=Exchange.NSE,
                instrument_type=InstrumentType.EQUITY,
                lot_size=1,
                tick_size=0.05,
                is_active=True
            )
        ]
        
        for instrument in instruments:
            db.add(instrument)
        
        db.commit()
        
        # Create sample strategy
        strategy = Strategy(
            id=uuid4(),
            name="MA Crossover Demo",
            description="Moving Average Crossover strategy for demo",
            owner_id=admin.id,
            strategy_type="MovingAverageCrossover",
            config={
                "short_window": 10,
                "long_window": 30,
                "rsi_period": 14,
                "rsi_oversold": 30,
                "rsi_overbought": 70
            },
            risk_params={
                "max_position_size": 100,
                "stop_loss_percent": 2.0,
                "daily_loss_limit": 5000
            },
            status=StrategyStatus.DRAFT,
            mode=TradingMode.PAPER
        )
        db.add(strategy)
        
        db.commit()
        
        print("✅ Seed data created successfully!")
        print(f"Admin user: admin@velox.com / admin123")
        print(f"Instruments: RELIANCE, TCS, INFY")
        print(f"Sample strategy: MA Crossover Demo")
    
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
