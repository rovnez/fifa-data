# player_parser.py
from bs4 import BeautifulSoup
from scraper import get_page_content
from utils import format_date  # expects 'Jul 21, 2000' -> '2000-07-21'

url = 'https://sofifa.com/player/155862/200061/'
html = get_page_content(url)

import re
from urllib.parse import parse_qs, urlparse
from bs4 import BeautifulSoup, NavigableString

STAT_HEADINGS = {
    "Attacking","Skill","Movement","Power",
    "Mentality","Defending","Goalkeeping","Traits"
}

def split_attribute_grids(soup):
    info_grids, stat_grids = [], []
    for g in soup.select("div.grid.attribute"):
        heads = {h.get_text(strip=True) for h in g.select("h5")}
        if heads & STAT_HEADINGS:
            stat_grids.append(g)
        else:
            info_grids.append(g)
    return info_grids, stat_grids

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

            if before_val is not None and key.lower() in {"skill moves","weak foot","international reputation"}:
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
        qs = parse_qs(urlparse(a.get("href","")).query)
        code = int(qs.get("sc[]",[None])[0]) if qs.get("sc[]") else None
        specs.append({"name": name, "code": code})
    return specs

# ---------- STATS ----------
def parse_stat_grid(grid):
    out = {}
    for col in grid.select(":scope > .col"):
        heading = col.h5.get_text(strip=True)
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
    return out

# ---------- POSITIONS ----------
def extract_position_ratings(soup):
    positions = {}
    for box in soup.select("aside .calculated div.pos"):
        code = box.find(text=True, recursive=False).strip()
        em = box.find("em")
        raw = (em.get("title") or em.get_text(strip=True))
        rating = int(re.match(r"\d+", raw).group())
        positions[code] = rating

    best_pos_label = soup.select_one("div.attribute p label:-soup-contains-own('Best position')")
    best_ovr_label = soup.select_one("div.attribute p label:-soup-contains-own('Best overall')")

    return {
        "positions": positions,
        "best_position": best_pos_label.parent.select_one(".pos").get_text(strip=True) if best_pos_label else None,
        "best_overall": int(best_ovr_label.parent.em["title"]) if best_ovr_label else None
    }

# ---------- MASTER ----------
def parse_player(html):
    soup = BeautifulSoup(html, "html.parser")

    info_grids, stat_grids = split_attribute_grids(soup)

    info = {}
    for g in info_grids:
        info.update(parse_info_grid(g))

    stats = {}
    for g in stat_grids:
        stats.update(parse_stat_grid(g))

    pos = extract_position_ratings(soup)

    return {"info": info, "stats": stats, **pos}


result = parse_player(html)
result["info"]["Profile"]["Preferred foot"]        # "Right"
result["info"]["Profile"]["Skill moves"]           # 3
result["info"]["Club"]["Position"]                 # "LCB"
result["stats"]["Attacking"][0]                    # {'name': 'Crossing', 'value': 66}
result["positions"]["RB"]                          # 86
result["best_position"]                            # "RB"

ROW_HEADER = [
    "player_id", "version", "name", "full_name", "description", "image", "height_cm", "weight_kg", "dob", "positions",
    "overall_rating", "potential", "value", "wage",
    "preferred_foot", "weak_foot", "skill_moves", "international_reputation", "work_rate", "body_type", "real_face", "release_clause",
    "specialities",
    "club_id", "club_name", "club_league_id", "club_league_name", "club_logo", "club_rating", "club_position", "club_kit_number", "club_joined",
    "club_contract_valid_until",
    "country_id", "country_name", "country_league_id", "country_league_name", "country_flag", "country_rating", "country_position", "country_kit_number",
    "crossing", "finishing", "heading_accuracy", "short_passing", "volleys",
    "dribbling", "curve", "fk_accuracy", "long_passing", "ball_control",
    "acceleration", "sprint_speed", "agility", "reactions", "balance",
    "shot_power", "jumping", "stamina", "strength", "long_shots",
    "aggression", "interceptions", "positioning", "vision", "penalties", "composure",
    "defensive_awareness", "standing_tackle", "sliding_tackle",
    "gk_diving", "gk_handling", "gk_kicking", "gk_positioning", "gk_reflexes",
    "play_styles"
]


