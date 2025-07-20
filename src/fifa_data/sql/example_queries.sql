select p.player_id, p.player_name, n.nation_name
from main.player p
         inner join main.player_club pc on p.player_id = pc.player_id
         inner join main.time t on pc.time_id = t.time_id
         inner join main.club c on pc.club_id = c.club_id
         inner join main.nation n on p.nation_id = n.nation_id
         inner join main.club_league cl on c.club_id = cl.club_id and t.time_id = cl.time_id
where t.fifa_version = 23
  and t.fifa_update = 6
  and c.club_name = 'PSV'
;
with bet as ( select l.league_id, l.league_name, n.nation_id, n.nation_name, count(*) as cnt
              from main.player p
                       inner join main.player_club pc on p.player_id = pc.player_id
                       inner join main.time t on pc.time_id = t.time_id
                       inner join main.club c on pc.club_id = c.club_id
                       inner join main.nation n on p.nation_id = n.nation_id
                       inner join main.club_league cl on c.club_id = cl.club_id and t.time_id = cl.time_id
                       inner join main.league l on cl.league_id = l.league_id
              where t.fifa_version = 23
                and t.fifa_update = 6
              group by l.league_id, l.league_name, n.nation_id, n.nation_name )
   , bet2 as ( select *, rank() over ( partition by bet.league_id, bet.league_name order by bet.cnt desc) as rn from bet )
select *
from bet2
where rn in (1, 2, 3)


--select count(*)
select p.player_id,
       p.player_name,
       c.club_name,
       l.league_name,
       pos.position_code,
       pos.position_group,
       ps.overall,
       ps.potential,
       ps.value_eur,
       ps.wage_eur,
       ps.age,
       ps.height_cm,
       ps.weight_kg,
       ps.weak_foot,
       ps.skill_moves,
       ps.international_reputation,
       ps.release_clause_eur,
       ps.pace,
       ps.shooting,
       ps.passing,
       ps.dribbling,
       ps.defending,
       ps.physic,
       ps.attacking_crossing,
       ps.attacking_finishing,
       ps.attacking_heading_accuracy,
       ps.attacking_short_passing,
       ps.attacking_volleys,
       ps.skill_dribbling,
       ps.skill_curve,
       ps.skill_fk_accuracy,
       ps.skill_long_passing,
       ps.skill_ball_control,
       ps.movement_acceleration,
       ps.movement_sprint_speed,
       ps.movement_agility,
       ps.movement_reactions,
       ps.movement_balance,
       ps.power_shot_power,
       ps.power_jumping,
       ps.power_stamina,
       ps.power_strength,
       ps.power_long_shots,
       ps.mentality_aggression,
       ps.mentality_interceptions,
       ps.mentality_positioning,
       ps.mentality_vision,
       ps.mentality_penalties,
       ps.mentality_composure,
       ps.defending_marking_awareness,
       ps.defending_standing_tackle,
       ps.defending_sliding_tackle
from main.player p
         inner join main.player_club pc on p.player_id = pc.player_id
         inner join main.club c on pc.club_id = c.club_id
         inner join main.time t on pc.time_id = t.time_id
         inner join main.club_league cl on c.club_id = cl.club_id and t.time_id = cl.time_id
         inner join main.league l on cl.league_id = l.league_id
         inner join main.nation n on p.nation_id = n.nation_id
         inner join main.player_position pp on p.player_id = pp.player_id and t.time_id = pp.time_id and pp.player_position_order = 1
         inner join main.position pos on pp.position_id = pos.position_id
         inner join main.player_stats ps on p.player_id = ps.player_id and t.time_id = ps.time_id
where t.fifa_version = 23
  and t.fifa_update = 6
  and l.league_id in (10, 13, 16, 19, 31, 53) -- top 5 leagues + eredivisie
  and pos.position_code <> 'GK'