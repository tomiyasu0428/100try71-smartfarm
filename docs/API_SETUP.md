# API設定ガイド

このドキュメントでは、SmartFarm Agentアプリケーションで使用する各種APIの設定方法について説明します。

## 1. Google Maps API

### APIキーの取得手順

1. [Google Cloud Platform](https://console.cloud.google.com/)にアクセスし、アカウントを作成またはログインします。
2. 新しいプロジェクトを作成します。
3. 左側のナビゲーションから「APIとサービス」→「ライブラリ」を選択します。
4. 以下のAPIを有効化します：
   - Maps JavaScript API
   - Geocoding API
   - Drawing Library
   - Geometry Library
5. 「APIとサービス」→「認証情報」を選択します。
6. 「認証情報を作成」→「APIキー」をクリックします。
7. 作成されたAPIキーをコピーします。
8. （推奨）APIキーの制限を設定します：
   - HTTPリファラーの制限（アプリケーションのドメインのみ）
   - APIの制限（Maps JavaScript APIのみ）

### APIキーの設定

#### フロントエンド（Next.js）
`.env.local`ファイルに以下の行を追加します：
```
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

#### バックエンド（FastAPI）
`.env`ファイルに以下の行を追加します：
```
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

## 2. OpenAI API

### APIキーの取得手順

1. [OpenAIのウェブサイト](https://platform.openai.com/)にアクセスし、アカウントを作成またはログインします。
2. 右上のプロファイルアイコンをクリックし、「View API keys」を選択します。
3. 「Create new secret key」をクリックします。
4. キーの名前を入力し、「Create secret key」をクリックします。
5. 生成されたAPIキーをコピーします（このキーは一度しか表示されないため、安全な場所に保存してください）。

### APIキーの設定

バックエンド（FastAPI）の`.env`ファイルに以下の行を追加します：
```
OPENAI_API_KEY=your_openai_api_key_here
```

## 3. Supabase

### プロジェクト作成手順

1. [Supabaseのウェブサイト](https://supabase.com/)にアクセスし、アカウントを作成またはログインします。
2. 「New Project」をクリックします。
3. プロジェクト名、パスワード、リージョンを設定します。
4. 「Create new project」をクリックします。
5. プロジェクトが作成されるまで待ちます（数分かかる場合があります）。

### 接続情報の取得

1. プロジェクトのダッシュボードで「Settings」→「API」を選択します。
2. 「Project URL」と「anon/public」キーをコピーします。

### 接続情報の設定

バックエンド（FastAPI）の`.env`ファイルに以下の行を追加します：
```
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_KEY=your_supabase_anon_key_here
```

## 4. JWT認証用のシークレットキー

バックエンド（FastAPI）の`.env`ファイルに以下の行を追加します：
```
SECRET_KEY=your_secure_random_string_here
```

シークレットキーは、以下のPythonコードで生成できます：
```python
import secrets
print(secrets.token_hex(32))
```

## 環境変数の設定確認

すべての環境変数が正しく設定されているか確認するには、以下のファイルを参照してください：

- フロントエンド：`.env.local`
- バックエンド：`.env`

これらのファイルは、バージョン管理システムにコミットしないでください。代わりに、`.env.example`や`.env.local.example`ファイルをテンプレートとして提供することをお勧めします。
