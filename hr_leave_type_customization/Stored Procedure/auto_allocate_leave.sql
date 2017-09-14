-- Function: auto_allocate_leave(integer)

-- DROP FUNCTION auto_allocate_leave(integer);

CREATE OR REPLACE FUNCTION auto_allocate_leave(_leavetype integer)
  RETURNS void AS
$BODY$
DECLARE work_days integer;
DECLARE number_of_days integer;
DECLARE td_date date;
DECLARE eff_date date;
DECLARE exp_date date;
DECLARE fy integer;
DECLARE _number_of_days integer;
DECLARE leaveRecord hr_leave_type%rowtype;
DECLARE r hr_employee%rowtype;
DECLARE exdate date;
DECLARE effdate date;
DECLARE exdate_one date;

BEGIN
	fy=(SELECT id FROM account_fiscalyear WHERE date_stop >= now()::date AND date_start <= now()::date);
	FOR leaveRecord IN SELECT * FROM hr_leave_type WHERE holiday_status_id=_leavetype
	LOOP 
	    FOR r IN SELECT hr_employee.*  from hr_employee where status not in ('inactive') and id in (select emp_id from employee_category_rel 
			WHERE category_id in (SELECT category_id from leave_employee_category_rel WHERE leavetype_id =leaveRecord.id)) 
			AND id not in (SELECT employee_id from hr_holidays WHERE effective_date::date + 1 * cast('1 year' as interval) >= now()::date AND holiday_status_id=leaveRecord.holiday_status_id)
	    LOOP
			SELECT COALESCE(max(effective_date) + 1 * CAST('1 year' as interval),r.initial_employment_date)::date as myeff_date INTO effdate
			FROM hr_holidays WHERE employee_id=r.id AND holiday_status_id=leaveRecord.holiday_status_id and type='add';
			
			SELECT COALESCE(max(expiry_date),r.initial_employment_date) as myexp_date INTO exdate FROM hr_holidays 
			WHERE employee_id=r.id AND holiday_status_id=leaveRecord.holiday_status_id AND type='add';

			SELECT COALESCE(max(expiry_date),r.initial_employment_date) INTO exdate_one FROM hr_holidays 
			WHERE employee_id=r.id AND holiday_status_id=leaveRecord.holiday_status_id AND type='add';
			-----------------------------------------------------------------------------------------------------------
			IF leaveRecord.based_on='joined_date' THEN
					IF leaveRecord.duration_before_allocation_type='day' THEN
						td_date=now()::date - leaveRecord.duration_before_allocation * cast('1 day' as interval);
						IF eff_date=r.initial_employment_date THEN
							eff_date=effdate + leaveRecord.duration_before_allocation * cast('1 day' as interval);
						ELSE
							eff_date=effdate;
						END IF;
						-----------------------------------
						IF leaveRecord.name='Earned_Leave' THEN   
							IF leaveRecord.validity > 1 THEN
								IF exdate_one <> r.initial_employment_date THEN
									IF exdate_one > now()::date THEN
										exp_date=r.initial_employment_date + leaveRecord.duration_before_allocation * cast('1 day' as interval) + leaveRecord.validity * cast('1 year' as interval);
									ELSE
										exp_date=eff_date + leaveRecord.validity * cast('1 year' as interval);
									END IF;
								ELSE
									exp_date=eff_date + leaveRecord.validity * cast('1 year' as interval);
								END IF;
							ELSE
								exp_date=eff_date + leaveRecord.validity * cast('1 year' as interval);
							END IF;
						ELSE
							exp_date=eff_date + leaveRecord.validity * cast('1 year' as interval);
						END IF;
						-----------------------------------
					END IF;
					IF leaveRecord.duration_before_allocation_type='month' THEN 
						td_date=now()::date - leaveRecord.duration_before_allocation * cast('1 month' as interval);
						IF eff_date=r.initial_employment_date THEN
							eff_date=effdate + leaveRecord.duration_before_allocation * cast('1 month' as interval);
						ELSE
							eff_date=effdate;
						END IF;
						----------------------------------
						IF leaveRecord.name='Earned_Leave' THEN   
							IF leaveRecord.validity > 1 THEN
								IF exdate_one <> r.initial_employment_date THEN
									IF exdate_one > now()::date THEN
										exp_date=r.initial_employment_date + leaveRecord.duration_before_allocation * cast('1 month' as interval) + leaveRecord.validity * cast('1 year' as interval);
									ELSE
										exp_date=eff_date + leaveRecord.validity * cast('1 year' as interval);
									END IF;
								ELSE
									exp_date=eff_date + leaveRecord.validity * cast('1 year' as interval);
								END IF;
							ELSE
								exp_date=eff_date + leaveRecord.validity * cast('1 year' as interval);
							END IF;
						ELSE
							exp_date=eff_date + leaveRecord.validity * cast('1 year' as interval);
						END IF;
						----------------------------------
					END IF;
					IF leaveRecord.duration_before_allocation_type='year' THEN 
							td_date=now()::date - leaveRecord.duration_before_allocation * cast('1 year' as interval);
						IF eff_date=r.initial_employment_date THEN
							eff_date=effdate + leaveRecord.duration_before_allocation * cast('1 year' as interval);
						ELSE
							eff_date=effdate;
						END IF;
						--------------------------
						IF leaveRecord.name='Earned_Leave' THEN   
							IF leaveRecord.validity > 1 THEN
								IF exdate_one <> r.initial_employment_date THEN
									IF exdate_one > now()::date THEN
										exp_date=r.initial_employment_date + leaveRecord.duration_before_allocation * cast('1 year' as interval) + leaveRecord.validity * cast('1 year' as interval);
									ELSE
										exp_date=eff_date + leaveRecord.validity * cast('1 year' as interval);
									END IF;
								ELSE
									exp_date=eff_date + leaveRecord.validity * cast('1 year' as interval);
								END IF;
							ELSE
								exp_date=eff_date + leaveRecord.validity * cast('1 year' as interval);
							END IF;
						ELSE
							exp_date=eff_date + leaveRecord.validity * cast('1 year' as interval);
						END IF;
						--------------------------
					END IF;
			END IF;
			IF leaveRecord.based_on='permanent' THEN
					IF leaveRecord.duration_before_allocation_type='day' THEN
						td_date=now()::date - leaveRecord.duration_before_allocation * cast('1 day' as interval);
						IF eff_date=r.initial_employment_date THEN
							eff_date=effdate + leaveRecord.duration_before_allocation * cast('1 day' as interval);
						ELSE
							eff_date=effdate;
						END IF;
						exp_date=eff_date + leaveRecord.validity * cast('1 year' as interval);
					END IF;
					IF leaveRecord.duration_before_allocation_type='month' THEN 
						td_date=now()::date -  leaveRecord.duration_before_allocation * cast('1 month' as interval);
						IF eff_date=r.initial_employment_date THEN
							eff_date=effdate + leaveRecord.duration_before_allocation * cast('1 month' as interval);
						ELSE
							eff_date=effdate;
						END IF;
						exp_date=eff_date + leaveRecord.validity * cast('1 year' as interval);
					END IF;
					IF leaveRecord.duration_before_allocation_type='year' THEN 
						td_date=now()::date -  leaveRecord.duration_before_allocation * cast('1 year' as interval);
						IF eff_date=r.initial_employment_date THEN
							eff_date=effdate + leaveRecord.duration_before_allocation * cast('1 year' as interval);
						ELSE
							eff_date=effdate;
						END IF;
						exp_date=eff_date + leaveRecord.validity * cast('1 year' as interval);
					END IF;
			END IF;
			-----------------------------------------------------------------------------------------------------------     
			IF leaveRecord.name='Earned_Leave' THEN     
					IF leaveRecord.deduct_per_month ='t' THEN
						work_days=(select count(wd.id) from hr_emp_workingdays_permonth wd 
						where wd.no_of_days < leaveRecord.min_days_per_month and wd.employee_id = r.id and wd.year=date_part('year', now()::date)-1);
						--IS_earnleave = (select id from hr_employee where id=r.id and initial_employment_date < (current_date - INTERVAL '12 months')::date);
						_number_of_days=leaveRecord.max_days_tobe_allocated - COALESCE( work_days::int, '0' );
						IF r.initial_employment_date < td_date::date THEN
							INSERT INTO hr_holidays(employee_id,name,holiday_status_id,number_of_days,number_of_days_temp,type,holiday_type,fiscalyear_id,state,
							department_id,create_date,write_date,message_last_post,user_id,create_uid,write_uid,manager_id2,manager_id,effective_date,expiry_date,
							section_id,meeting_id)
							VALUES (r.id,leaveRecord.name,leaveRecord.holiday_status_id,_number_of_days,_number_of_days,'add','employee',fy,'validate',
							r.department_id,now(),now(),now(),1,1,1,r.parent_id,r.parent_id,eff_date,exp_date,r.section_id,leaveRecord.categ_id);
						END IF;
					ELSE 
						IF r.initial_employment_date < td_date::date THEN
							INSERT INTO hr_holidays(employee_id,name,holiday_status_id,number_of_days,number_of_days_temp,type,holiday_type,fiscalyear_id,state,
							department_id,create_date,write_date,message_last_post,user_id,create_uid,write_uid,manager_id2,manager_id,effective_date,expiry_date,
							section_id,meeting_id)
							VALUES (r.id,leaveRecord.name,leaveRecord.holiday_status_id,leaveRecord.max_days_tobe_allocated,leaveRecord.max_days_tobe_allocated,'add','employee',fy,'validate',
							r.department_id,now(),now(),now(),1,1,1,r.parent_id,r.parent_id,eff_date,exp_date,r.section_id,leaveRecord.categ_id);
						END IF;
					END IF;
			END IF;
			IF leaveRecord.name='Medical_Leave' THEN
						work_days=(select count(id) from hr_emp_workingdays_permonth where no_of_days < leaveRecord.min_days_per_month and employee_id = r.id);
						--IS_earnleave = (select employee_id from hr_contract where employee_id=r.id and date_start < (current_date - INTERVAL '6 months')::date);
						_number_of_days=leaveRecord.max_days_tobe_allocated;
						IF r.initial_employment_date < td_date::date THEN
							INSERT INTO hr_holidays(employee_id,name,holiday_status_id,number_of_days,number_of_days_temp,type,holiday_type,fiscalyear_id,state,
							department_id,create_date,write_date,message_last_post,user_id,create_uid,write_uid,manager_id2,manager_id,effective_date,expiry_date,
							section_id,meeting_id)
							VALUES (r.id,leaveRecord.name,leaveRecord.holiday_status_id,_number_of_days,_number_of_days,'add','employee',fy,'validate',
							r.department_id,now(),now(),now(),1,1,1,r.parent_id,r.parent_id,eff_date,exp_date,r.section_id,leaveRecord.categ_id);
					END IF; 
				END IF;
				IF leaveRecord.name='Casual_Leave' THEN
					INSERT INTO hr_holidays(employee_id,name,holiday_status_id,number_of_days,number_of_days_temp,type,holiday_type,fiscalyear_id,state,
					department_id,create_date,write_date,message_last_post,user_id,create_uid,write_uid,manager_id2,manager_id,effective_date,expiry_date,
					section_id,meeting_id)
					VALUES (r.id,leaveRecord.name,leaveRecord.holiday_status_id,leaveRecord.max_days_tobe_allocated,leaveRecord.max_days_tobe_allocated,'add','employee',fy,'validate',
					r.department_id,now(),now(),now(),1,1,1,r.parent_id,r.parent_id,eff_date,exp_date,r.section_id,leaveRecord.categ_id);
			END IF;	
	     END LOOP;		        
         END LOOP;	
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION auto_allocate_leave(integer)
  OWNER TO odoo;