def parse_player(url: str):
    html = get_page_content(url)
    soup = BeautifulSoup(html, "html.parser")

    data = extract_all_skill_blocks(html)
    attacking = {s["name"]: s["value"] for s in data["Attacking"]}

    player_id = url.split("/")[4]

    description = _attr(soup.select_one('meta[name=description]'), "content")
    version = format_date(_text(soup.select_one('select[name=roster] option[selected]')))

    article = soup.select_one("main article")
    profile = article.select_one(".profile") if article else None

    name = (_text(soup.title).split(" FC ")[0]).strip() if soup.title else ""
    full_name = _text(profile.select_one("h1")) if profile else ""
    image = _attr(profile.select_one("img"), "data-src") if profile else ""

    profile_text = _text(profile.select_one("p")) if profile else ""

    dob = format_date(_regex_first(profile_text, r"\(([^)]+)\)"))  # inside parentheses
    height_cm = _regex_first(profile_text, r"(\d+)cm")
    weight_kg = _regex_first(profile_text, r"(\d+)kg")
    positions = ",".join([_text(s) for s in (profile.select("p span") if profile else [])])

    grids = article.select(".grid") if article else []
    overall_rating, potential, value, wage = _parse_overall(grids)

    content_player_info = grids[1].select(".col") if len(grids) > 1 else []

    profile_attrs = _parse_profile_block(content_player_info)  # 8
    specialities = _parse_specialities_block(content_player_info)  # 1
    club = _parse_club_block(content_player_info)  # 10
    country = _parse_country_block(content_player_info)  # 8
    attributes = _parse_attributes(grids)  # 36

    row = [
        player_id, version, name, full_name, description, image,
        height_cm, weight_kg, dob, positions,
        overall_rating, potential, value, wage,
        *profile_attrs,
        *specialities,
        *club,
        *country,
        *attributes
    ]

    # sanity
    assert len(row) == len(ROW_HEADER), f"Row length {len(row)} != header {len(ROW_HEADER)}"
    # only needed if you manually build CSV lines yourself:
    return [c.replace('"', '""') if isinstance(c, str) else c for c in row]


# ---------------- helpers ----------------

def _text(node):
    return node.get_text(strip=True) if node else ""


def _attr(node, key):
    return node.get(key, "") if node and node.has_attr(key) else ""


def _regex_first(text, pattern):
    if not text:
        return ""
    m = re.search(pattern, text)
    return m.group(1) if m else ""


def _find_block_index(cols, title_substring):
    for i, col in enumerate(cols):
        h = col.select_one("h5")
        if h and title_substring in _text(h):
            return i
    return -1


def _extract_lines(col):
    return [_text(p) for p in col.select("p")]


def _extract_html_strings(col):
    return [str(p) for p in col.select("p")]


def _find_value(lines, label):
    # mimic JS: find first line containing substring, then remove the label
    for s in lines:
        if label in s:
            return s.replace(label, "").strip()
    return ""


def _strip_all_ws(s):
    return re.sub(r"\s+", "", s) if s else ""


def _parse_overall(grids):
    if not grids:
        return "", "", "", ""
    ems = grids[0].select(".col em")
    vals = [_text(e) for e in ems]
    return (vals + ["", "", "", ""])[:4]


def _parse_profile_block(cols):
    idx = _find_block_index(cols, "Profile")
    if idx < 0:
        return [""] * 8
    lines = _extract_lines(cols[idx])

    preferred_foot = _find_value(lines, "Preferred foot")
    weak_foot = _find_value(lines, "Weak foot")
    skill_moves = _find_value(lines, "Skill moves")
    international_rep = _find_value(lines, "International reputation")
    work_rate = _strip_all_ws(_find_value(lines, "Work rate"))
    body_type = _find_value(lines, "Body type")
    real_face = _find_value(lines, "Real face")
    release_clause = _find_value(lines, "Release clause")

    return [
        preferred_foot, weak_foot, skill_moves, international_rep,
        work_rate, body_type, real_face, release_clause
    ]


