create table fifa_players
(
    player_id                      INTEGER,
    player_url                     TEXT,
    fifa_version                   INTEGER,
    fifa_update                    INTEGER,
    fifa_update_date               TEXT,
    short_name                     TEXT,
    long_name                      TEXT,
    player_positions               TEXT,
    overall                        INTEGER,
    potential                      INTEGER,
    value_eur                      INTEGER,
    wage_eur                       INTEGER,
    age                            INTEGER,
    dob                            TEXT,
    height_cm                      INTEGER,
    weight_kg                      INTEGER,
    league_id                      INTEGER,
    league_name                    TEXT,
    league_level                   INTEGER,
    club_team_id                   INTEGER,
    club_name                      TEXT,
    club_position                  TEXT,
    club_jersey_number             INTEGER,
    club_loaned_from               TEXT,
    club_joined_date               TEXT,
    club_contract_valid_until_year INTEGER,--
    nationality_id                 INTEGER,
    nationality_name               TEXT,
    nation_team_id                 INTEGER,
    nation_position                TEXT,
    nation_jersey_number           INTEGER,
    preferred_foot                 TEXT,
    weak_foot                      INTEGER,
    skill_moves                    INTEGER,
    international_reputation       INTEGER,
    work_rate                      TEXT,
    body_type                      TEXT,
    real_face                      TEXT,
    release_clause_eur             INTEGER,
    player_tags                    TEXT,
    player_traits                  TEXT,
    pace                           INTEGER,
    shooting                       INTEGER,
    passing                        INTEGER,
    dribbling                      INTEGER,
    defending                      INTEGER,
    physic                         INTEGER,
    attacking_crossing             INTEGER,
    attacking_finishing            INTEGER,
    attacking_heading_accuracy     INTEGER,
    attacking_short_passing        INTEGER,
    attacking_volleys              INTEGER,
    skill_dribbling                INTEGER,
    skill_curve                    INTEGER,
    skill_fk_accuracy              INTEGER,
    skill_long_passing             INTEGER,
    skill_ball_control             INTEGER,
    movement_acceleration          INTEGER,
    movement_sprint_speed          INTEGER,
    movement_agility               INTEGER,
    movement_reactions             INTEGER,
    movement_balance               INTEGER,
    power_shot_power               INTEGER,
    power_jumping                  INTEGER,
    power_stamina                  INTEGER,
    power_strength                 INTEGER,
    power_long_shots               INTEGER,
    mentality_aggression           INTEGER,
    mentality_interceptions        INTEGER,
    mentality_positioning          INTEGER,
    mentality_vision               INTEGER,
    mentality_penalties            INTEGER,
    mentality_composure            INTEGER,
    defending_marking_awareness    INTEGER,
    defending_standing_tackle      INTEGER,
    defending_sliding_tackle       INTEGER,
    goalkeeping_diving             INTEGER,
    goalkeeping_handling           INTEGER,
    goalkeeping_kicking            INTEGER,
    goalkeeping_positioning        INTEGER,
    goalkeeping_reflexes           INTEGER,
    goalkeeping_speed              INTEGER,
    ls                             TEXT,
    st                             TEXT,
    rs                             TEXT,
    lw                             TEXT,
    lf                             TEXT,
    cf                             TEXT,
    rf                             TEXT,
    rw                             TEXT,
    lam                            TEXT,
    cam                            TEXT,
    ram                            TEXT,
    lm                             TEXT,
    lcm                            TEXT,
    cm                             TEXT,
    rcm                            TEXT,
    rm                             TEXT,
    lwb                            TEXT,
    ldm                            TEXT,
    cdm                            TEXT,
    rdm                            TEXT,
    rwb                            TEXT,
    lb                             TEXT,
    lcb                            TEXT,
    cb                             TEXT,
    rcb                            TEXT,
    rb                             TEXT,
    gk                             TEXT,
    player_face_url                TEXT
);


create table club
(
    club_id   INTEGER not null
        constraint pk_club primary key,
    club_name TEXT    not null,
    league_id INTEGER not null
        constraint fk_club_league references league
);


