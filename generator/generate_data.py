"""Generate synthetic master data for a fictional company, 'Acme Precision Instruments'.

Everything is fake (Faker). Defects are injected on purpose, then fixed gradually
across six monthly snapshots so data quality trends can be analysed.
Output: CSV files in /data (regenerate any time: the seed makes it repeatable).
"""
import random
import re
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

SEED = 42
N_CUSTOMERS, N_MATERIALS, N_INSTALLED = 2500, 1200, 6000
SNAPSHOTS = [date(2026, 5, 31), date(2026, 6, 30), date(2026, 7, 31),
             date(2026, 8, 31), date(2026, 9, 30), date(2026, 10, 31)]
FIX_PROB = 0.18  # chance that an open defect gets fixed in each later month
OUT_DIR = Path(__file__).resolve().parent.parent / "data"

rng = random.Random(SEED)
Faker.seed(SEED)
fake = Faker()
LETTERS = "ABCDEFGHJKLMNPRSTUVWXYZ"

# code: (name, iso3, region, currency, postal pattern: # = digit, ? = letter)
COUNTRIES = {
    "PH": ("Philippines", "PHL", "APAC", "PHP", "####"),
    "SG": ("Singapore", "SGP", "APAC", "SGD", "######"),
    "JP": ("Japan", "JPN", "APAC", "JPY", "#######"),
    "AU": ("Australia", "AUS", "APAC", "AUD", "####"),
    "DE": ("Germany", "DEU", "EMEA", "EUR", "#####"),
    "FR": ("France", "FRA", "EMEA", "EUR", "#####"),
    "CH": ("Switzerland", "CHE", "EMEA", "CHF", "####"),
    "GB": ("United Kingdom", "GBR", "EMEA", "GBP", "?# #??"),
    "US": ("United States", "USA", "AMER", "USD", "#####"),
    "CA": ("Canada", "CAN", "AMER", "CAD", "?#? #?#"),
    "BR": ("Brazil", "BRA", "AMER", "BRL", "########"),
    "MX": ("Mexico", "MEX", "AMER", "MXN", "#####"),
}
INDUSTRIES = ["Pharma", "Food & Beverage", "Chemicals", "Laboratory & Research", "Logistics"]
PAYMENT_TERMS = ["NET30", "NET45", "NET60", "PREPAY"]
REGIONS = ["APAC", "EMEA", "AMER"]
REGION_LAG = {"APAC": 10, "EMEA": 18, "AMER": 25}  # max days a change request takes

# (base name, material type, product group, weight range in kg or None)
CATALOG = [
    ("Laboratory Balance", "INSTRUMENT", "LAB", (2, 12)),
    ("Precision Balance", "INSTRUMENT", "LAB", (3, 15)),
    ("Moisture Analyzer", "INSTRUMENT", "LAB", (5, 10)),
    ("pH Meter", "INSTRUMENT", "LAB", (0.3, 2)),
    ("Titrator", "INSTRUMENT", "LAB", (4, 9)),
    ("Industrial Scale", "INSTRUMENT", "INDUSTRIAL", (20, 150)),
    ("Checkweigher", "INSTRUMENT", "INSPECTION", (80, 400)),
    ("Metal Detector", "INSTRUMENT", "INSPECTION", (60, 300)),
    ("X-Ray Inspection System", "INSTRUMENT", "INSPECTION", (300, 900)),
    ("Calibration Weight Set", "ACCESSORY", "LAB", (0.5, 6)),
    ("Draft Shield", "ACCESSORY", "LAB", (0.2, 1)),
    ("Weighing Pan", "ACCESSORY", "LAB", (0.1, 0.8)),
    ("Load Cell", "SPARE_PART", "INDUSTRIAL", (0.5, 8)),
    ("Display Board", "SPARE_PART", "LAB", (0.1, 0.6)),
    ("Conveyor Belt", "SPARE_PART", "INSPECTION", (5, 40)),
    ("Calibration Service", "SERVICE", "SERVICE", None),
    ("Preventive Maintenance", "SERVICE", "SERVICE", None),
    ("Installation Service", "SERVICE", "SERVICE", None),
]

KEYS = {"customers": "customer_id", "materials": "material_id", "installed_base": "asset_id"}
DUP_PREFIX = {"customers": "C", "materials": "M", "installed_base": "A"}
RECORD_TYPE = {"customers": "CUSTOMER", "materials": "MATERIAL", "installed_base": "INSTALLED_BASE"}


def rand_date(start, end):
    return start + timedelta(days=rng.randint(0, (end - start).days))


def only_letters(text):
    return re.sub(r"[^a-z]", "", text.lower())