def _parse_specialities_block(cols):
    idx = _find_block_index(cols, "Player specialities")
    if idx < 0:
        return [""]
    lines = _extract_lines(cols[idx])
    return [",".join([s.replace("#", "").strip() for s in lines])]


def _parse_club_block(cols):
    idx = _find_block_index(cols, "Club")
    if idx < 0:
        return [""] * 10

    html_strs = _extract_html_strings(cols[idx])
    txt_lines = _extract_lines(cols[idx])

    def first_html_containing(substr):
        for h in html_strs:
            if substr in h:
                return h
        return ""

    # club info
    club_html = first_html_containing("/team/")
    club_s = BeautifulSoup(club_html, "html.parser")
    club_a = club_s.select_one("a[href*='/team/']")
    club_href = _attr(club_a, "href")
    club_id = club_href.split("/")[2] if club_href else ""
    club_name = _text(club_a)
    club_logo = _attr(club_a.select_one("img"), "data-src")

    league_html = first_html_containing("/league/")
    league_s = BeautifulSoup(league_html, "html.parser")
    league_a = league_s.select_one("a[href*='/league/']")
    league_href = _attr(league_a, "href")
    club_league_id = league_href.split("/")[2] if league_href else ""
    club_league_name = _text(league_a)

    rating_html = first_html_containing("<svg")
    rating_s = BeautifulSoup(rating_html, "html.parser")
    club_rating = _text(rating_s)

    club_position = _find_value(txt_lines, "Position")
    club_kit_number = _find_value(txt_lines, "Kit number")
    club_joined = format_date(_find_value(txt_lines, "Joined"))
    club_contract = _find_value(txt_lines, "Contract valid until")

    return [
        club_id, club_name, club_league_id, club_league_name, club_logo,
        club_rating, club_position, club_kit_number, club_joined, club_contract
    ]


def _parse_country_block(cols):
    idx = _find_block_index(cols, "National team")
    if idx < 0:
        return [""] * 8

    html_strs = _extract_html_strings(cols[idx])
    txt_lines = _extract_lines(cols[idx])

    def first_html_containing(substr):
        for h in html_strs:
            if substr in h:
                return h
        return ""

    country_html = first_html_containing("/team/")
    s = BeautifulSoup(country_html, "html.parser")
    a = s.select_one("a[href*='/team/']")
    href = _attr(a, "href")
    country_id = href.split("/")[2] if href else ""
    country_name = _text(a)
    country_flag = _attr(a.select_one("img"), "data-src")

    league_html = first_html_containing("/league/")
    s2 = BeautifulSoup(league_html, "html.parser")
    a2 = s2.select_one("a[href*='/league/']")
    href2 = _attr(a2, "href")
    country_league_id = href2.split("/")[2] if href2 else ""
    country_league_name = _text(a2)

    rating_html = first_html_containing("<svg")
    s3 = BeautifulSoup(rating_html, "html.parser")
    country_rating = _text(s3)

    country_position = _find_value(txt_lines, "Position")
    country_kit_number = _find_value(txt_lines, "Kit number")

    return [
        country_id, country_name, country_league_id, country_league_name, country_flag,
        country_rating, country_position, country_kit_number
    ]


