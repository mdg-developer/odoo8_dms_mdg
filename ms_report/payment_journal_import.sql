

CREATE OR REPLACE FUNCTION public.get_cashbook_payment_seq(ms_id integer, msl_id integer)
  RETURNS integer AS
$BODY$
DECLARE
	msol_seq integer=0;
BEGIN

	WITH get_sequence AS (
		select row_number() over (order by id) as seq,id from account_bank_statement_line where statement_id=ms_id order by id
	)
	select seq into msol_seq from get_sequence where id=msl_id;

	RETURN msol_seq;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION public.get_cashbook_payment_seq(integer, integer)
  OWNER TO odoo;


CREATE OR REPLACE FUNCTION public.get_journal_import_seq(ms_id integer, msl_id integer)
  RETURNS integer AS
$BODY$
DECLARE
	msol_seq integer=0;
BEGIN

	WITH get_sequence AS (
		select row_number() over (order by id) as seq,id from account_move_line where move_id=ms_id order by id
	)
	select seq into msol_seq from get_sequence where id=msl_id;

	RETURN msol_seq;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION public.get_journal_import_seq(integer, integer)
  OWNER TO odoo;