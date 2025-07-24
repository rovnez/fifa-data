--
-- select f.fifa_version, f.fifa_update, f.fifa_update_date, count(*) as cnt
-- from main.fifa f
-- group by f.fifa_version, f.fifa_update, f.fifa_update_date;
--
-- delete from main.fifa
-- where (fifa.fifa_version, fifa.fifa_update) not in ((23, 5), (22, 11), (21, 8), (20, 8), (19, 15), (18, 14), (17, 7), (16, 9), (15, 9));
--
-- select count(*)
-- from main.fifa f
-- where (f.fifa_version, f.fifa_update) in ((23, 5), (22, 11), (21, 8), (20, 8), (19, 15), (18, 14), (17, 7), (16, 9), (15, 9));


/* =====================================================================================================================
            Populate nationality
========================================================================================================================
*/


insert into main.nation (nation_id, nation_name)
select distinct f.nationality_id, f.nationality_name
from main.fifa f;

/* =====================================================================================================================
            Populate player
========================================================================================================================
*/

-- 159909: What is going on here? (TODO: remove certain competitions?)
-- 181458: Ivan Perišić preferred_foot left -> right
-- 221659: common example

-- should be zero
select f.player_id, f.fifa_version, f.fifa_update, count(*)
from main.fifa f
group by f.player_id, f.fifa_version, f.fifa_update
having count(*) > 1;
;
with bet as ( select f.player_id,
                     f.short_name,
                     f.long_name,
                     f.dob,
                     f.nationality_id,
                     f.preferred_foot,
                     rank() over (partition by f.player_id order by f.fifa_version desc, f.fifa_update desc) as rn
              from main.fifa f )
insert
into main.player (player_id, player_name, player_long_name, dob, nation_id, preferred_foot)
select bet.player_id, bet.short_name, bet.long_name, bet.dob, bet.nationality_id, bet.preferred_foot
from bet
where bet.rn = 1;
--use the most recent information


/* =====================================================================================================================
            Populate club
========================================================================================================================
*/

-- Players that where present in the database, but where at a club that was not in the game at that time ?
-- select distinct f.club_name, f.club_team_id, f.league_name, f.short_name, f.long_name, f.overall
-- from main.fifa f
-- where f.club_team_id not glob '[0-9]*'


/*
general idea:
bet: one club (club_id), has multiple names (club_name)
bet2: create logic to select the desired name
insert: select desired name
*/
;
with bet as ( select f.club_team_id, f.club_name, max(f.fifa_version) as fifa_version_max, max(f.fifa_update) as fifa_update_max
              from main.fifa f
              where f.club_team_id glob '[0-9]*' --remove invalid club_ids
              group by f.club_team_id, f.club_name ),
     bet2 as ( select bet.club_team_id,
                      bet.club_name,
                      bet.fifa_version_max,
                      bet.fifa_update_max,
                      rank() over (partition by bet.club_team_id order by bet.fifa_version_max desc, bet.fifa_update_max desc) as rn --club id: 112395 (hence club_name also)
               from bet )
insert
into main.club (club_id, club_name)
select bet2.club_team_id, bet2.club_name
from bet2
where bet2.rn = 1;
--use the most recent name

/* =====================================================================================================================
            Populate time
========================================================================================================================
*/

insert into main.time (fifa_version, fifa_update, fifa_update_date)
select distinct f.fifa_version, f.fifa_update, f.fifa_update_date
from main.fifa f
order by f.fifa_update_date, f.fifa_version, f.fifa_update;

/* =====================================================================================================================
            Populate player_stats
========================================================================================================================
*/

insert into main.player_stats(player_id, time_id, overall, potential, value_eur, wage_eur, age, height_cm, weight_kg,
                              weak_foot, skill_moves, international_reputation, release_clause_eur, pace, shooting,
                              passing, dribbling, defending, physic, attacking_crossing, attacking_finishing,
                              attacking_heading_accuracy, attacking_short_passing, attacking_volleys, skill_dribbling,
                              skill_curve, skill_fk_accuracy, skill_long_passing, skill_ball_control,
                              movement_acceleration, movement_sprint_speed, movement_agility, movement_reactions,
                              movement_balance, power_shot_power, power_jumping, power_stamina, power_strength,
                              power_long_shots, mentality_aggression, mentality_interceptions, mentality_positioning,
                              mentality_vision, mentality_penalties, mentality_composure, defending_marking_awareness,
                              defending_standing_tackle, defending_sliding_tackle, goalkeeping_diving,
                              goalkeeping_handling, goalkeeping_kicking, goalkeeping_positioning, goalkeeping_reflexes,
                              goalkeeping_speed)
