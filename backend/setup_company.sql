-- Island Glass CRM - Company Setup for User
-- Run this in Supabase SQL Editor

-- Step 1: Create a company for your business
INSERT INTO companies (name)
VALUES ('Island Glass & Mirror')
RETURNING id;

-- Step 2: Copy the UUID from the result above, then run this:
-- (Replace 'YOUR-COMPANY-UUID-HERE' with the actual UUID from step 1)
/*
UPDATE user_profiles
SET company_id = 'YOUR-COMPANY-UUID-HERE'
WHERE id = '48990466-d8c8-45e0-8254-f32a2ea76437';
*/

-- After running both steps, your user will have a company_id and RLS will work!
