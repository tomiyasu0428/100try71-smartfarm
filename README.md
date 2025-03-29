# SmartFarm Agent - AI農場管理アプリ

SmartFarm Agentは、大規模農場や農業チーム向けに、地図インターフェースやチャットベースで営農データ（圃場・資材・作業スケジュールなど）にアクセス・更新できるアプリケーションです。OpenAI Agents SDKを使ったAIエージェントとの対話を通じて、作業予定の管理や作業記録の自動化、問い合わせ応答を可能にします。

## 機能

- **圃場管理**: Google Maps APIを使用した圃場の地図表示、ポリゴン描画、面積自動計算
- **作業予定管理**: 作業の登録、カレンダー表示、担当者割り当て
- **資材・農機管理**: 在庫管理、使用記録
- **AIチャット**: OpenAI Agents SDKを使用した自然言語での操作と問い合わせ
- **レポート生成**: 作業履歴や収穫データの可視化

## 技術スタック

### バックエンド
- Python 3.9+
- FastAPI
- Supabase (PostgreSQL)
- OpenAI Agents SDK

### フロントエンド
- TypeScript
- React / Next.js
- Material UI
- Google Maps API

## 開発環境のセットアップ

### 前提条件
- Python 3.9以上
- Node.js 16以上
- npm または yarn
- Supabaseアカウント
- Google Maps APIキー
- OpenAI APIキー

### バックエンドのセットアップ

1. リポジトリをクローン
```bash
git clone <repository-url>
cd smartfarm
```

2. 仮想環境の作成と有効化
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
```

3. 依存関係のインストール
```bash
pip install -r requirements.txt
```

4. 環境変数の設定
```bash
cp .env.example .env
# .envファイルを編集して必要な環境変数を設定
```

5. サーバーの起動
```bash
uvicorn app.main:app --reload
```

### フロントエンドのセットアップ

1. 依存関係のインストール
```bash
cd frontend
npm install
```

2. 環境変数の設定
```bash
cp .env.local.example .env.local
# .env.localファイルを編集して必要な環境変数を設定
```

3. 開発サーバーの起動
```bash
npm run dev
```

## データベース設定

Supabaseで以下のテーブルを作成する必要があります：

- organizations: 組織情報
- users: ユーザー情報
- fields: 圃場情報
- crops: 作物マスタ
- crop_work_categories: 作業カテゴリ
- crop_workflow_templates: 作業テンプレート
- cultivation_plans: 作付け計画
- scheduled_tasks: 予定タスク
- resources: 資材/農機
- usage_logs: 使用ログ

詳細なスキーマ定義は `docs/` ディレクトリを参照してください。

## API仕様

バックエンドAPIの仕様は、サーバー起動後に以下のURLでSwagger UIを通じて確認できます：

```
http://localhost:8000/docs
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
