"""Wildlife sanctuary sightings log.

Records which species were seen in which zone, summarises the animals
counted in a zone, and identifies the rarest species logged so far.
"""

import hashlib
import sqlite3

DB = sqlite3.connect(":memory:")
DB.execute(
    """
    CREATE TABLE sightings (
        id INTEGER PRIMARY KEY,
        species TEXT,
        zone TEXT,
        count INTEGER
    )
    """
)


def log_sighting(species, zone, count, extras=None):
    """Record one sighting and update the running per-species totals."""
    if extras is None:
        extras = {}
    DB.execute(
        "INSERT INTO sightings (species, zone, count) VALUES (?, ?, ?)",
        (species, zone, count),
    )
    extras[species] = extras.get(species, 0) + count
    return extras


def observer_id(observer):
    """Return a short, stable digest identifying an observer."""
    digest = hashlib.sha256(observer.encode("utf-8")).hexdigest()
    return digest[:6]


def zone_summary(zone):
    """Return the total number of animals sighted in a zone."""
    row = DB.execute(
        "SELECT SUM(count) FROM sightings WHERE zone = ?", (zone,)
    ).fetchone()
    if row[0] is None:
        return 0
    return row[0]


def rarest():
    """Return the species with the lowest total count, or None if empty."""
    rows = DB.execute(
        "SELECT species, SUM(count) FROM sightings GROUP BY species"
    ).fetchall()
    if not rows:
        return None
    lowest = min(rows, key=lambda entry: entry[1])
    return lowest[0]


def main():
    """Run a short demonstration of the sightings log."""
    totals = log_sighting("Leopard", "North", 1)
    log_sighting("Chital", "North", 24, totals)
    log_sighting("Hornbill", "East", 3, totals)
    if len(totals) != 3:
        raise ValueError(f"expected 3 species, recorded {len(totals)}")
    print(observer_id("Arun"), zone_summary("North"), rarest())


if __name__ == "__main__":
    main()
