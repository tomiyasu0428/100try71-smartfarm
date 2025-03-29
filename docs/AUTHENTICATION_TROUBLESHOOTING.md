# 認証システムのトラブルシューティングと本番環境設定ガイド

## 開発中に発生したエラーと解決策

### 1. RLSポリシーの無限再帰エラー

**エラー内容:**
```
postgrest.exceptions.APIError: {'code': '42P17', 'details': None, 'hint': None, 'message': 'infinite recursion detected in policy for relation "users"'}
```

**原因:**
`users`テーブルのRLSポリシーが自分自身を参照する循環参照になっていました。例えば、以下のようなポリシーが問題を引き起こしていました：

```sql
CREATE POLICY "ユーザーは自分の組織のメンバーのみ参照可能" ON users
  FOR SELECT USING (
    organization_id IN (
      SELECT organization_id FROM users WHERE auth_id = auth.uid()
    )
  );
```

**解決策:**
1. 循環参照を避けるポリシーに修正
2. 開発段階ではRLSを一時的に無効化

```sql
-- RLSを一時的に無効化
ALTER TABLE "public"."users" DISABLE ROW LEVEL SECURITY;
```

### 2. BIGINT型とUUID型の不一致エラー

**エラー内容:**
```
"ユーザー登録に失敗しました: {'code': '22P02', 'details': None, 'hint': None, 'message': 'invalid input syntax for type bigint: \"7ae5d2e9-afcf-4ddb-ba7a-32221404a6ba\"'}"
```

**原因:**
`users`テーブルの`id`フィールドがBIGINT型なのに、UUIDフォーマットの文字列を挿入しようとしていました。

**解決策:**
`id`フィールドはBIGSERIAL型（自動採番）なので、挿入時に指定せず、自動生成されるようにコードを修正しました。

### 3. 外部キー制約違反エラー

**エラー内容:**
```
"Key (auth_id)=(c7468800-d038-4736-a534-ff469998a1fa) is not present in table \"users\"."
"insert or update on table \"users\" violates foreign key constraint \"users_auth_id_fkey\""
```

**原因:**
`users`テーブルの`auth_id`フィールドが`auth.users`テーブルの`id`を参照する外部キー制約があるため、`auth.users`テーブルに存在しないUUIDを設定しようとして制約違反が発生しました。

**解決策:**
開発段階では、外部キー制約を一時的に削除しました：

```sql
-- 外部キー制約を一時的に削除
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_auth_id_fkey;

-- auth_idをNULLABLEに変更（オプション）
ALTER TABLE users ALTER COLUMN auth_id DROP NOT NULL;
```

## 本番環境への移行前に必要な設定

開発の便宜上、いくつかの制約やセキュリティ設定を一時的に緩和しましたが、本番環境に移行する前に以下の設定を必ず行ってください：

### 1. RLSポリシーの再設定

```sql
-- usersテーブルのRLSを有効化
ALTER TABLE "public"."users" ENABLE ROW LEVEL SECURITY;

-- 適切なポリシーを設定（循環参照を避ける）
CREATE POLICY "ユーザーは自分自身のレコードのみ参照可能" ON users
  FOR SELECT USING (auth_id = auth.uid());

CREATE POLICY "管理者は同じ組織のユーザーを参照可能" ON users
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM users u
      WHERE u.auth_id = auth.uid() AND u.role = 'admin'
      AND u.organization_id = users.organization_id
    )
  );
```

### 2. 外部キー制約の再設定

```sql
-- auth_idの外部キー制約を再設定
ALTER TABLE users
  ADD CONSTRAINT users_auth_id_fkey
  FOREIGN KEY (auth_id) REFERENCES auth.users(id);
```

### 3. 認証フローの修正

開発段階では認証フローをバイパスしていましたが、本番環境では適切なSupabase認証フローを使用するようにコードを修正してください：

```python
# Supabaseの認証を使用してユーザーを登録
response = user_service.supabase.auth.sign_up({
    "email": user_in.email,
    "password": user_in.password
})

# ユーザーテーブルにも情報を保存
user_data = {
    "auth_id": response.user.id,
    "name": user_in.name,
    "email": user_in.email,
    "organization_id": user_in.organization_id,
    "role": user_in.role
}

user_service.supabase.table("users").insert(user_data).execute()
```

### 4. セキュリティ設定の確認

- 強力なパスワードポリシーの設定
- JWTトークンの有効期限の適切な設定
- CORS設定の制限（許可するオリジンを本番環境のドメインに限定）
- 環境変数の保護（本番環境のシークレットキーは開発環境とは別のものを使用）

### 5. エラーハンドリングの強化

- より詳細なエラーメッセージをログに記録
- ユーザーに表示するエラーメッセージはセキュリティ情報を含まないように注意
- 適切なHTTPステータスコードの使用

これらの設定を適切に行うことで、セキュアで堅牢な認証システムを構築できます。
