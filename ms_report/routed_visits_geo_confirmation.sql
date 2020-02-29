--SELECT calculate_distance(32.9697, -96.80322, 29.46786, -98.53506, 'K');

CREATE OR REPLACE FUNCTION calculate_distance(lat1 float, lon1 float, lat2 float, lon2 float, units varchar)
RETURNS float AS $dist$
    DECLARE
        dist float = 0;
        radlat1 float;
        radlat2 float;
        theta float;
        radtheta float;
    BEGIN
        IF lat1 = lat2 OR lon1 = lon2
            THEN RETURN dist;
        ELSE
            radlat1 = pi() * lat1 / 180;
            radlat2 = pi() * lat2 / 180;
            theta = lon1 - lon2;
            radtheta = pi() * theta / 180;
            dist = sin(radlat1) * sin(radlat2) + cos(radlat1) * cos(radlat2) * cos(radtheta);

            IF dist > 1 THEN dist = 1; END IF;

            dist = acos(dist);
            dist = dist * 180 / pi();
            dist = dist * 60 * 1.1515;

            IF units = 'K' THEN dist = dist * 1.609344; END IF;
            IF units = 'N' THEN dist = dist * 0.8684; END IF;

            RETURN dist;
        END IF;
    END;
$dist$ LANGUAGE plpgsql;

--select * from routed_visits_report limit 10
--drop view routed_visits_report

CREATE OR REPLACE VIEW routed_visits_report
 AS
	select A.date,A.name customer_name,A.customer_code,A.branch,A.tablet,
	month_name,year_name,A.sales_man,A.sale_plan_day,
	A.sale_plan_trip,sales_team,COALESCE(round(diff_km::int,2),0) diff_km,
	case when COALESCE(round(diff_km::int,2),0) > 1 then 'true'::character varying
	else 'false'::character varying end as highlight
	from 
	(
		select cv.date::date date,rp.name,rp.customer_code,rb.name branch,ti.name tablet,	
		to_char(to_timestamp (date_part('month',cv.date)::text, 'MM'), 'TMMonth') month_name,
		date_part('year',cv.date) year_name,
		(select name from res_partner where id in (select partner_id from res_users where id=cv.user_id)) sales_man,
		spd.name sale_plan_day,spt.name sale_plan_trip,ccs.name sales_team,
		(SELECT calculate_distance(latitude, longitude, partner_latitude, partner_longitude, 'K')) as diff_km
		from customer_visit cv
		left join res_partner rp on (cv.customer_id=rp.id)
		left join res_branch rb on (cv.branch_id=rb.id)
		left join tablets_information ti on (cv.tablet_id=ti.id)
		left join sale_plan_day spd on (cv.sale_plan_day_id=spd.id)
		left join sale_plan_trip spt on (cv.sale_plan_trip_id=spt.id)
		left join crm_case_section ccs on (cv.sale_team_id=ccs.id)
		where m_status!='reject'	
	)A