create table nation
(
    nation_id   INTEGER not null
        constraint pk_nation primary key,
    nation_name TEXT    not null
);

create table league
(
    league_id    INTEGER not null
        constraint pk_league primary key,
    league_name  TEXT    not null,
    league_level INTEGER,
    nation_id    INTEGER
        constraint fk_league_nation references nation
);

create table player
(
    player_id                   INTEGER not null
        constraint pk_player primary key,
    player_name                 TEXT    not null,
    player_long_name            TEXT    not null,
    dob                         TEXT    not null,
    nation_id                   INTEGER not null
        constraint fk_player_nation references nation,
    preferred_foot              TEXT    not null,
    club_id                     INTEGER
        constraint fk_player_club references club,


    overall                     INTEGER,
    potential                   INTEGER,
    value_eur                   INTEGER,
    wage_eur                    INTEGER,
    age                         INTEGER,
    height_cm                   INTEGER,
    weight_kg                   INTEGER,
    weak_foot                   INTEGER,
    skill_moves                 INTEGER,
    international_reputation    INTEGER,
    release_clause_eur          INTEGER,
    pace                        INTEGER,
    shooting                    INTEGER,
    passing                     INTEGER,
    dribbling                   INTEGER,
    defending                   INTEGER,
    physic                      INTEGER,
    attacking_crossing          INTEGER,
    attacking_finishing         INTEGER,
    attacking_heading_accuracy  INTEGER,
    attacking_short_passing     INTEGER,
    attacking_volleys           INTEGER,
    skill_dribbling             INTEGER,
    skill_curve                 INTEGER,
    skill_fk_accuracy           INTEGER,
    skill_long_passing          INTEGER,
    skill_ball_control          INTEGER,
    movement_acceleration       INTEGER,
    movement_sprint_speed       INTEGER,
    movement_agility            INTEGER,
    movement_reactions          INTEGER,
    movement_balance            INTEGER,
    power_shot_power            INTEGER,
    power_jumping               INTEGER,
    power_stamina               INTEGER,
    power_strength              INTEGER,
    power_long_shots            INTEGER,
    mentality_aggression        INTEGER,
    mentality_interceptions     INTEGER,
    mentality_positioning       INTEGER,
    mentality_vision            INTEGER,
    mentality_penalties         INTEGER,
    mentality_composure         INTEGER,
    defending_marking_awareness INTEGER,
    defending_standing_tackle   INTEGER,
    defending_sliding_tackle    INTEGER,
    goalkeeping_diving          INTEGER,
    goalkeeping_handling        INTEGER,
    goalkeeping_kicking         INTEGER,
    goalkeeping_positioning     INTEGER,
    goalkeeping_reflexes        INTEGER,
    goalkeeping_speed           INTEGER
);

create table position
(
    position_id    INTEGER not null
        constraint pk_position primary key autoincrement,
    position       TEXT    not null,
    field_role     TEXT,
    role           TEXT,
    position_order INTEGER
);



create table player_position
(
    player_position_id    INTEGER not null
        constraint pk_player_position primary key autoincrement,
    player_id             INTEGER not null
        constraint fk_player_position_player_id references player,
    position_id           INTEGER not null
        constraint fk_player_position_position_id references position,
    player_position_order INTEGER not null
);

create table player_position_link
(
    player_id   INTEGER not null
        constraint fk_player_position_player_id references player,
    position_id INTEGER not null
        constraint fk_player_position_position_id references position,
    constraint pk_player_position primary key (position_id, player_id)
);


/* =====================================================================================================================
            SQUAD
========================================================================================================================
*/

create table squad
(
    squad_id   INTEGER not null
        constraint pk_squad primary key autoincrement,
    squad_name TEXT
);

create table squad_player_position
(
    squad_player_position_id INTEGER not null
        constraint pk_squad_player_position primary key autoincrement,
    squad_id                 INTEGER not null
        constraint fk_squad_player_position_squad references squad,
    player_id                INTEGER not null
        constraint fk_squad_player_position_player references player,
    position_id              INTEGER not null
        constraint fk_squad_player_position_position references position,
    constraint ak_squad_player_position unique (squad_id, player_id)
);

