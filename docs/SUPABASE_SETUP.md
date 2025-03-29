# Supabase設定ガイド

このドキュメントでは、SmartFarm Agentアプリケーション用のSupabaseデータベースの設定方法について説明します。

## 1. テーブル構造の設定

Supabaseプロジェクトを作成した後、以下のテーブルを作成する必要があります。SQLエディタを使用して以下のSQLコマンドを実行してください。

### 組織（organizations）テーブル

```sql
CREATE TABLE organizations (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  address TEXT,
  contact_email TEXT,
  contact_phone TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLSポリシー
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "組織は認証されたユーザーのみ参照可能" ON organizations
  FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "組織は管理者のみ作成可能" ON organizations
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "組織は管理者のみ更新可能" ON organizations
  FOR UPDATE USING (auth.role() = 'authenticated');
```

### ユーザー（users）テーブル

```sql
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  auth_id UUID REFERENCES auth.users(id),
  organization_id BIGINT REFERENCES organizations(id),
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  role TEXT NOT NULL DEFAULT 'user', -- 'admin', 'user', etc.
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLSポリシー
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY "ユーザーは自分の組織のメンバーのみ参照可能" ON users
  FOR SELECT USING (
    auth.uid() = auth_id OR
    organization_id IN (
      SELECT organization_id FROM users WHERE auth_id = auth.uid()
    )
  );
CREATE POLICY "ユーザーは管理者のみ作成可能" ON users
  FOR INSERT WITH CHECK (
    auth.role() = 'authenticated' AND
    (
      SELECT role FROM users WHERE auth_id = auth.uid()
    ) = 'admin'
  );
CREATE POLICY "ユーザーは管理者または自分自身のみ更新可能" ON users
  FOR UPDATE USING (
    auth.uid() = auth_id OR
    (
      (SELECT role FROM users WHERE auth_id = auth.uid()) = 'admin' AND
      organization_id IN (
        SELECT organization_id FROM users WHERE auth_id = auth.uid()
      )
    )
  );
```

### 圃場（fields）テーブル

```sql
CREATE TABLE fields (
  id BIGSERIAL PRIMARY KEY,
  organization_id BIGINT REFERENCES organizations(id),
  name TEXT NOT NULL,
  coordinates TEXT NOT NULL, -- GeoJSON形式の座標データ（JSON文字列）
  area FLOAT, -- ヘクタール単位
  soil_type TEXT,
  crop_type TEXT,
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_by BIGINT REFERENCES users(id),
  updated_by BIGINT REFERENCES users(id)
);

-- RLSポリシー
ALTER TABLE fields ENABLE ROW LEVEL SECURITY;
CREATE POLICY "圃場は自分の組織のものだけ参照可能" ON fields
  FOR SELECT USING (
    organization_id IN (
      SELECT organization_id FROM users WHERE auth_id = auth.uid()
    )
  );
CREATE POLICY "圃場は認証されたユーザーのみ作成可能" ON fields
  FOR INSERT WITH CHECK (
    auth.role() = 'authenticated' AND
    organization_id IN (
      SELECT organization_id FROM users WHERE auth_id = auth.uid()
    )
  );
CREATE POLICY "圃場は認証されたユーザーのみ更新可能" ON fields
  FOR UPDATE USING (
    auth.role() = 'authenticated' AND
    organization_id IN (
      SELECT organization_id FROM users WHERE auth_id = auth.uid()
    )
  );
CREATE POLICY "圃場は認証されたユーザーのみ削除可能" ON fields
  FOR DELETE USING (
    auth.role() = 'authenticated' AND
    organization_id IN (
      SELECT organization_id FROM users WHERE auth_id = auth.uid()
    )
  );
```

### 作物マスタ（crops）テーブル

```sql
CREATE TABLE crops (
  id BIGSERIAL PRIMARY KEY,
  organization_id BIGINT REFERENCES organizations(id),
  name TEXT NOT NULL,
  category TEXT,
  growing_period INTEGER, -- 生育日数
  planting_season TEXT, -- 植付け時期
  harvesting_season TEXT, -- 収穫時期
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLSポリシー
ALTER TABLE crops ENABLE ROW LEVEL SECURITY;
CREATE POLICY "作物は自分の組織のものだけ参照可能" ON crops
  FOR SELECT USING (
    organization_id IN (
      SELECT organization_id FROM users WHERE auth_id = auth.uid()
    )
  );
CREATE POLICY "作物は認証されたユーザーのみ作成可能" ON crops
  FOR INSERT WITH CHECK (
    auth.role() = 'authenticated' AND
    organization_id IN (
      SELECT organization_id FROM users WHERE auth_id = auth.uid()
    )
  );
```

### 作業カテゴリ（crop_work_categories）テーブル

```sql
CREATE TABLE crop_work_categories (
  id BIGSERIAL PRIMARY KEY,
  organization_id BIGINT REFERENCES organizations(id),
  name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLSポリシー
ALTER TABLE crop_work_categories ENABLE ROW LEVEL SECURITY;
CREATE POLICY "作業カテゴリは自分の組織のものだけ参照可能" ON crop_work_categories
  FOR SELECT USING (
    organization_id IN (
      SELECT organization_id FROM users WHERE auth_id = auth.uid()
    )
  );
```

### 作業テンプレート（crop_workflow_templates）テーブル

