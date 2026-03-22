import os
import time
from sqlalchemy import create_engine, text

def get_engine():
    url = os.environ["NEON_URL"]
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=1800,
        connect_args={"sslmode": "require", "connect_timeout": 30}
    )

def release_daily_batch(batch_size: int = 1000):
    engine = get_engine()
    for attempt in range(3):
        try:
            with engine.connect() as conn:
                result = conn.execute(text("""
                    UPDATE retail_transactions
                    SET release_date = CURRENT_DATE
                    WHERE invoice IN (
                        SELECT invoice FROM retail_transactions
                        WHERE release_date IS NULL
                        ORDER BY invoicedate ASC
                        LIMIT :batch
                    )
                """), {"batch": batch_size})
                conn.commit()
                print(f"✓ Released {result.rowcount:,} new rows for today")
                return
        except Exception as e:
            print(f"Attempt {attempt+1}/3 failed: {e}")
            if attempt < 2:
                time.sleep(15)
            else:
                raise

if __name__ == "__main__":
    release_daily_batch()
