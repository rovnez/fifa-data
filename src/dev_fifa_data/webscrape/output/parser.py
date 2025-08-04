import re
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import parse_qs, urlparse

from dev_fifa_data.webscrape.scraper_repository import TestScraperRepository

scraper_repo = TestScraperRepository()
html = scraper_repo.get_page_content('some_url', name='MESSI_23')

big_soup = BeautifulSoup(html, "html.parser")


def parse_position_ratings(soup) -> dict:
    # assert length is 24
    # assert keys
    # assert format = 'value + value'
    positions = {}
    for box in soup.select("aside .calculated div.pos"):
        code = box.find(string=True, recursive=False).strip()
        em = box.find("em")
        rating = em.get_text(strip=True)
        positions[code] = rating
    return positions


STAT_HEADINGS = {
    "Attacking", "Skill", "Movement", "Power",
    "Mentality", "Defending", "Goalkeeping",
}

STAT_SPECIAL_HEADINGS = {
    "Traits", "PlayStyles",
}

INFO_HEADINGS = {
    'Club', 'National team', 'Player specialities', 'Profile'
}


def split_attribute_grids(soup):
    info_grids, stat_grids = [], []
    for g in soup.select("div.grid.attribute"):
        heads = {h.get_text(strip=True) for h in g.select("h5")}
        if heads & STAT_HEADINGS:
            stat_grids.append(g)
        elif heads & INFO_HEADINGS:
            info_grids.append(g)
        else:
            # for example: FC 25, skips 'Roles'
            print(f"Unknown headings: {heads}")
    return info_grids, stat_grids


def parse_stat_grid(grid):
    out = {}
    for col in grid.select(":scope > .col"):
        heading = col.h5.get_text(strip=True)
        if heading in STAT_HEADINGS:
            stats = []
            for p in col.find_all("p", recursive=False):
                em = p.find("em")
                if not em:
                    continue
                raw = em.get("title", em.get_text(strip=True))
                value = int(re.match(r"\d+", raw).group())

                spans = p.find_all("span")
                label = spans[-1].get_text(strip=True) if spans else p.get_text(strip=True)
                stats.append({"name": label, "value": value})
            out[heading] = stats
        elif heading in STAT_SPECIAL_HEADINGS:
            styles = []
            for span in col.select('p > span[data-tippy-content]'):
                name = re.sub(r'\s*\+$', '', span.get_text(strip=True))  # drop trailing “+”
                styles.append(name)
            out[heading] = set(styles)
    return out


def extract_point_stats(soup):
    # 1) grab the inline <script> that holds the POINT_* vars
    script_tag = soup.find('script', string=lambda s: s and 'POINT_' in s)
    if not script_tag:
        return {}

    js = script_tag.string

    # 2) pull out ALL assignments in that var statement
    #    e.g. POINT_DEF=33  or OVERALL='Overall'
    assignments = dict(
        (k, v.strip().strip('"\''))
        for k, v in re.findall(r'([A-Z_]+)\s*=\s*([^,;]+)', js)
    )

    # 3) keep only the POINT_* ones and cast to int
    return {
        k.replace('POINT_', ''): int(v)
        for k, v in assignments.items()
        if k.startswith('POINT_')
    }


# ---------- INFO / META ----------
def parse_info_grid(grid):
    out = {}
    for col in grid.select(":scope > .col"):
        section = col.h5.get_text(strip=True)

        # Special-case: Player specialities
        if section.lower().startswith("player special"):
            out[section] = extract_specialities(col)
            continue

        section_dict = {}
        for p in col.find_all("p", recursive=False):
            label_tag = p.find("label")
            if not label_tag:
                continue

            key = label_tag.get_text(strip=True)

            # value AFTER the label
            after_parts = []
            for node in label_tag.next_siblings:
                if isinstance(node, NavigableString):
                    t = node.strip()
                    if t:
                        after_parts.append(t)
                else:
                    after_parts.append(node.get_text(" ", strip=True))
            after_val = " ".join(after_parts).strip() or None

            # value BEFORE the label (stars/snippets)
            before_text = p.get_text(" ", strip=True)
            m = re.match(r"^(\d+)\b", before_text)
            before_val = int(m.group(1)) if m else None

            if before_val is not None and key.lower() in {"skill moves", "weak foot", "international reputation"}:
                value = before_val
            else:
                value = after_val

            section_dict[key] = value

        out[section] = section_dict
    return out