select f.player_id,
       t.time_id,
       iif(overall glob '[0-9]*', overall, null)                                         as overall,
       iif(potential glob '[0-9]*', potential, null)                                     as potential,
       iif(value_eur glob '[0-9]*', value_eur, null)                                     as value_eur,
       iif(wage_eur glob '[0-9]*', wage_eur, null)                                       as wage_eur,
       iif(age glob '[0-9]*', age, null)                                                 as age,
       iif(height_cm glob '[0-9]*', height_cm, null)                                     as height_cm,
       iif(weight_kg glob '[0-9]*', weight_kg, null)                                     as weight_kg,
       iif(weak_foot glob '[0-9]*', weak_foot, null)                                     as weak_foot,
       iif(skill_moves glob '[0-9]*', skill_moves, null)                                 as skill_moves,
       iif(international_reputation glob '[0-9]*', international_reputation, null)       as international_reputation,
       iif(release_clause_eur glob '[0-9]*', release_clause_eur, null)                   as release_clause_eur,
       iif(pace glob '[0-9]*', pace, null)                                               as pace,
       iif(shooting glob '[0-9]*', shooting, null)                                       as shooting,
       iif(passing glob '[0-9]*', passing, null)                                         as passing,
       iif(dribbling glob '[0-9]*', dribbling, null)                                     as dribbling,
       iif(defending glob '[0-9]*', defending, null)                                     as defending,
       iif(physic glob '[0-9]*', physic, null)                                           as physic,
       iif(attacking_crossing glob '[0-9]*', attacking_crossing, null)                   as attacking_crossing,
       iif(attacking_finishing glob '[0-9]*', attacking_finishing, null)                 as attacking_finishing,
       iif(attacking_heading_accuracy glob '[0-9]*', attacking_heading_accuracy, null)   as attacking_heading_accuracy,
       iif(attacking_short_passing glob '[0-9]*', attacking_short_passing, null)         as attacking_short_passing,
       iif(attacking_volleys glob '[0-9]*', attacking_volleys, null)                     as attacking_volleys,
       iif(skill_dribbling glob '[0-9]*', skill_dribbling, null)                         as skill_dribbling,
       iif(skill_curve glob '[0-9]*', skill_curve, null)                                 as skill_curve,
       iif(skill_fk_accuracy glob '[0-9]*', skill_fk_accuracy, null)                     as skill_fk_accuracy,
       iif(skill_long_passing glob '[0-9]*', skill_long_passing, null)                   as skill_long_passing,
       iif(skill_ball_control glob '[0-9]*', skill_ball_control, null)                   as skill_ball_control,
       iif(movement_acceleration glob '[0-9]*', movement_acceleration, null)             as movement_acceleration,
       iif(movement_sprint_speed glob '[0-9]*', movement_sprint_speed, null)             as movement_sprint_speed,
       iif(movement_agility glob '[0-9]*', movement_agility, null)                       as movement_agility,
       iif(movement_reactions glob '[0-9]*', movement_reactions, null)                   as movement_reactions,
       iif(movement_balance glob '[0-9]*', movement_balance, null)                       as movement_balance,
       iif(power_shot_power glob '[0-9]*', power_shot_power, null)                       as power_shot_power,
       iif(power_jumping glob '[0-9]*', power_jumping, null)                             as power_jumping,
       iif(power_stamina glob '[0-9]*', power_stamina, null)                             as power_stamina,
       iif(power_strength glob '[0-9]*', power_strength, null)                           as power_strength,
       iif(power_long_shots glob '[0-9]*', power_long_shots, null)                       as power_long_shots,
       iif(mentality_aggression glob '[0-9]*', mentality_aggression, null)               as mentality_aggression,
       iif(mentality_interceptions glob '[0-9]*', mentality_interceptions, null)         as mentality_interceptions,
       iif(mentality_positioning glob '[0-9]*', mentality_positioning, null)             as mentality_positioning,
       iif(mentality_vision glob '[0-9]*', mentality_vision, null)                       as mentality_vision,
       iif(mentality_penalties glob '[0-9]*', mentality_penalties, null)                 as mentality_penalties,
       iif(mentality_composure glob '[0-9]*', mentality_composure, null)                 as mentality_composure,
       iif(defending_marking_awareness glob '[0-9]*', defending_marking_awareness, null) as defending_marking_awareness,
       iif(defending_standing_tackle glob '[0-9]*', defending_standing_tackle, null)     as defending_standing_tackle,
       iif(defending_sliding_tackle glob '[0-9]*', defending_sliding_tackle, null)       as defending_sliding_tackle,
       iif(goalkeeping_diving glob '[0-9]*', goalkeeping_diving, null)                   as goalkeeping_diving,
       iif(goalkeeping_handling glob '[0-9]*', goalkeeping_handling, null)               as goalkeeping_handling,
       iif(goalkeeping_kicking glob '[0-9]*', goalkeeping_kicking, null)                 as goalkeeping_kicking,
       iif(goalkeeping_positioning glob '[0-9]*', goalkeeping_positioning, null)         as goalkeeping_positioning,
       iif(goalkeeping_reflexes glob '[0-9]*', goalkeeping_reflexes, null)               as goalkeeping_reflexes,
       iif(goalkeeping_speed glob '[0-9]*', goalkeeping_speed, null)                     as goalkeeping_speed
