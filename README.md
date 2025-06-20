# コンサル向けシミュレーションツール

## 概要
コンサルティング業務でよく使用される財務シミュレーションを簡単に作成できるWebアプリケーションです。業界別プリセットやAI最適化提案機能を備え、プロフェッショナルなビジネス分析をサポートします。

## 🌟 主な機能
- 📈 **売上・費用・利益の月次シミュレーション**
  - 初月売上と成長率を設定して将来予測
  - 季節変動を考慮した詳細な分析
- 🏢 **業界別プリセット**
  - EC・小売業（年末商戦対応）
  - 旅行・レジャー（GW、夏休み、年末年始ピーク）
  - BtoB企業（年度末、四半期末強化）
  - スタートアップ（資金調達時期考慮）
- 🤖 **AI最適化提案**
  - ROAS改善提案
  - 利益率安定化アドバイス
  - 赤字月の警告と対策
- 📊 **インタラクティブなビジュアライゼーション**
  - Plotlyによる動的グラフ
  - リアルタイムでの結果反映
- 📁 **データエクスポート**
  - Excel形式（xlsxwriter使用）
  - CSV形式（UTF-8 BOM付き）
- 🎯 **KPI自動計算**
  - ROAS（広告費用対効果）
  - 利益率
  - 月次成長率
- 📱 **レスポンシブデザイン**

## ローカル実行

```bash
# 依存関係インストール
pip install -r requirements.txt

# アプリ起動
streamlit run app.py
```

## デプロイ方法

### Streamlit Cloud (推奨・無料)

#### 事前準備
1. **GitHubアカウント**が必要です（無料）
2. **Streamlit Cloudアカウント**を作成（GitHubアカウントでサインイン可能）

#### デプロイ手順

1. **GitHubにリポジトリを作成**
   ```bash
   # 初期化（まだの場合）
   git init
   
   # .gitignoreを作成（推奨）
   echo "keywords/" > .gitignore
   echo "__pycache__/" >> .gitignore
   echo "*.pyc" >> .gitignore
   echo ".DS_Store" >> .gitignore
   
   # ファイルを追加
   git add .
   git commit -m "Initial commit"
   
   # GitHubリポジトリに接続
   git remote add origin https://github.com/[あなたのユーザー名]/[リポジトリ名].git
   git branch -M main
   git push -u origin main
   ```

2. **Streamlit Cloudでデプロイ**
   - [share.streamlit.io](https://share.streamlit.io) にアクセス
   - GitHubアカウントでサインイン
   - "New app" をクリック
   - 以下を選択：
     - Repository: `[あなたのユーザー名]/[リポジトリ名]`
     - Branch: `main`
     - Main file path: `app.py`
   - "Deploy!" をクリック

3. **デプロイ完了**
   - 数分でデプロイが完了します
   - URLは `https://[アプリ名]-[ランダム文字列].streamlit.app` の形式になります
   - カスタムドメインの設定も可能です（有料プラン）

#### 注意事項
- 無料プランでは月1,000時間まで利用可能
- プライベートリポジトリも無料でデプロイ可能
- デプロイ後も自動的に更新されます（GitHubにpushするだけ）

### Heroku
```bash
# Procfileとsetup.shが必要
echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
```

### Replit
1. Replit.comでアカウント作成
2. "Import from GitHub" でリポジトリをインポート
3. "Run" ボタンでデプロイ

## 使用技術
- Python 3.8+
- Streamlit
- Pandas
- Plotly
- NumPy

## トラブルシューティング

### よくある問題と解決方法

1. **ModuleNotFoundError**
   ```bash
   # 依存関係を再インストール
   pip install -r requirements.txt
   ```

2. **Streamlit Cloudでのデプロイエラー**
   - requirements.txtに全ての依存関係が記載されているか確認
   - Python バージョンが3.8以上か確認
   - リポジトリがpublicまたは適切に認証されているか確認

3. **Excel出力エラー**
   ```bash
   # xlsxwriterとopenpyxlを確実にインストール
   pip install xlsxwriter openpyxl
   ```

## ライセンス
MITライセンス

## 作成者
このアプリケーションはコンサルティング業務の効率化を目的として作成されました。