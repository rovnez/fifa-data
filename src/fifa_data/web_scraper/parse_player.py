import re
from multiprocessing.forkserver import set_forkserver_preload

import bs4
from datetime import datetime, date

from fifa_data.web_scraper.utils import parse_player_url, convert_date_to_iso

CUR_RX = re.compile(r"€\s*([\d.]+)\s*([MK]?)", re.I)


def _eur_to_int(txt: str | None) -> int | None:
    if not txt:
        return None
    m = CUR_RX.search(txt)
    if not m:
        return None
    num_str, suffix = m.groups()
    try:
        num = float(num_str)
    except ValueError:
        return None
    multiplier = {"M": 1_000_000, "K": 1_000}.get(suffix.upper(), 1)
    return int(num * multiplier)


def _int_from_href(href, pattern):
    m = re.search(pattern, href)
    return int(m.group(1)) if m else None


def _safe_int(m):
    return int(m.group(1)) if m else None


class PlayerParser:
    AGGREGATE_STATS = {
        'PAC': 'pace',
        'SHO': 'shooting',
        'PAS': 'passing',
        'DRI': 'dribbling',
        'DEF': 'defending',
        'PHY': 'physic',
        'SPD': 'goalkeeping_spped'  # This stats is relevant for goalkeepers
    }

    HEADERS_STATS = {
        "Attacking", "Skill", "Movement", "Power",
        "Mentality", "Defending", "Goalkeeping",
    }

    HEADERS_SPECIAL_STATS = {
        "Traits", "PlayStyles",
    }

    HEADERS_INFO = {
        'Club', 'National team', 'Player specialities', 'Profile'
    }

    def __init__(self, player_url: str, html: str):
        # TODO: convert euto to int (6M -> 6 000 000)
        self.bs: bs4.BeautifulSoup = bs4.BeautifulSoup(html)

        player_info = parse_player_url(player_url)

        # info that should be filled when initializing the parser
        self.player_id: int = player_info['player_id']
        self.player_url: str = player_url[:-1] if player_url[-1] == '/' else player_url  # for consistency with older data
        self.fifa_version: int = player_info['fifa_version']
        self.fifa_update: int = player_info['fifa_update']
        self.fifa_update_date: str | None = None

        self.player_face_url: str | None = None

        self.short_name: str | None = None
        self.long_name: str | None = None
        self.positions: list | None = None

        # age, dob, height_cm, weight_kg
        self.main_info = dict.fromkeys(['age', 'dob', 'height_cm', 'weight_kg', 'nationality_id', 'nationality_name'], None)
        self.main_stats = dict.fromkeys(['overall', 'potential', 'value_eur', 'wage_eur'], None)

        self.stat_grids = []
        self.info_grids = []

        self.position_ratings = {}
        self.player_specialities = set()

        # dict for storing all the cols of the grids (both stats and info)
        self._cols = {}

        self.profile_data = dict.fromkeys(
            ['preferred_foot', 'weak_foot', 'skill_moves', 'international_reputation', 'work_rate', 'body_type', 'real_face', 'release_clause_eur'], None)
        self.club_data = dict.fromkeys(
            ["league_id", "league_name", "league_level", "club_team_id", "club_name", "club_position", "club_jersey_number", "club_loaned_from",
             "club_joined_date", "club_contract_valid_until_year"], None)
        # TODO: figure out league level

        self.position_ratings = dict.fromkeys(
            ['LS', 'ST', 'RS', 'LW', 'LF', 'RF', 'RW', 'LAM', 'CAM', 'RAM', 'LM', 'LCM', 'CM', 'RCM', 'RM', 'LDM', 'CDM', 'RDM', 'LB', 'LCB', 'CB', 'RCB', 'RB',
             'GK'], None
        )

        # 'nationality_id' and 'nationality_name' are part of main_info
        self.national_team_data = dict.fromkeys(["nation_team_id", "nation_position", "nation_jersey_number"], None)

        self.stats = {}
        self.special_stats = {}
        self.aggregated_stats = {}

    def parse(self):
        self.short_name = self.bs.header.h1.get_text()
        self.long_name = self.bs.main.h1.get_text(strip=True)
        self.positions = [x.get_text() for x in self.bs.article.div.select('.pos')]

        fifa_update_date = self.bs.header.find(id='select-roster').get_text(strip=True)
        self.fifa_update_date = convert_date_to_iso(fifa_update_date)

        self.parse_main_info()
        self.parse_main_stats()
        # first we split the main grid into 4 parts (1: info_grid, 2: exists only on FC 25 -> ignore, 3: stat_grid 1, 4: stat_grid 2)
        self._split_grids()

        self.position_ratings.update(self.parse_position_ratings())

        # dict_keys(['Profile', 'Player specialities', 'Club', 'National team', 'Attacking', 'Skill', 'Movement', 'Power', 'Mentality', 'Defending', 'Goalkeeping', 'PlayStyles'])

        # parse info grid
        profile = self._cols.get('Profile')
        if profile:
            self._parse_profile(profile)

        player_specialities = self._cols.get('Player specialities')
        self.player_specialities = set(x.get_text() for x in player_specialities.find_all('p'))

        club = self._cols.get('Club')
        if club:
            self._parse_club(club)
        national_team = self._cols.get('National team')
        if national_team:
            self._parse_national_team(national_team)

        self.parse_stat_grid()
        self.parse_aggregate_stats()

    def export_player_data(self) -> dict:
        mega_dict = {
            'player_id': self.player_id,
            'player_url': self.player_url,
            'fifa_version': self.fifa_version,
            'fifa_update': self.fifa_update,
            'fifa_update_date': self.fifa_update_date,
            'short_name': self.short_name,
            'long_name': self.long_name,
            'positions': self.positions,
            'player_face_url': self.player_face_url,
            'player_tags': list(self.player_specialities),

        }

        mega_dict.update(self.main_stats)
        mega_dict.update(self.main_info)
        mega_dict.update(self.club_data)
        mega_dict.update(self.national_team_data)
        mega_dict.update(self.profile_data)
        mega_dict.update(self.aggregated_stats)

        for key, value in self.stats.items():
            if key in self.HEADERS_STATS:
                mega_dict.update({key.lower() + '_' + x['name'].lower().replace(' ', '_'): x['value'] for x in value})
            elif key in self.HEADERS_SPECIAL_STATS:
                mega_dict['player_traits'] = ", ".join(value)

        # rename some stats for consistency
        mega_dict["defending_marking_awareness"] = mega_dict.pop("defending_defensive_awareness")
        mega_dict["mentality_positioning"] = mega_dict.pop("mentality_att._position")

        mega_dict.update({k.lower(): v for k, v in self.position_ratings.items()})

        return mega_dict

    def parse_main_info(self):
        ## GET MAIN_INFO
        # get main_info (age,dob,height_cm,weight_kg)
        AGE_RX = re.compile(r"(\d+)\s*y\.o\.", re.I)
        DOB_RX = re.compile(r"\(([^)]+)\)")  # date in parentheses
        HT_RX = re.compile(r"(\d+)\s*cm", re.I)
        WT_RX = re.compile(r"(\d+)\s*kg", re.I)

        # Get the block containing age etc.
        info_block = self.bs.article.p

        self.player_face_url = self.bs.article.find('img').get('data-src')

        info_txt = info_block.contents[-1]
        self.main_info['age'] = _safe_int(AGE_RX.search(info_txt))
        dob_raw = DOB_RX.search(info_txt).group(1)
        self.main_info['dob'] = convert_date_to_iso(dob_raw)
        self.main_info['height_cm'] = _safe_int(HT_RX.search(info_txt))
        self.main_info['weight_kg'] = _safe_int(WT_RX.search(info_txt))

        self.main_info['nationality_name'] = info_block.find('a').get('title')
        link = info_block.find('a').get('href')
        # parse `'/players?na=27'`
        nationality_id = link.split('=')[1]
        self.main_info['nationality_id'] = nationality_id

    def parse_main_stats(self):
        # get overall rating, potential, value, wage (second div, create key value pairs)
        main_stats_block = self.bs.article.find_all('div')[1]
        some_stats = {sub.get_text(): col.get_text() for sub, col in zip(main_stats_block.select('div.sub'), main_stats_block.find_all('em'))}
        self.main_stats['overall'] = some_stats['Overall rating']
        self.main_stats['potential'] = some_stats['Potential']
        self.main_stats['value_eur'] = _eur_to_int(some_stats['Value'])
        self.main_stats['wage_eur'] = _eur_to_int(some_stats['Wage'])

    def _split_grids(self):

        # classify each grid
        self._cols = {h.get_text(): x for x in self.bs.article.find_all('div', class_='col') if (h := x.find('h5'))}

        for grid in self.bs.find('article').select('div.grid.attribute'):
            headers = {h.get_text() for h in grid.find_all('h5')}

            if headers & self.HEADERS_INFO:
                self.info_grids.append(grid)
            elif headers & self.HEADERS_STATS:
                self.stat_grids.append(grid)
            else:
                continue
                # e.g., 'Roles' (FC 25)
                # print(f"Unknown headings: {headers}")

    def parse_position_ratings(self) -> dict:
        # assert length is 27
        positions = {}
        for box in self.bs.find('aside').css.select('div.pos'):
            position = box.find(string=True, recursive=False)
            rating = box.find('em').text
            positions[position] = rating
        return positions

    def parse_aggregate_stats(self):
        # grab the <script> with POINT_*
        script_tag = self.bs.find('script', string=lambda s: 'POINT_' in s)
        if not script_tag:
            return

        # extract all assignments
        # e.g. POINT_DEF=33  or OVERALL='Overall'
        assignments = dict(
            (k, v.strip().strip('"\''))
            for k, v in re.findall(r'([A-Z_]+)\s*=\s*([^,;]+)', script_tag.string)
        )

        # keep only POINT_* and cast to int
        res = {
            k.replace('POINT_', ''): int(v)
            for k, v in assignments.items()
            if k.startswith('POINT_')
        }
        self.aggregated_stats = {self.AGGREGATE_STATS[k]: v for k, v in res.items() if k in self.AGGREGATE_STATS.keys()}
        return

    def parse_stat_grid(self):
        for grid in self.stat_grids:
            self._parse_stat_grid(grid)

    def _parse_stat_grid(self, grid):
        out = {}
        for col in grid.find_all('div', recursive=False):
            header = col.h5.get_text()
            if header in self.HEADERS_STATS:
                stats = []
                for p in col.find_all("p", recursive=False):
                    spans = p.find_all("span")
                    value = int(spans[0].get_text())
                    label = spans[1].get_text()

                    stats.append({"name": label, "value": value})
                out[header] = stats
            elif header in self.HEADERS_SPECIAL_STATS:
                out[header] = set(x.get_text() for x in col.find_all('p'))
        self.stats.update(out)

    def _parse_profile(self, profile):

        for p in profile.find_all("p", recursive=False):
            key = p.find('label').get_text()

            if key.upper() in {'PREFERRED FOOT', 'BODY TYPE', 'REAL FACE'}:
                value = p.find('label').next_sibling.get_text(" ", strip=True)
                self.profile_data[key.lower().replace(' ', '_')] = value

            elif key.upper() in {"SKILL MOVES", "WEAK FOOT", "INTERNATIONAL REPUTATION"}:
                value = int(p.contents[0][0])
                self.profile_data[key.lower().replace(' ', '_')] = value

            # no longer present in FC 25
            elif key.upper() in {'WORK RATE'}:
                value = p.find('label').next_sibling.get_text(" ", strip=True)
                self.profile_data['work_rate'] = value.replace(' ', '')

            elif key.upper() in {'RELEASE CLAUSE'}:
                value = p.find('label').next_sibling.get_text(" ", strip=True)
                self.profile_data['release_clause_eur'] = _eur_to_int(value)
            else:
                print(f"Skipping unrecognized profile key: '{key}'")
                # raise ValueError(f"Unrecognized profile key: '{key}'")
        return

    def _parse_club(self, club):
        # Club & league rows (first two <p> with <a>)
        team_a = club.select_one("p > a[href*='/team/']")
        league_a = club.select_one("p > a[href*='/league/']")

        club_team_id = _int_from_href(team_a["href"], r"/team/(\d+)/")
        club_name = team_a.get_text(strip=True)

        league_id = _int_from_href(league_a["href"], r"/league/(\d+)")
        league_name = league_a.get_text(strip=True)

        self.club_data['league_id'] = league_id
        self.club_data['league_name'] = league_name
        self.club_data['club_team_id'] = club_team_id
        self.club_data['club_name'] = club_name

        # iterate over every p-label pair 8
        for p, label in [(p, label) for p in club.find_all("p") if (label := p.find('label'))]:
            key = label.get_text()
            value = p.contents[-1].get_text()
            if key == 'Position':
                self.club_data["club_position"] = value
            elif key == 'Kit number':
                value = int(value)
                self.club_data["club_jersey_number"] = value

            elif key == 'Contract valid until':
                value = int(value)
                self.club_data["club_contract_valid_until_year"] = value

            elif key == 'Joined':
                value = convert_date_to_iso(value[1:])
                self.club_data["club_joined_date"] = value
            else:
                print(key, value)

    def _parse_national_team(self, national_team):
        # first <p> with /team/ = national team row
        team_a = national_team.select_one("p > a[href*='/team/']")
        league_a = national_team.select_one("p > a[href*='/league/']")  # may be useful if you store nation_league_id/name

        nation_team_id = _int_from_href(team_a["href"], r"/team/(\d+)/")
        nation_name = team_a.get_text(strip=True)

        self.national_team_data["nation_team_id"] = nation_team_id

        # rows with labels
        for p, label in [(p, label) for p in national_team.find_all("p") if (label := p.find('label'))]:
            key = label.get_text()
            value = p.contents[-1].get_text()
            if key == 'Position':
                self.national_team_data['nation_position'] = value
            elif key == 'Kit number':
                self.national_team_data['nation_jersey_number'] = int(value)
            else:
                print(key, value)