from main.fifa_players f
         inner join main.time t on f.fifa_update = t.fifa_update and f.fifa_version = t.fifa_version;


/* =====================================================================================================================
            populate position
========================================================================================================================
*/

insert into position (position_code, position_name, position_group, position_order)
values ('GK', 'goalkeeper', 'goalkeeper', 1);
insert into position (position_code, position_name, position_group, position_order)
values ('RWB', 'right_wing_back', 'defender', 2);
insert into position (position_code, position_name, position_group, position_order)
values ('RB', 'right_back', 'defender', 3);
insert into position (position_code, position_name, position_group, position_order)
values ('CB', 'centre_back', 'defender', 4);
insert into position (position_code, position_name, position_group, position_order)
values ('LB', 'left_back', 'defender', 5);
insert into position (position_code, position_name, position_group, position_order)
values ('LWB', 'left_wing_back', 'defender', 6);
insert into position (position_code, position_name, position_group, position_order)
values ('CDM', 'defensive_midfielder', 'midfielder', 7);
insert into position (position_code, position_name, position_group, position_order)
values ('RM', 'right_midfielder', 'midfielder', 8);
insert into position (position_code, position_name, position_group, position_order)
values ('CM', 'central_midfielder', 'midfielder', 9);
insert into position (position_code, position_name, position_group, position_order)
values ('LM', 'left_midfielder', 'midfielder', 10);
insert into position (position_code, position_name, position_group, position_order)
values ('CAM', 'attacking_midfielder', 'midfielder', 11);
insert into position (position_code, position_name, position_group, position_order)
values ('RW', 'right_winger', 'forward', 12);
insert into position (position_code, position_name, position_group, position_order)
values ('CF', 'centre_forward', 'forward', 13);
insert into position (position_code, position_name, position_group, position_order)
values ('ST', 'striker', 'forward', 14);
insert into position (position_code, position_name, position_group, position_order)
values ('LW', 'left_winger', 'forward', 15);


/* =====================================================================================================================
            populate player_position
========================================================================================================================
*/


;
with recursive SplitPositions as ( select player_id,
                                          fifa_version,
                                          fifa_update,
                                          trim(substr(position || ',', 1, instr(position || ',', ',') - 1)) as position,
                                          substr(position || ',', instr(position || ',', ',') + 1)          as remaining_positions,
                                          1                                                                 as position_order
                                   from ( select f.player_id, f.fifa_version, f.fifa_update, f.player_positions as position from main.fifa f )
                                   where position is not null

                                   union all

                                   select player_id,
                                          fifa_version,
                                          fifa_update,
                                          trim(substr(remaining_positions, 1, instr(remaining_positions, ',') - 1)) as position,
                                          substr(remaining_positions, instr(remaining_positions, ',') + 1)          as remaining_positions,
                                          position_order + 1
                                   from SplitPositions
                                   where remaining_positions like '%,%' )
insert
into main.player_position (player_id, time_id, position_id, player_position_order)
select SplitPositions.player_id, t.time_id, p.position_id, SplitPositions.position_order
from SplitPositions
         inner join main.position p on p.position_code = SplitPositions.position
         inner join main.time t on t.fifa_version = SplitPositions.fifa_version and t.fifa_update = SplitPositions.fifa_update;


/* =====================================================================================================================
            populate player_club
========================================================================================================================
*/

insert into main.player_club (player_id, time_id, club_id)
select f.player_id, t.time_id, f.club_team_id
from main.fifa f
         inner join main.time t on f.fifa_version = t.fifa_version and f.fifa_update = t.fifa_update