# ---------- 1. clean (defect-free) master data ----------
def build_customers():
    rows = []
    for i in range(1, N_CUSTOMERS + 1):
        code = rng.choice(list(COUNTRIES))
        _, _, region, currency, pattern = COUNTRIES[code]
        company = fake.company()
        domain = re.sub(r"[^a-z0-9]", "", company.lower())[:20] or "example"
        rows.append({
            "customer_id": f"C{i:06d}",
            "customer_name": company,
            "country_code": code,
            "region": region,
            "city": fake.city(),
            "postal_code": fake.bothify(pattern, letters=LETTERS),
            "tax_id": f"{code}-{fake.numerify('#########')}",
            "email": f"{only_letters(fake.first_name())}.{only_letters(fake.last_name())}@{domain}.com",
            "industry": rng.choice(INDUSTRIES),
            "payment_terms": rng.choice(PAYMENT_TERMS),
            "currency": currency,
            "sales_org": f"SO-{region}",
            "status": "BLOCKED" if rng.random() < 0.05 else "ACTIVE",
            "created_date": rand_date(date(2016, 1, 1), date(2025, 12, 31)),
        })
    return rows


def build_materials():
    rows = []
    for i in range(1, N_MATERIALS + 1):
        base, mtype, group, wrange = rng.choice(CATALOG)
        rows.append({
            "material_id": f"M{i:06d}",
            "description": f"{base} {fake.bothify('??-####', letters=LETTERS)}",
            "material_type": mtype,
            "product_group": group,
            "base_uom": "EA",
            "weight_kg": round(rng.uniform(*wrange), 2) if wrange else None,
        })
    return rows


def build_installed_base(customers, materials):
    instruments = [m for m in materials if m["material_type"] == "INSTRUMENT"]
    rows = []
    for i in range(1, N_INSTALLED + 1):
        cust = rng.choice(customers)
        install = rand_date(cust["created_date"], date(2026, 3, 31))
        last_cal = rand_date(install, date(2026, 4, 30))
        rows.append({
            "asset_id": f"A{i:06d}",
            "serial_number": f"SN{i:09d}",
            "material_id": rng.choice(instruments)["material_id"],
            "customer_id": cust["customer_id"],
            "install_date": install,
            "warranty_end_date": install + timedelta(days=730),
            "last_calibration_date": last_cal,
            "next_calibration_due": last_cal + timedelta(days=365),
        })
    return rows


# ---------- 2. defect injectors: each one mutates a copy of a clean row ----------
def d_missing_tax(r, g): r["tax_id"] = None
def d_bad_email(r, g):
    e = r["email"]
    r["email"] = g.choice([e.replace("@", ""), e.replace(".com", ""), e.replace("@", "@@")])
def d_country_format(r, g):
    name, iso3 = COUNTRIES[r["country_code"]][:2]
    r["country_code"] = g.choice([iso3, name, name.upper()])
def d_bad_postal(r, g):
    p = r["postal_code"]
    r["postal_code"] = g.choice([p + "9", p[:-1], "N/A"])
def d_currency(r, g):
    r["currency"] = g.choice([c for c in ("USD", "EUR", "JPY", "CHF") if c != r["currency"]])
def d_payment(r, g): r["payment_terms"] = g.choice(["Net 30", "30 days", "N30", "net45", "60D"])
def d_missing_uom(r, g): r["base_uom"] = None
def d_bad_uom(r, g): r["base_uom"] = g.choice(["PCS", "PIECE", "ea", "Each"])
def d_missing_weight(r, g): r["weight_kg"] = g.choice([None, 0])
def d_orphan(r, g): r["customer_id"] = f"C9{g.randint(0, 99999):05d}"  # no such customer
def d_cal_before(r, g): r["next_calibration_due"] = r["install_date"] - timedelta(days=g.randint(1, 400))


def dup_customer(r, new_id, g):
    d = dict(r)
    d["customer_id"] = new_id
    d["customer_name"] = g.choice([r["customer_name"].upper(), r["customer_name"] + " Ltd",
                                   r["customer_name"].replace(",", "")])
    return d


def dup_material(r, new_id, g):
    d = dict(r)
    d["material_id"] = new_id
    return d


def dup_installed(r, new_id, g):
    d = dict(r)
    d["asset_id"] = new_id  # same serial number, new asset id
    return d


# table -> [(defect type, probability(clean row), injector, field it changes)]
SPECS = {
    "customers": [
        ("MISSING_TAX_ID", lambda r: 0.15 if r["country_code"] in ("PH", "BR", "MX") else 0.03, d_missing_tax, "tax_id"),
        ("INVALID_EMAIL", lambda r: 0.03, d_bad_email, "email"),
        ("COUNTRY_FORMAT", lambda r: 0.05, d_country_format, "country_code"),
        ("INVALID_POSTAL_CODE", lambda r: 0.03, d_bad_postal, "postal_code"),
        ("CURRENCY_MISMATCH", lambda r: 0.02, d_currency, "currency"),
        ("PAYMENT_TERMS_FORMAT", lambda r: 0.06, d_payment, "payment_terms"),
    ],
    "materials": [
        ("MISSING_UOM", lambda r: 0.03, d_missing_uom, "base_uom"),
        ("INVALID_UOM", lambda r: 0.03, d_bad_uom, "base_uom"),
        ("MISSING_WEIGHT", lambda r: 0.06 if r["weight_kg"] is not None else 0, d_missing_weight, "weight_kg"),
    ],
    "installed_base": [
        ("ORPHAN_CUSTOMER", lambda r: 0.02, d_orphan, "customer_id"),
        ("CALIBRATION_BEFORE_INSTALL", lambda r: 0.02, d_cal_before, "next_calibration_due"),
    ],
}
DUPLICATES = {  # table -> (defect type, probability, builder)
    "customers": ("DUPLICATE_CUSTOMER", 0.03, dup_customer),
    "materials": ("DUPLICATE_MATERIAL", 0.02, dup_material),
    "installed_base": ("DUPLICATE_SERIAL", 0.015, dup_installed),
}


