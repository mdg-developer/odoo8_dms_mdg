CREATE TABLE report_temp
(
  employee integer,
  cal_allocated numeric,
  causal numeric,
  earn_allcated numeric,
  earn numeric,
  cal_balance numeric,
  earn_balance numeric,  
  unpaid1 numeric,
  unpaid2 numeric,
  medical1 numeric,
  medical2 numeric,
  medical3 numeric,
  maternity numeric,
  absent1 numeric,
  absent2 numeric,
  job character varying,
  emp_name character varying
)
WITH (
  OIDS=FALSE
);
ALTER TABLE report_temp
  OWNER TO openerp;
  
-- Table: incometax_temp

-- DROP TABLE incometax_temp;


CREATE TABLE incometax_temp
(
  emp_name character varying,
  dep_name character varying,
  job_name character varying,
  join_date date,
  nrc_no character varying,
  mon_wage double precision,
  year_wage double precision,
  blw double precision,
  marital character varying,
  wf_spouse numeric,
  wf_child numeric,
  wf_parent numeric,
  social_contribution numeric,
  li_amount double precision,
  amount1 numeric,
  amount2 numeric,
  amount3 numeric,
  in_tax numeric
)
-- Table: overtime_temp

-- DROP TABLE overtime_temp;

CREATE TABLE overtime_temp
(
  emp_name character varying,
  dep_name character varying,
  job_name character varying,
  att_date date,
  in_time time without time zone,
  out_time time without time zone,
  ot_hour double precision,
  amount numeric
)
WITH (
  OIDS=FALSE
);
ALTER TABLE overtime_temp
  OWNER TO openerp;
  
-- Table: emp_temp1

-- DROP TABLE emp_temp1;

CREATE TABLE emp_temp1
(
  emp_cla integer,
  job_id integer,
  hp_id integer,
  job character varying,
  emp_id integer,
  emp_name character varying,
  basic_salary numeric,
  allowance numeric,
  travel_all numeric,
  contribution numeric,
  cla numeric,
  cla1 numeric,
  cla_day numeric,
  total numeric,
  ssb numeric,
  sff numeric,
  total_value numeric,
  income_tax numeric,
  causlv numeric,
  annuallv numeric,
  unplv1 numeric,
  unplv2 numeric,
  medlv1 numeric,
  medlv2 numeric,
  medlv3 numeric,
  matlv numeric,
  abslv1 numeric,
  abslv2 numeric,
  workld1 numeric,
  workld2 numeric,
  workld3 numeric,
  workld4 numeric,
  workld5 numeric
)
WITH (
  OIDS=FALSE
);
ALTER TABLE emp_temp1
  OWNER TO openerp;



-- Table: emp_temp2

-- DROP TABLE emp_temp2;

CREATE TABLE emp_temp2
(
  emp_cla integer,
  emp_name character varying,
  job character varying,
  job_id integer,
  total_emp integer,
  basic_salary numeric,
  allowance numeric,
  travel_all numeric,
  contribution numeric,
  cla numeric,
  total numeric,
  ssb numeric,
  total_value numeric,
  income_tax numeric,
  cla1 numeric,
  cla_day numeric
)
WITH (
  OIDS=FALSE
);
ALTER TABLE emp_temp2
  OWNER TO openerp;


-- Table: employee_temp

-- DROP TABLE employee_temp;

CREATE TABLE employee_temp
(
  emp_cla integer,
  job character varying,
  job_id integer,
  total_emp integer,
  basic_salary numeric,
  allowance numeric,
  travell_amount numeric,
  contribution numeric,
  cla numeric,
  total numeric,
  ssb numeric,
  total_value numeric,
  income_tax numeric
)
WITH (
  OIDS=FALSE
);
ALTER TABLE employee_temp
  OWNER TO openerp;


-- Table: employee_temp_table

-- DROP TABLE employee_temp_table;

