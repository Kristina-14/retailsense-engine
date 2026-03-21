# import os
# from sqlalchemy import create_engine, text

# def release_daily_batch(batch_size: int = 500):
#     if "SUPABASE_URL" not in os.environ and 'SUPABASE_URL' in globals():
#         os.environ["SUPABASE_URL"] = globals()['SUPABASE_URL']

#     engine = create_engine(os.environ["SUPABASE_URL"])
#     with engine.connect() as conn:
#         result = conn.execute(text("""
#             UPDATE retail_transactions
#             SET release_date = CURRENT_DATE
#             WHERE invoice IN (
#                 SELECT invoice FROM retail_transactions
#                 WHERE release_date IS NULL
#                 ORDER BY invoicedate ASC
#                 LIMIT :batch
#             )
#         """), {"batch": batch_size})
#         conn.commit()
#         print(f"✓ Released {result.rowcount} new rows for today")

# if __name__ == "__main__":
#     release_daily_batch()

import os
import time
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

def get_engine():
    password = quote_plus(os.environ["SUPABASE_PASSWORD"])
    url = (
        f"postgresql://postgres.gsqizlwftqumpjhcmmzk:{password}"
        f"@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"
    )
    return create_engine(url, pool_pre_ping=True)

def release_daily_batch(batch_size: int = 500):
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
                        ORDER BY invoice_date ASC
                        LIMIT :batch
                    )
                """), {"batch": batch_size})
                conn.commit()
                print(f"✓ Released {result.rowcount} new rows for today")
                return
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                print("Retrying in 15 seconds...")
                time.sleep(15)
            else:
                raise

if __name__ == "__main__":
    release_daily_batch()
