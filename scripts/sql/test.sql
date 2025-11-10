-- - Retrieve only non-deleted users
select * from app_user as au where au.is_anonymized is not True;

select * from wallet;

-- - Retrieve only non-deleted users and their wallet details
select w.id as wallet_id, au.full_name as user_full_name, au.email as user_email, w.updated_at, w.total_balance, w.locked_amount
from wallet as w inner join app_user as au on w.user_id = au.id
where au.is_anonymized is not True
order by au.email asc
limit 1;

