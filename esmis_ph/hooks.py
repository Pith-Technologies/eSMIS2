import csv
import logging
import os
from datetime import datetime

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Bulk-load barangay records from CSV using raw SQL batch inserts.

    Skips if barangays are already present to make the hook idempotent.
    Uses psycopg2 execute_values for efficient bulk insertion rather than
    ORM create(), which would be prohibitively slow for ~42,000 records.
    """
    csv_path = os.path.join(os.path.dirname(__file__), "data", "psgc", "barangays.csv")
    if not os.path.exists(csv_path):
        _logger.warning("PSGC barangay CSV not found at %s", csv_path)
        return

    cr = env.cr

    cr.execute("SELECT COUNT(*) FROM esmis_psgc_barangay")
    if cr.fetchone()[0] > 0:
        _logger.info("PSGC barangays already loaded, skipping.")
        return

    _logger.info("Loading PSGC barangays from CSV...")

    cr.execute("SELECT psgc_code, id FROM esmis_psgc_city_municipality")
    city_map = dict(cr.fetchall())

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        batch = []
        skipped = 0
        for row in reader:
            cm_id = city_map.get(row["city_municipality_psgc_code"])
            if cm_id:
                batch.append((row["name"], row["psgc_code"], cm_id))
            else:
                skipped += 1

    if skipped:
        _logger.warning(
            "Skipped %d barangay rows: city_municipality_psgc_code not found in loaded data.",
            skipped,
        )

    if batch:
        from psycopg2.extras import execute_values

        now = datetime.now()
        execute_values(
            cr,
            """INSERT INTO esmis_psgc_barangay
               (name, psgc_code, city_municipality_id, create_uid, write_uid,
                create_date, write_date)
               VALUES %s""",
            [(name, code, cm_id, 1, 1, now, now) for name, code, cm_id in batch],
            page_size=5000,
        )
        _logger.info("Loaded %d barangay records.", len(batch))
    else:
        _logger.warning("No barangay records were loaded from CSV.")
