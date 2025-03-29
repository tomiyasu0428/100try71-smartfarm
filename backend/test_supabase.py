import os
from dotenv import load_dotenv
from supabase import create_client

# .envファイルから環境変数を読み込む
load_dotenv()

# Supabase接続情報を取得
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# 接続情報を表示
print(f"接続先URL: {supabase_url}")
print(f"APIキー: {supabase_key[:10]}...（セキュリティのため一部のみ表示）")

try:
    # Supabaseクライアントを作成
    supabase = create_client(supabase_url, supabase_key)
    
    # 簡単なクエリを実行（テーブルが存在するかどうかに関わらず接続テストになる）
    response = supabase.table("organizations").select("*").limit(1).execute()
    
    # 接続成功
    print("Supabaseへの接続に成功しました！")
    print(f"レスポンス: {response}")
    
except Exception as e:
    # 接続失敗
    print(f"Supabaseへの接続に失敗しました: {str(e)}")
