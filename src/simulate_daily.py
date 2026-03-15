import os
from sqlalchemy import create_engine, text

def release_daily_batch(batch_size: int = 500):
    if "SUPABASE_URL" not in os.environ and 'SUPABASE_URL' in globals():
        os.environ["SUPABASE_URL"] = globals()['SUPABASE_URL']

    engine = create_engine(os.environ["SUPABASE_URL"])
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
        print(f"✓ Released {result.rowcount} new rows for today")

if __name__ == "__main__":
    release_daily_batch()
