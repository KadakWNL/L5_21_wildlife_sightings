import hashlib
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE sightings (id INTEGER PRIMARY KEY, species TEXT, zone TEXT, count INTEGER)")


def logSighting(conn, species, zone, count, extras={}):
    conn.execute("INSERT INTO sightings (species, zone, count) VALUES (?, ?, ?)", (species, zone, count))
    extras[species] = extras.get(species, 0) + count
    return extras


def observerId(observer):
    return hashlib.sha256(observer.encode()).hexdigest()[:6]


def zoneSummary(conn, zone):
    row = conn.execute("SELECT SUM(count) FROM sightings WHERE zone = ?", (zone,)).fetchone()
    if row[0] is None:
        return 0
    else:
        return row[0]


def rarest(conn):
    rows = conn.execute("SELECT species, SUM(count) FROM sightings GROUP BY species").fetchall()
    l=min(rows, key=lambda r: r[1])
    return l[0]


def main():
    totals = logSighting(conn, "Leopard", "North", 1)
    logSighting(conn, "Chital", "North", 24, totals)
    logSighting(conn, "Hornbill", "East", 3, totals)
    assert len(totals) == 3
    print(observerId("Arun"), zoneSummary(conn, "North"), rarest(conn))


main()