CREATE TABLE employee_temp_table
(
  emp_cla integer,
  job_id integer,
  hp_id integer,
  job character varying,
  emp_id integer,
  emp_name character varying,
  basic_salary numeric,
  allowance numeric,
  travell_amount numeric,
  contribution numeric,
  cla numeric,
  total numeric,
  ssb numeric,
  total_value numeric,
  income_tax numeric,
  causlv numeric,
  annuallv numeric,
  unplv1 numeric,
  unplv2 numeric,
  medlv1 numeric,
  medlv2 numeric,
  medlv3 numeric,
  matlv numeric,
  abslv1 numeric,
  abslv2 numeric,
  workld1 numeric,
  workld2 numeric,
  workld3 numeric,
  workld4 numeric,
  workld5 numeric,
  sff numeric
)
WITH (
  OIDS=FALSE
);
ALTER TABLE employee_temp_table
  OWNER TO openerp;


-- Table: fb_days_temp

-- DROP TABLE fb_days_temp;

CREATE TABLE fb_days_temp
(
  fp_no_days date,
  emp_id integer
)
WITH (
  OIDS=FALSE
);
ALTER TABLE fb_days_temp
  OWNER TO openerp;
  
-- Table: leave_days_temp

-- DROP TABLE leave_days_temp;

CREATE TABLE leave_days_temp
(
  hold_leave_days date,
  half_leave_days date,
  emp_id integer,
  hold_leave_name character varying,
  half_leave_name character varying
)
WITH (
  OIDS=FALSE
);
ALTER TABLE leave_days_temp
  OWNER TO openerp;

  
-- Table: leave_late_temp

-- DROP TABLE leave_late_temp;

CREATE TABLE leave_late_temp
(
  emp_name character varying,
  job_name character varying,
  dep_name character varying,
  no_fp date,
  whole_leave date,
  half_leave date,
  late_day date,
  action character varying
)
WITH (
  OIDS=FALSE
);
ALTER TABLE leave_late_temp
  OWNER TO openerp;

-- Table: work_histroy_temp

-- DROP TABLE work_histroy_temp;

CREATE TABLE work_histroy_temp
(
  emp_id integer,
  job_id integer,
  dep_id integer,
  f_date date,
  t_date date
)
WITH (
  OIDS=FALSE
);
ALTER TABLE work_histroy_temp
  OWNER TO openerp;

  -- Table: emp_history

-- DROP TABLE emp_history;

CREATE TABLE emp_history
(
  id bigint,
  job_name character varying,
  count1 integer,
  count2 integer,
  countsum integer
)
WITH (
  OIDS=FALSE
);
ALTER TABLE emp_history
  OWNER TO openerp;
  
  
-- Table: dep_history

-- DROP TABLE dep_history;

CREATE TABLE dep_history
(
  id bigint,
  job_name character varying,
  dep_count1 integer,
  dep_count2 integer,
  dep_count3 integer,
  dep_countsum integer
)
WITH (
  OIDS=FALSE
);
ALTER TABLE dep_history
  OWNER TO openerp;
-- Table: monthly_incometax_temp

-- DROP TABLE monthly_incometax_temp;

CREATE TABLE monthly_incometax_temp
(
  emp_id integer,
  emp_name character varying,
  dep_name character varying,
  job_name character varying,
  join_date date,
  nrc_no character varying,
  mon_wage double precision,
  year_wage double precision,
  blw double precision,
  marital character varying,
  wf_spouse numeric,
  wf_child numeric,
  wf_parent numeric,
  social_contribution numeric,
  li_amount double precision,
  amount1 numeric,
  amount2 numeric,
  amount3 numeric,
  in_tax numeric
)
WITH (
  OIDS=FALSE
);
ALTER TABLE monthly_incometax_temp
  OWNER TO openerp;

  -- Table: ssb_monthly_temp

-- DROP TABLE ssb_monthly_temp;

