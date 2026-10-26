import hashlib
import sqlite3

DB = sqlite3.connect(":memory:")
DB.execute("CREATE TABLE sightings (id INTEGER PRIMARY KEY, species TEXT, zone TEXT, count INTEGER)")


def logSighting(species, zone, count, extras=None):
    if extras is None:
        extras = {}
    DB.execute("INSERT INTO sightings (species, zone, count) VALUES (?, ?, ?)", (species, zone, count))
    extras[species] = extras.get(species, 0) + count
    return extras


def observerId(observer):
    return hashlib.sha256(observer.encode()).hexdigest()[:6]


def zoneSummary(zone):
    row = DB.execute("SELECT SUM(count) FROM sightings WHERE zone = ?", (zone,)).fetchone()
    if row[0] is None:
        return 0
    return row[0]


def rarest():
    rows = DB.execute("SELECT species, SUM(count) FROM sightings GROUP BY species").fetchall()
    l=min(rows, key=lambda r: r[1])
    return l[0]


def main():
    totals = logSighting("Leopard", "North", 1)
    logSighting("Chital", "North", 24, totals)
    logSighting("Hornbill", "East", 3, totals)
    if len(totals) != 3:
        raise ValueError(f"expected 3 species, recorded {len(totals)}")
    print(observerId("Arun"), zoneSummary("North"), rarest())


main()