def _parse_attributes(grids):
    if len(grids) < 4:
        return [""] * 36

    def clean_list(grid):
        ps = grid.select(".col p")
        out = []
        for p in ps:
            for s in p.select("span.plus, span.minus"):
                s.decompose()
            out.append(_text(p))
        return out

    cleaned_grids = {i: clean_list(grids[i]) for i in range(len(grids))}

    g2 = clean_list(grids[3])
    g3 = clean_list(grids[4])

    def val(lst, label):
        for s in lst:
            if label in s:
                return s.replace(label, "").strip()
        return ""

    # attacking
    crossing = val(g2, "Crossing")
    finishing = val(g2, "Finishing")
    heading_accuracy = val(g2, "Heading accuracy")
    short_passing = val(g2, "Short passing")
    volleys = val(g2, "Volleys")

    # skill
    dribbling = val(g2, "Dribbling")
    curve = val(g2, "Curve")
    fk_accuracy = val(g2, "FK Accuracy")
    long_passing = val(g2, "Long passing")
    ball_control = val(g2, "Ball control")

    # movement
    acceleration = val(g2, "Acceleration")
    sprint_speed = val(g2, "Sprint speed")
    agility = val(g2, "Agility")
    reactions = val(g2, "Reactions")
    balance = val(g2, "Balance")

    # power
    shot_power = val(g2, "Shot power")
    jumping = val(g2, "Jumping")
    stamina = val(g2, "Stamina")
    strength = val(g2, "Strength")
    long_shots = val(g2, "Long shots")

    # mentality
    aggression = val(g3, "Aggression")
    interceptions = val(g3, "Interceptions")
    positioning = val(g3, "Att. Position")
    vision = val(g3, "Vision")
    penalties = val(g3, "Penalties")
    composure = val(g3, "Composure")

    # defending
    defensive_awareness = val(g3, "Defensive awareness")
    standing_tackle = val(g3, "Standing tackle")
    sliding_tackle = val(g3, "Sliding tackle")

    # goalkeeping
    gk_diving = val(g3, "GK Diving")
    gk_handling = val(g3, "GK Handling")
    gk_kicking = val(g3, "GK Kicking")
    gk_positioning = val(g3, "GK Positioning")
    gk_reflexes = val(g3, "GK Reflexes")

    # play styles
    play_styles = ""
    cols_in_g3 = grids[3].select(".col")
    for col in cols_in_g3:
        h5 = col.select_one("h5")
        if h5 and "PlayStyles" in _text(h5):
            play_styles = ",".join([_text(p) for p in col.select("p")])
            break

    return [
        crossing, finishing, heading_accuracy, short_passing, volleys,
        dribbling, curve, fk_accuracy, long_passing, ball_control,
        acceleration, sprint_speed, agility, reactions, balance,
        shot_power, jumping, stamina, strength, long_shots,
        aggression, interceptions, positioning, vision, penalties, composure,
        defensive_awareness, standing_tackle, sliding_tackle,
        gk_diving, gk_handling, gk_kicking, gk_positioning, gk_reflexes,
        play_styles
    ]


def parse_basic_profile(url: str):
    html = get_page_content(url)
    soup = BeautifulSoup(html, "html.parser")

    player_id = url.split("/")[4]

    # meta description
    description_tag = soup.select_one('meta[name=description]')
    description = description_tag["content"] if description_tag else ""

    # version from dropdown
    version_tag = soup.select_one('select[name=roster] option[selected]')
    version = format_date(version_tag.text.strip()) if version_tag else ""

    # main profile section
    article = soup.select_one("main article")
    profile = article.select_one(".profile") if article else None

    name = soup.title.text.split(" FC ")[0].strip() if soup.title else ""
    full_name = profile.select_one("h1").text.strip() if profile else ""
    image = profile.select_one("img")["data-src"] if profile and profile.select_one("img") else ""

    profile_text = profile.select_one("p").text if profile and profile.select_one("p") else ""

    # Extract DOB
    dob_match = profile_text.split("(")[-1].split(")")[0] if "(" in profile_text else ""
    dob = format_date(dob_match)

    # Height
    height_cm = ""
    if "cm" in profile_text:
        height_cm = profile_text.split("cm")[0].split()[-1]

    # Weight
    weight_kg = ""
    if "kg" in profile_text:
        weight_kg = profile_text.split("kg")[0].split()[-1]

    # Positions
    spans = profile.select("p span") if profile else []
    positions = ",".join([s.text for s in spans])

    return [
        player_id,
        version,
        name,
        full_name,
        description,
        image,
        height_cm,
        weight_kg,
        dob,
        positions
    ]
