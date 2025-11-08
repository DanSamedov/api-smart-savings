select * from app_user;

select * from wallet;

select w.id as wallet_id, au.full_name as user_full_name, au.email as user_email, w.updated_at, w.total_balance, w.locked_amount
from wallet as w inner join app_user as au on w.user_id = au.id;

