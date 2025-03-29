-- 初期データ投入用SQLスクリプト

-- 組織の作成
INSERT INTO organizations (name, address, contact_email)
VALUES ('サンプル農場', '東京都千代田区1-1-1', 'info@example.com');

-- 管理者ユーザーの作成（auth.usersテーブルへの参照は実際のユーザー登録後に更新する必要があります）
-- 注意: auth_idは実際のSupabase Authで作成されたユーザーのUUIDに置き換える必要があります
INSERT INTO users (auth_id, organization_id, name, email, role)
VALUES 
  (NULL, 1, '管理者ユーザー', 'admin@example.com', 'admin');

-- 作業カテゴリの作成
INSERT INTO crop_work_categories (organization_id, name, description)
VALUES 
  (1, '耕起', '土を耕す作業'),
  (1, '播種', '種をまく作業'),
  (1, '施肥', '肥料を与える作業'),
  (1, '防除', '病害虫対策の作業'),
  (1, '収穫', '作物を収穫する作業');

-- 作物マスタの作成
INSERT INTO crops (organization_id, name, category, growing_period, planting_season, harvesting_season)
VALUES 
  (1, '米（コシヒカリ）', '穀物', 120, '4月-5月', '9月-10月'),
  (1, '小麦', '穀物', 240, '10月-11月', '6月-7月'),
  (1, '大豆', '豆類', 120, '6月', '10月-11月'),
  (1, 'トマト', '野菜', 90, '3月-4月', '7月-9月'),
  (1, 'キャベツ', '野菜', 90, '3月/8月', '6月/11月');

-- サンプル圃場の作成
INSERT INTO fields (organization_id, name, coordinates, area, soil_type, crop_type, notes, created_by)
VALUES 
  (1, '北圃場', '[{"lat":35.6895,"lng":139.6917},{"lat":35.6905,"lng":139.6927},{"lat":35.6915,"lng":139.6917},{"lat":35.6905,"lng":139.6907}]', 1.5, '黒ボク土', '米（コシヒカリ）', 'サンプル圃場です', 1),
  (1, '南圃場', '[{"lat":35.6855,"lng":139.6917},{"lat":35.6865,"lng":139.6927},{"lat":35.6875,"lng":139.6917},{"lat":35.6865,"lng":139.6907}]', 2.0, '砂質土', '小麦', 'サンプル圃場です', 1);

-- サンプル作付け計画の作成
INSERT INTO cultivation_plans (organization_id, field_id, crop_id, name, planting_date, expected_harvest_date, status, created_by)
VALUES 
  (1, 1, 1, '2025年コシヒカリ栽培', '2025-04-15', '2025-09-15', 'planned', 1),
  (1, 2, 2, '2025年小麦栽培', '2024-10-20', '2025-06-20', 'in_progress', 1);

-- サンプル予定タスクの作成
INSERT INTO scheduled_tasks (organization_id, cultivation_plan_id, category_id, name, description, scheduled_date, duration_hours, assignee_id, created_by)
VALUES 
  (1, 1, 1, '北圃場耕起', '北圃場の耕起作業', '2025-04-01', 4, 1, 1),
  (1, 1, 2, '北圃場播種', '北圃場の播種作業', '2025-04-15', 6, 1, 1),
  (1, 2, 4, '南圃場防除', '南圃場の防除作業', '2025-03-15', 3, 1, 1);

-- サンプル資材の作成
INSERT INTO resources (organization_id, name, type, category, quantity, unit)
VALUES 
  (1, 'コシヒカリ種子', 'material', '種子', 100, 'kg'),
  (1, '化成肥料', 'material', '肥料', 500, 'kg'),
  (1, 'トラクター', 'equipment', '農機', 2, '台'),
  (1, 'コンバイン', 'equipment', '農機', 1, '台');

-- サンプル使用ログの作成
INSERT INTO usage_logs (organization_id, resource_id, task_id, quantity_used, usage_date, created_by)
VALUES 
  (1, 1, 2, 50, '2025-04-15', 1),
  (1, 3, 1, 1, '2025-04-01', 1);
