/* =====================================================================================================================
########################################################################################################################



DESCRIPTION:
Check Fifa data
The csv contains 20007182 lines
Half of the lines are empty, so there should be (20007182/2)-1 = 10003590 lines



########################################################################################################################
========================================================================================================================
*/


select count(*)
from main.fifa f



/* =====================================================================================================================
            Some examples
========================================================================================================================
*/

select *
from main.player p
where p.player_name = 'M. Depay'

select *
from main.player_position pp
inner join main.position p on pp.position_id = p.position_id
where pp.player_id = 202556


-- in fifa 22 Wrexham (national league = 5th english league) was added as the only time from that league (due to rich owners)



-- Note: fifa_teams bevat meer teams dan fifa_players