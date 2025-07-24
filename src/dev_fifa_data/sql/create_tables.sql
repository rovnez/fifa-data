create table time
(
    time_id          INTEGER not null
        constraint pk_time primary key autoincrement,
    fifa_version     INTEGER not null,
    fifa_update      INTEGER not null,
    fifa_update_date TEXT    not null,
    constraint ak_time unique (fifa_version, fifa_update)
);

create table position
(
    position_id    INTEGER not null
        constraint pk_position primary key autoincrement,
    position_code  TEXT    not null,
    position_name  TEXT,
    position_group TEXT,
    position_order INTEGER
);


create table club
(
    club_id   INTEGER not null
        constraint pk_club primary key,
    club_name TEXT    not null
);

create table nation
(
    nation_id   INTEGER not null
        constraint pk_nation primary key,
    nation_name TEXT    not null
);

create table player
(
    player_id        INTEGER not null
        constraint pk_player primary key,
    player_name      TEXT    not null,
    player_long_name TEXT    not null,
    dob              TEXT    not null,
    nation_id        INTEGER not null
        constraint fk_player_nation references nation,
    preferred_foot   TEXT    not null
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


create table player_club
(
    player_club_id INTEGER not null
        constraint pk_player_club primary key autoincrement,
    player_id      INTEGER not null
        constraint fk_player_club_player references player,
    time_id        INTEGER not null
        constraint fk_player_club_time references time,
    club_id        INTEGER not null
        constraint fk_player_club_club references club,
    constraint ak_player_club unique (player_id, time_id)
);



create index ix_player_club_club_id on player_club (club_id);
create index ix_player_club_club_id_player_id_time_id on player_club (club_id, player_id, time_id);


create table club_league
(
    club_league_id INTEGER not null
        constraint pk_club_league primary key autoincrement,
    club_id        INTEGER not null
        constraint fk_club_league_club references club,
    time_id        INTEGER not null
        constraint fk_club_league_time references time,
    league_id      INTEGER not null
        constraint fk_club_league_league references league,
    constraint ak_club_league unique (club_id, time_id)
);



create table player_position
(
    player_position_id INTEGER not null
        constraint pk_player_position primary key autoincrement,
    player_id          INTEGER not null
        constraint fk_player_position_player_id references player,
    time_id            INTEGER not null
        constraint fk_player_position_time_id references time,
    position_id        INTEGER not null
        constraint fk_player_position_position_id references position,
    player_position_order     INTEGER not null
);

create table player_stats
(
    player_stats_id             INTEGER not null
        constraint pk_player_stats primary key autoincrement,
    player_id                   INTEGER
        constraint fk_player_stats_player_id references player,
    time_id                     INTEGER
        constraint fk_player_stats_time_id references time,
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
    goalkeeping_speed           INTEGER,
    constraint ak_player_stats unique (player_id, time_id)
);