def draw_fix_index():
    """Snapshot index (1..5) in which a defect gets fixed, or None if it never is."""
    for s in range(1, len(SNAPSHOTS)):
        if rng.random() < FIX_PROB:
            return s
    return None


def is_active(event, s):
    return event["fixed"] is None or s < event["fixed"]


# ---------- 3. decide which records get which defects ----------
def assign_defects(table, clean_rows):
    pk = KEYS[table]
    events, dup_count = [], 0
    for r in clean_rows:
        region = r.get("region") or rng.choice(REGIONS)
        used = set()
        for defect, prob, fn, field in SPECS[table]:
            if field in used or rng.random() >= prob(r):
                continue
            used.add(field)
            events.append(dict(table=table, record_id=r[pk], defect=defect, kind="field",
                               fn=fn, fixed=draw_fix_index(), region=region))
        dup_type, dup_prob, dup_fn = DUPLICATES[table]
        if rng.random() < dup_prob:
            dup_count += 1
            new_id = f"{DUP_PREFIX[table]}{900000 + dup_count}"
            events.append(dict(table=table, record_id=new_id, defect=dup_type, kind="dup",
                               dup_row=dup_fn(r, new_id, random.Random(new_id)),
                               fixed=draw_fix_index(), region=region))
    return events


# ---------- 4. build the monthly snapshots ----------
def build_snapshots(table, clean_rows, events):
    pk = KEYS[table]
    field_events = defaultdict(list)
    for e in events:
        if e["kind"] == "field":
            field_events[e["record_id"]].append(e)
    rows, truth = [], []
    for s, snap in enumerate(SNAPSHOTS):
        for r in clean_rows:
            row = dict(r)
            for e in field_events.get(r[pk], []):
                if is_active(e, s):
                    e["fn"](row, random.Random(f"{r[pk]}-{e['defect']}"))
                    truth.append((snap, table, r[pk], e["defect"]))
            row["snapshot_date"] = snap
            rows.append(row)
        for e in events:
            if e["kind"] == "dup" and is_active(e, s):
                row = dict(e["dup_row"])
                row["snapshot_date"] = snap
                rows.append(row)
                truth.append((snap, table, e["record_id"], e["defect"]))
    return rows, truth


# ---------- 5. the data steward queue (change requests) ----------
def build_change_requests(all_events):
    rows = []
    for e in all_events:
        closed = e["fixed"] is not None
        if not closed and rng.random() > 0.35:  # only some open defects have a request yet
            continue
        if closed:
            resolved = SNAPSHOTS[e["fixed"]] - timedelta(days=rng.randint(0, 5))
            created = resolved - timedelta(days=rng.randint(1, REGION_LAG[e["region"]]))
            status = "CLOSED"
        else:
            span = (SNAPSHOTS[-1] - SNAPSHOTS[0]).days
            created = SNAPSHOTS[0] + timedelta(days=rng.randint(0, span))
            resolved, status = None, rng.choice(["OPEN", "IN_PROGRESS"])
        rows.append({
            "request_id": f"CR{len(rows) + 1:06d}",
            "record_type": RECORD_TYPE[e["table"]],
            "record_id": e["record_id"],
            "reason": e["defect"],
            "region": e["region"],
            "priority": rng.choices(["LOW", "MEDIUM", "HIGH"], weights=[50, 35, 15])[0],
            "created_date": created,
            "resolved_date": resolved,
            "status": status,
        })
    return rows


def main():
    OUT_DIR.mkdir(exist_ok=True)
    customers = build_customers()
    materials = build_materials()
    installed = build_installed_base(customers, materials)
    clean = {"customers": customers, "materials": materials, "installed_base": installed}

    all_events, truth = [], []
    for table, rows in clean.items():
        events = assign_defects(table, rows)
        snapshot_rows, table_truth = build_snapshots(table, rows, events)
        pd.DataFrame(snapshot_rows).to_csv(OUT_DIR / f"{table}.csv", index=False)
        all_events += events
        truth += table_truth
        print(f"{table}: {len(snapshot_rows):,} rows across {len(SNAPSHOTS)} snapshots")

    cr = pd.DataFrame(build_change_requests(all_events))
    cr.to_csv(OUT_DIR / "change_requests.csv", index=False)
    print(f"change_requests: {len(cr):,} rows")

    truth_df = pd.DataFrame(truth, columns=["snapshot_date", "table_name", "record_id", "defect_type"])
    truth_df.to_csv(OUT_DIR / "ground_truth_defects.csv", index=False)
    print(f"ground_truth_defects: {len(truth_df):,} rows")


if __name__ == "__main__":
    main()