def extract_specialities(col):
    specs = []
    for a in col.select("p > a"):
        name = a.get_text(strip=True).lstrip("#")
        qs = parse_qs(urlparse(a.get("href", "")).query)
        code = int(qs.get("sc[]", [None])[0]) if qs.get("sc[]") else None
        specs.append({"name": name, "code": code})
    return specs


def extract_specialities(col):
    specs = []
    for a in col.select("p > a"):
        name = a.get_text(strip=True).lstrip("#")
        qs = parse_qs(urlparse(a.get("href", "")).query)
        code = int(qs.get("sc[]", [None])[0]) if qs.get("sc[]") else None
        specs.append({"name": name, "code": code})
    return specs


import re
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString

DATE_FMT = "%b %d, %Y"  # e.g. "Jul 16, 2023"


def _text_after_label(p, css_sel=None, default=None):
    """Return clean text after <label> inside <p>. Optionally pull text from a css_sel under that <p>."""
    label = p.find("label")
    if not label:
        return default
    if css_sel:
        node = p.select_one(css_sel)
        if node:
            return node.get_text(strip=True)
    parts = []
    for sib in label.next_siblings:
        if isinstance(sib, NavigableString):
            t = sib.strip()
            if t:
                parts.append(t)
        else:
            parts.append(sib.get_text(" ", strip=True))
    return " ".join(parts).strip() or default


def _int_from_href(href, pattern):
    m = re.search(pattern, href)
    return int(m.group(1)) if m else None


def extract_club_info(col):
    # Club & league rows (first two <p> with <a>)
    team_a = col.select_one("p > a[href*='/team/']")
    league_a = col.select_one("p > a[href*='/league/']")

    club_team_id = _int_from_href(team_a["href"], r"/team/(\d+)/")
    club_name = team_a.get_text(strip=True)

    league_id = _int_from_href(league_a["href"], r"/league/(\d+)")
    league_name = league_a.get_text(strip=True)

    # Stars/overall row (3rd <p>) we ignore unless you want it; not needed for requested cols
    # Position / kit / joined / contract / loaned from
    data = {
        "league_id": league_id,
        "league_name": league_name,
        "league_level": None,  # fill later; see below
        "club_team_id": club_team_id,
        "club_name": club_name,
        "club_position": None,
        "club_jersey_number": None,
        "club_loaned_from": None,
        "club_joined_date": None,
        "club_contract_valid_until_year": None,
    }

    # iterate remaining <p> rows with <label>
    for p in col.find_all("p"):
        lab = p.find("label")
        if not lab:
            continue
        key = lab.get_text(strip=True).lower()
        if key == "position":
            data["club_position"] = _text_after_label(p, css_sel=".pos")
        elif key == "kit number":
            v = _text_after_label(p)
            data["club_jersey_number"] = int(re.search(r"\d+", v).group()) if v else None
        elif key in {"joined", "transfer date"}:
            v = _text_after_label(p)
            try:
                data["club_joined_date"] = datetime.strptime(v, DATE_FMT).date().isoformat()
            except Exception:
                data["club_joined_date"] = v  # keep raw if parse fails
        elif key == "contract valid until":
            v = _text_after_label(p)
            m = re.search(r"\d{4}", v or "")
            data["club_contract_valid_until_year"] = int(m.group()) if m else None
        elif key in {"loaned from", "on loan from"}:
            data["club_loaned_from"] = _text_after_label(p)

    return data