where f.club_team_id is not null --fix: some players have no club
;

/* =====================================================================================================================
            Populate league
========================================================================================================================
*/

;
with bet as ( select f.league_id, f.league_name, f.league_level, max(f.fifa_version) as fifa_version_max, max(f.fifa_update) as fifa_update_max
              from main.fifa f
              where f.league_id is not null
              group by f.league_id, f.league_name, f.league_level ),
     bet2 as ( select bet.league_id,
                      bet.league_name,
                      bet.league_level,
                      bet.fifa_version_max,
                      bet.fifa_update_max,
                      rank() over (partition by bet.league_id order by bet.fifa_version_max desc, bet.fifa_update_max desc) as rn
               from bet )
insert
into main.league (league_id, league_name, league_level)
select bet2.league_id, bet2.league_name, bet2.league_level
from bet2;
-- it is not needed to filter on most_recent since this data has remained static

/* =====================================================================================================================
            populate club_leage
========================================================================================================================
*/

insert into main.club_league (club_id, time_id, league_id)
select distinct f.club_team_id, t.time_id, f.league_id
from main.fifa f
         inner join main.time t on f.fifa_version = t.fifa_version and f.fifa_update = t.fifa_update
where f.club_team_id is not null
  and f.league_id is not null
;

-- select f.*
-- from main.fifa f
--          inner join main.time t on f.fifa_version = t.fifa_version and f.fifa_update = t.fifa_update
-- where not (f.club_team_id glob '[0-9]*' or f.league_id glob '[0-9]*')

/* =====================================================================================================================
            Examples
========================================================================================================================
*/

/*
-- empty table and reset index
DELETE FROM main.player_club;
DELETE FROM sqlite_sequence WHERE name = 'player_club';
*/

/*
create table player_position
(
    player_position_id INTEGER not null
        constraint PK_player_position primary key autoincrement,
    player_id          INTEGER
        constraint player_position_player_player_id_fk references player,
    time_id            INTEGER
        constraint player_position_time_time_id_fk references time,
    position_id        INTEGER
        constraint player_position_position_position_id_fk references position
);

*/

drop table if exists league_nation;
create temporary table league_nation
(
    league_id INTEGER,
    nation_id INTEGER
);


insert into league_nation (league_id, nation_id)
values (1, 13),     -- Denmark
       (4, 7),      -- Belgium
       (7, 54),     -- Brazil (but unlicensed/fake players)
       (10, 34),    -- Netherlands
       (13, 14),    -- England
       (14, 14),    -- England
       (16, 18),    -- France
       (17, 18),    -- France
       (19, 21),    -- Germany
       (20, 21),    -- Germany
       (31, 27),    -- Italy
       (32, 27),    -- Italy
       (39, 95),    -- United States
       (41, 36),    -- Norway
       (50, 42),    -- Scotland
       (53, 45),    -- Spain
       (54, 45),    -- Spain
       (56, 46),    -- Sweden
       (60, 14),    -- England
       (61, 14),    -- England
       (62, 14),    -- England --Due to Wrexham
       (63, 22),    -- Greece
       (64, 23),    -- Hungary
       (65, 25),    -- Republic of Ireland
       (66, 37),    -- Poland
       (67, 40),    -- Russia
       (68, 48),    -- Turkey
       (76, null),  -- Mixed clubs (rest of the world)
       (80, 4),     -- Austria
       (83, 167),   -- Korea Republic
       (189, 47),   -- Switzerland
       (308, 38),   -- Portugal
       (317, 10),   -- Croatia
       (318, 11),   -- Cyprus
       (319, 12),   -- Czech Republic
       (322, 17),   -- Finland
       (330, 39),   -- Romania
       (332, 49),   -- Ukraine
       (335, 55),   -- Chile
       (336, 56),   -- Colombia
       (337, 58),   -- Paraguay
       (338, 60),   -- Uruguay
       (341, 83),   -- Mexico
       (347, 140),  -- South Africa
       (349, 163),  -- Japan
       (350, 183),  -- Saudi Arabia
       (351, 195),  -- Australia
       (353, 52),   -- Argentina
       (2012, 155), -- China PR
       (2013, 190), -- United Arab Emirates
       (2017, 53),  -- Bolivia
       (2018, 57),  -- Ecuador
       (2019, 61),  -- Venezuela
       (2020, 59),  -- Peru
       (2076, 21),  -- Germany
       (2149, 159) -- India
;

update league
set nation_id = ( select ln.nation_id from league_nation ln where ln.league_id = league.league_id );