```sql
CREATE TABLE crop_workflow_templates (
  id BIGSERIAL PRIMARY KEY,
  organization_id BIGINT REFERENCES organizations(id),
  crop_id BIGINT REFERENCES crops(id),
  category_id BIGINT REFERENCES crop_work_categories(id),
  name TEXT NOT NULL,
  description TEXT,
  days_from_planting INTEGER, -- 植付けからの日数
  duration_hours FLOAT, -- 作業時間（時間）
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLSポリシー
ALTER TABLE crop_workflow_templates ENABLE ROW LEVEL SECURITY;
CREATE POLICY "作業テンプレートは自分の組織のものだけ参照可能" ON crop_workflow_templates
  FOR SELECT USING (
    organization_id IN (
      SELECT organization_id FROM users WHERE auth_id = auth.uid()
    )
  );
```

### 作付け計画（cultivation_plans）テーブル

```sql
CREATE TABLE cultivation_plans (
  id BIGSERIAL PRIMARY KEY,
  organization_id BIGINT REFERENCES organizations(id),
  field_id BIGINT REFERENCES fields(id),
  crop_id BIGINT REFERENCES crops(id),
  name TEXT NOT NULL,
  planting_date DATE,
  expected_harvest_date DATE,
  status TEXT DEFAULT 'planned', -- 'planned', 'in_progress', 'completed', 'canceled'
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_by BIGINT REFERENCES users(id),
  updated_by BIGINT REFERENCES users(id)
);

-- RLSポリシー
ALTER TABLE cultivation_plans ENABLE ROW LEVEL SECURITY;
CREATE POLICY "作付け計画は自分の組織のものだけ参照可能" ON cultivation_plans
  FOR SELECT USING (
    organization_id IN (
      SELECT organization_id FROM users WHERE auth_id = auth.uid()
    )
  );
```

### 予定タスク（scheduled_tasks）テーブル

```sql
CREATE TABLE scheduled_tasks (
  id BIGSERIAL PRIMARY KEY,
  organization_id BIGINT REFERENCES organizations(id),
  cultivation_plan_id BIGINT REFERENCES cultivation_plans(id),
  category_id BIGINT REFERENCES crop_work_categories(id),
  name TEXT NOT NULL,
  description TEXT,
  scheduled_date DATE NOT NULL,
  duration_hours FLOAT,
  assignee_id BIGINT REFERENCES users(id),
  status TEXT DEFAULT 'scheduled', -- 'scheduled', 'in_progress', 'completed', 'canceled'
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_by BIGINT REFERENCES users(id),
  updated_by BIGINT REFERENCES users(id)
);

-- RLSポリシー
ALTER TABLE scheduled_tasks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "予定タスクは自分の組織のものだけ参照可能" ON scheduled_tasks
  FOR SELECT USING (
    organization_id IN (
      SELECT organization_id FROM users WHERE auth_id = auth.uid()
    )
  );
```

### 資材/農機（resources）テーブル

```sql
CREATE TABLE resources (
  id BIGSERIAL PRIMARY KEY,
  organization_id BIGINT REFERENCES organizations(id),
  name TEXT NOT NULL,
  type TEXT NOT NULL, -- 'material', 'equipment'
  category TEXT,
  quantity FLOAT,
  unit TEXT,
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLSポリシー
ALTER TABLE resources ENABLE ROW LEVEL SECURITY;
CREATE POLICY "資材/農機は自分の組織のものだけ参照可能" ON resources
  FOR SELECT USING (
    organization_id IN (
      SELECT organization_id FROM users WHERE auth_id = auth.uid()
    )
  );
```

### 使用ログ（usage_logs）テーブル

```sql
CREATE TABLE usage_logs (
  id BIGSERIAL PRIMARY KEY,
  organization_id BIGINT REFERENCES organizations(id),
  resource_id BIGINT REFERENCES resources(id),
  task_id BIGINT REFERENCES scheduled_tasks(id),
  quantity_used FLOAT,
  usage_date DATE NOT NULL,
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_by BIGINT REFERENCES users(id)
);

-- RLSポリシー
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "使用ログは自分の組織のものだけ参照可能" ON usage_logs
  FOR SELECT USING (
    organization_id IN (
      SELECT organization_id FROM users WHERE auth_id = auth.uid()
    )
  );
```

## 2. 初期データの投入

基本的なデータを投入するためのSQLコマンドの例：

```sql
-- 組織の作成
INSERT INTO organizations (name, address, contact_email)
VALUES ('サンプル農場', '東京都千代田区1-1-1', 'info@example.com');

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
```

## 3. Supabase認証の設定

Supabaseダッシュボードの「Authentication」→「Settings」で以下の設定を行います：

1. **Email Auth**を有効化
   - 「Enable Email Signup」をオンにします
   - 「Confirm Email」は任意（開発中はオフでも可）

2. **Site URL**の設定
   - フロントエンドのURLを設定します（例：`http://localhost:3000`）

3. **Redirect URLs**の設定
   - フロントエンドのコールバックURLを追加します（例：`http://localhost:3000/auth/callback`）

## 4. バックエンドとの接続確認

Supabaseの設定が完了したら、バックエンドからの接続をテストします：

1. `.env`ファイルに正しいSupabase URLとAPIキーが設定されていることを確認します
2. バックエンドサーバーを起動します：
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```
3. ブラウザで`http://localhost:8000/docs`にアクセスし、SwaggerUIからAPIエンドポイントをテストします

## 5. フロントエンドとの接続確認

フロントエンドからSupabaseへの直接アクセスが必要な場合は、以下の設定を行います：

1. `.env.local`ファイルに以下の行を追加します：
   ```
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url_here
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here
   ```

2. フロントエンドサーバーを起動します：
   ```bash
   cd frontend
   npm run dev
   ```

3. ブラウザで`http://localhost:3000`にアクセスし、アプリケーションの動作を確認します