DATE_FMT = "%b %d, %Y"  # "Jul 16, 2023"


# ---------- small helpers ----------

def _int_from_href(href, pattern):
    m = re.search(pattern, href)
    return int(m.group(1)) if m else None


def _text_after_label(p, css_sel=None, default=None):
    lab = p.find("label")
    if not lab:
        return default
    if css_sel:
        node = p.select_one(css_sel)
        if node:
            return node.get_text(strip=True)
    parts = []
    for sib in lab.next_siblings:
        if isinstance(sib, NavigableString):
            t = sib.strip()
            if t:
                parts.append(t)
        else:
            parts.append(sib.get_text(" ", strip=True))
    return " ".join(parts).strip() or default


# ---------- nationality from header (optional but handy) ----------

def extract_primary_nationality(soup):
    a = soup.select_one('.profile p a[href*="/players?na="]')
    if not a:
        return {"nationality_id": None, "nationality_name": None}
    nat_id = _int_from_href(a["href"], r"na=(\d+)")
    nat_name = a.get("title") or a.get_text(strip=True)
    return {"nationality_id": nat_id, "nationality_name": nat_name}


# ---------- National team block ----------

def extract_national_team_info(col):
    # first <p> with /team/ = national team row
    team_a = col.select_one("p > a[href*='/team/']")
    league_a = col.select_one("p > a[href*='/league/']")  # may be useful if you store nation_league_id/name

    nation_team_id = _int_from_href(team_a["href"], r"/team/(\d+)/")
    nation_name = team_a.get_text(strip=True)

    data = {
        "nation_team_id": nation_team_id,
        "nationality_id": None,  # will be filled by extract_primary_nationality
        "nationality_name": None,
        "nation_position": None,
        "nation_jersey_number": None,
    }

    # rows with labels
    for p in col.find_all("p"):
        lab = p.find("label")
        if not lab:
            continue
        key = lab.get_text(strip=True).lower()
        if key == "position":
            data["nation_position"] = _text_after_label(p, css_sel=".pos")
        elif key == "kit number":
            val = _text_after_label(p)
            m = re.search(r"\d+", val or "")
            data["nation_jersey_number"] = int(m.group()) if m else None

    return data


# ---------- tie it together ----------

def parse_national_section(html):
    soup = BeautifulSoup(html, "html.parser")
    nat_block = soup.select_one("div.grid.attribute div.col:has(h5:-soup-contains('National team'))")
    nation = extract_national_team_info(nat_block) if nat_block else {}
    primary_nat = extract_primary_nationality(soup)
    nation.update({k: v for k, v in primary_nat.items() if k in nation})
    return nation


nat_block = big_soup.select_one("div.grid.attribute div.col:has(h5:-soup-contains('National team'))")
nation = extract_national_team_info(nat_block) if nat_block else {}
primary_nat = extract_primary_nationality(big_soup)
nation.update({k: v for k, v in primary_nat.items() if k in nation})

club_col = big_soup.select_one("div.grid.attribute div.col:has(h5:-soup-contains('Club'))")
club_info = extract_club_info(club_col)

big_summary_stats = extract_point_stats(big_soup)

big_info_grids, big_stat_grids = split_attribute_grids(big_soup)

info = {}
for g in big_info_grids:
    info.update(parse_info_grid(g))

big_stats = {}
for g in big_stat_grids:
    big_stats.update(parse_stat_grid(g))

dat = parse_position_ratings(big_soup)


# %% GET EXOTICS

def get_name(soup):
    val = soup.find_all(class_='ellipsis')
    return val[0].text


# assert length = 1

ut = big_soup.find('ellipses')

# %% GET MAIN INFO

import re, json
from datetime import datetime, date

CUR_RX = re.compile(r"€\s*([\d\.]+)\s*([MK]?)", re.I)
AGE_RX = re.compile(r"(\d+)\s*y\.o\.", re.I)
DOB_RX = re.compile(r"\(([^)]+)\)")  # date in parentheses
HT_RX = re.compile(r"(\d+)\s*cm", re.I)
WT_RX = re.compile(r"(\d+)\s*kg", re.I)


