# Supabase手動設定ガイド

このドキュメントでは、Supabaseダッシュボードを使用してSmartFarm Agentアプリケーション用のデータベースを手動で設定する手順を説明します。

## 1. Supabaseダッシュボードへのアクセス

1. [Supabase](https://app.supabase.com)にログインします
2. プロジェクト「bnfdzyimjqptdethyeve」を選択します

## 2. テーブルの作成

### SQLエディタの使用

1. 左側のナビゲーションから「SQL Editor」を選択します
2. 「New Query」をクリックして新しいSQLエディタを開きます
3. 以下のファイルの内容をコピーしてエディタに貼り付けます：
   - `/smartfarm/backend/db/init_tables.sql`
4. 「Run」ボタンをクリックしてSQLを実行します

### テーブル作成の確認

1. 左側のナビゲーションから「Table Editor」を選択します
2. 以下のテーブルが作成されていることを確認します：
   - organizations
   - users
   - fields
   - crops
   - crop_work_categories
   - crop_workflow_templates
   - cultivation_plans
   - scheduled_tasks
   - resources
   - usage_logs

## 3. サンプルデータの投入

1. 左側のナビゲーションから「SQL Editor」を選択します
2. 「New Query」をクリックして新しいSQLエディタを開きます
3. 以下のファイルの内容をコピーしてエディタに貼り付けます：
   - `/smartfarm/backend/db/seed_data.sql`
4. 「Run」ボタンをクリックしてSQLを実行します

### 注意事項

サンプルデータのSQLには、auth.usersテーブルへの参照（auth_id）がNULLになっています。実際のユーザー登録後に、以下のSQLを実行して更新する必要があります：

```sql
-- 実際のauth.usersのUUIDを取得
SELECT id FROM auth.users WHERE email = 'your_registered_email@example.com';

-- usersテーブルのauth_idを更新
UPDATE users SET auth_id = 'ここに取得したUUID' WHERE email = 'admin@example.com';
```

## 4. RLSポリシーの確認

1. 左側のナビゲーションから「Authentication」→「Policies」を選択します
2. 各テーブルに対して適切なRLSポリシーが設定されていることを確認します

## 5. 認証設定

1. 左側のナビゲーションから「Authentication」→「Providers」を選択します
2. 「Email」プロバイダーが有効になっていることを確認します
3. 必要に応じて「Phone」や「OAuth」プロバイダーも設定します

## 6. APIキーの確認

1. 左側のナビゲーションから「Project Settings」→「API」を選択します
2. 「Project URL」と「anon/public」キーが正しく環境変数に設定されていることを確認します：
   - SUPABASE_URL=https://bnfdzyimjqptdethyeve.supabase.co
   - SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJuZmR6eWltanFwdGRldGh5ZXZlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDMyMjU1NzMsImV4cCI6MjA1ODgwMTU3M30.SPEEI1UOgAz3BekMZ_IjiT3VlPxKuRNXZbuWKiSxeuw

## 7. バックエンドとの接続テスト

バックエンドサーバーを起動して接続をテストします：

```bash
cd backend
uvicorn app.main:app --reload
```

ブラウザで`http://localhost:8000/docs`にアクセスし、SwaggerUIからAPIエンドポイントをテストします。
