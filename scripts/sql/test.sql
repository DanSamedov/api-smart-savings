-- Retrieve only non-deleted users
select * from app_user as au where au.is_anonymized is not True;

select * from wallet order by total_balance desc;

-- -- Retrieve only non-deleted users and their wallet details
select w.id as wallet_id, au.full_name as user_full_name, au.email as user_email, w.updated_at, w.total_balance, w.locked_amount
from wallet as w inner join app_user as au on w.user_id = au.id
where au.is_anonymized is not True
order by au.email asc
limit 5;


-- -- -- Retrieve all transactions along with user email
-- -- select txn.id as txn_id, au.email as user_email, txn.amount as amount, txn.type as txn_type, txn.executed_at as executed_at
-- -- from transaction as txn inner join app_user as au on txn.owner_id = au.id
-- -- order by executed_at desc;