def _eur_to_int(txt: str | None) -> int | None:
    if not txt:
        return None
    m = CUR_RX.search(txt)
    if not m:
        return None
    num, suf = m.groups()
    num = float(num.replace(".", ""))  # "41" or "1.2"
    mul = {"M": 1_000_000, "K": 1_000}.get(suf.upper(), 1)
    return int(num * mul)


def _parse_date(d: str, fmt="%b %d, %Y") -> str | None:
    try:
        return datetime.strptime(d.strip(), fmt).date().isoformat()
    except Exception:
        return None


def _safe_int(m):
    return int(m.group(1)) if m else None


def extract_from_profile_block(block):
    # long_name
    long_name = block.select_one("h1").get_text(strip=True)

    # positions (all span.pos in the <p> under .profile)
    positions = [s.get_text(strip=True) for s in block.select("p span.pos")]

    # age/dob/height/weight line is the <p> after <h1>
    info_p = block.select_one("h1 + p")
    info_txt = " ".join(info_p.stripped_strings)

    age = _safe_int(AGE_RX.search(info_txt))
    dob_raw = DOB_RX.search(info_txt).group(1)
    dob = _parse_date(dob_raw)
    height_cm = _safe_int(HT_RX.search(info_txt))
    weight_kg = _safe_int(WT_RX.search(info_txt))

    return {
        "long_name": long_name,
        "player_positions": positions,
        "age": age,
        "dob": dob,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
    }


def extract_ratings_value_wage(soup, profile_block):
    # first .grid after that profile block
    grid = profile_block.find_next("div", class_="grid")
    metrics = {}
    for col in grid.select(":scope > .col"):
        sub = col.select_one(".sub")
        if not sub:
            continue
        key = sub.get_text(strip=True)
        # overall/potential sit in <em title="..">
        em = col.em
        val = em.get("title") or em.get_text(strip=True)
        metrics[key] = val

    overall = int(metrics["Overall rating"])
    potential = int(metrics["Potential"])
    value_eur = _eur_to_int(metrics["Value"])
    wage_eur = _eur_to_int(metrics["Wage"])

    return {
        "overall": overall,
        "potential": potential,
        "value_eur": value_eur,
        "wage_eur": wage_eur,
    }


def extract_header_fields(soup, today: date | None = None):

    # Prefer the first article/profile (page repeats it)
    profile_block = soup.select_one("article .profile")
    if not profile_block:
        raise ValueError("Profile block not found")

    data = extract_from_profile_block(profile_block)
    data.update(extract_ratings_value_wage(soup, profile_block))

    # Optional: recalc age from dob if 'today' provided (keeps your DB consistent over time)
    if today and data["dob"]:
        dob = datetime.fromisoformat(data["dob"]).date()
        data["age"] = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    # Optional fallback/validation from JSON-LD
    ld = soup.find("script", type="application/ld+json")
    if ld:
        try:
            js = json.loads(ld.string)
            data.setdefault("long_name", js.get("givenName", "") + " " + js.get("familyName", "") or data["long_name"])
            data.setdefault("dob", js.get("birthDate"))
            if js.get("height"):
                m = HT_RX.search(js["height"])
                if m:
                    data.setdefault("height_cm", int(m.group(1)))
            if js.get("weight"):
                m = WT_RX.search(js["weight"])
                if m:
                    data.setdefault("weight_kg", int(m.group(1)))
            # value_eur in ld["netWorth"] could be used too
        except Exception:
            pass

    # Final normalize player_positions to CSV string (if you need TEXT column)
    data["player_positions"] = ",".join(data["player_positions"])

    return data


# ---- usage ----
# html = open("messi.html").read()
# row = extract_header_fields(html, today=date.today())
# print(row)

# %%
ret = extract_header_fields(big_soup, today=None)
