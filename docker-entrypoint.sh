#!/bin/bash
set -e

echo "Waiting for database..."
python -c "
import time, os
from sqlalchemy import create_engine, text
url = os.getenv('DATABASE_URL', 'postgresql://workpulse:workpulse_secret@db:5432/workpulse_db')
for i in range(30):
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        print('Database ready.')
        break
    except Exception:
        time.sleep(2)
else:
    raise SystemExit('Database not available')
"

python -m database.init_db --seed

exec "$@"