CREATE TABLE ssb_monthly_temp
(
  p_emp_name character varying, 
  p_job_id integer, 
  p_ssn_no character varying, 
  p_dept_name character varying,
  p_dept_id integer,
  p_ssb_empr1 numeric,
  p_ssb_empr2 numeric, 
  p_ssb_empr3 numeric,
  p_ssb_empr4 numeric,
  p_ssb_empr5 numeric, 
  p_ssb_empr6 numeric, 
  p_ssb_empr7 numeric, 
  p_ssb_empr8 numeric,
  p_ssb_empr9 numeric, 
  p_ssb_empr10 numeric, 
  p_ssb_empr11 numeric, 
  p_ssb_empr12 numeric,
  p_ssb_emp1 numeric,
  p_ssb_emp2 numeric,
  p_ssb_emp3 numeric,
  p_ssb_emp4 numeric,
  p_ssb_emp5 numeric,
  p_ssb_emp6 numeric,
  p_ssb_emp7 numeric,
  p_ssb_emp8 numeric,
  p_ssb_emp9 numeric,
  p_ssb_emp10 numeric,
  p_ssb_emp11 numeric,
  p_ssb_emp12 numeric,
  total1 numeric,
  total2 numeric,
  total3 numeric,
  total4 numeric,
  total5 numeric,
  total6 numeric,
  total7 numeric,
  total8 numeric,
  total9 numeric,
  total10 numeric,
  total11 numeric,
  total12 numeric
)
WITH (
  OIDS=FALSE
);
ALTER TABLE ssb_monthly_temp
  OWNER TO openerp;

CREATE TABLE emp_count
(
  id bigint,
  job_name character varying,
  count integer
)
WITH (
  OIDS=FALSE
);
ALTER TABLE emp_count
  OWNER TO openerp;


CREATE TABLE emp_per_pro
(
  id bigint,
  job_name character varying,
  per integer,
  pro integer,
  sum integer
)
WITH (
  OIDS=FALSE
);
ALTER TABLE emp_per_pro
  OWNER TO openerp;
  
-- Table: fp_out_absence

-- DROP TABLE fp_out_absence;

CREATE TABLE fp_out_absence
(
  fp_out_absence date,
  emp_id character varying
)
WITH (
  OIDS=FALSE
);
ALTER TABLE fp_out_absence
  OWNER TO openerp;
-- Table: incometax_payment_temp

-- DROP TABLE incometax_payment_temp;

CREATE TABLE incometax_payment_temp
(
  emp_name integer,
  dep_name character varying,
  job_name character varying,
  join_date date,
  nrc_no character varying,
  mon_wage double precision,
  year_wage double precision,
  blw double precision,
  marital character varying,
  wf_spouse numeric,
  wf_child numeric,
  wf_parent numeric,
  social_contribution numeric,
  li_amount double precision,
  amount1 numeric,
  amount2 numeric,
  amount3 numeric,
  in_tax numeric,
  bail_out_tax numeric
)
WITH (
  OIDS=FALSE
);
ALTER TABLE incometax_payment_temp
  OWNER TO openerp;

  
  -- Table: employee_dept_temp

-- DROP TABLE employee_dept_temp;

CREATE TABLE employee_dept_temp
(
  emp_cla integer,
  dept character varying,
  dept_id integer,
  total_emp integer,
  basic_salary numeric,
  allowance numeric,
  travell_amount numeric,
  contribution numeric,
  cla numeric,
  total numeric,
  ssb numeric,
  total_value numeric,
  income_tax numeric
)
WITH (
  OIDS=FALSE
);
ALTER TABLE employee_dept_temp
  OWNER TO openerp;

-- Table: employee_dept_temp_table

-- DROP TABLE employee_dept_temp_table;

CREATE TABLE employee_dept_temp_table
(
  emp_cla integer,
  dept_id integer,
  hp_id integer,
  dept character varying,
  emp_id integer,
  emp_name character varying,
  basic_salary numeric,
  allowance numeric,
  travell_amount numeric,
  contribution numeric,
  cla numeric,
  total numeric,
  ssb numeric,
  total_value numeric,
  income_tax numeric,
  causlv numeric,
  annuallv numeric,
  unplv1 numeric,
  unplv2 numeric,
  medlv1 numeric,
  medlv2 numeric,
  medlv3 numeric,
  matlv numeric,
  abslv1 numeric,
  abslv2 numeric,
  workld1 numeric,
  workld2 numeric,
  workld3 numeric,
  workld4 numeric,
  workld5 numeric,
  sff numeric
)
WITH (
  OIDS=FALSE
);
ALTER TABLE employee_dept_temp_table
  OWNER TO openerp;


