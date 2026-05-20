# Google ドライブへファイルをアップロード

ローカルのファイルを [Google Drive API](https://developers.google.com/drive) で Google ドライブにアップロードするサンプルです。

## 仕組み（3ステップ）

1. **Google Cloud で API を有効化** … あなたのアプリがドライブを使う許可をもらう
2. **OAuth でログイン** … 初回だけブラウザで Google アカウントにログイン
3. **`files().create` でアップロード** … ローカルファイルをドライブに送る

## 事前準備

### 1. Google Cloud Console の設定

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成
2. **API とサービス** → **ライブラリ** → 「Google Drive API」を検索して **有効化**
3. **API とサービス** → **OAuth 同意画面** を設定（テストユーザーに自分の Gmail を追加）
4. **認証情報** → **認証情報を作成** → **OAuth クライアント ID**
   - アプリケーションの種類: **デスクトップアプリ**
5. ダウンロードした JSON を、このフォルダに **`credentials.json`** という名前で保存

### 2. Python 環境

```bash
cd "/Users/gotoumasato/Desktop/AIエンジニア/API連携実践課題"
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 使い方

```bash
# マイドライブ直下にアップロード
python upload_to_drive.py ./sample.txt

# 特定フォルダにアップロード（フォルダ ID はドライブの URL から取得）
python upload_to_drive.py ./photo.jpg --folder-id 1a2b3c4d5e6f7g8h9i0j
```

初回実行時、ブラウザが開き Google ログインを求められます。成功すると `token.json` が作られ、次回からは自動で認証されます。

## フォルダ ID の見つけ方

Google ドライブでフォルダを開いたときの URL:

`https://drive.google.com/drive/folders/【ここがフォルダID】`

## ファイル構成

| ファイル | 説明 |
|---------|------|
| `upload_to_drive.py` | アップロード処理の本体 |
| `credentials.json` | Cloud Console から取得（**自分で配置・Git に含めない**） |
| `token.json` | 初回ログイン後に自動生成（**Git に含めない**） |
| `requirements.txt` | 必要な Python パッケージ |

## 注意

- `credentials.json` と `token.json` は他人に渡さないでください
- スコープ `drive.file` は「このアプリが作成したファイル」のみ操作可能で、安全寄りの設定です

---

## 他の方にこのシステムを共有する

### 渡してよいもの / 渡してはいけないもの

| 渡す ✅ | 渡さない ❌ |
|--------|------------|
| `upload_to_drive.py` | `credentials.json`（原則・各自取得が安全） |
| `requirements.txt` | `token.json`（あなたのログイン情報） |
| `README.md` | `.venv/` フォルダ（環境は各自で作成） |
| `SETUP_FOR_TEAM.md` | |
| `sample.txt` | |

### 共有の2パターン

| パターン | 内容 | 向いている場面 |
|---------|------|----------------|
| **A. 各自で Google Cloud 設定** | コードだけ渡す。相手が自分用に `credentials.json` を取得 | 個人利用・人数が少ない |
| **B. 会社で1プロジェクト共有** | 管理者が OAuth を1つ作り、**テストユーザーに全員の Gmail を追加**。`credentials.json` を社内で配布 | チームで同じ設定に揃えたい |

どちらの場合も、**アップロード先はログインした人の Google ドライブ** です（相手の PC にあなたの `token.json` を渡しても、あなたのドライブには上がりません）。

### 手順：ZIP で渡す（いちばん簡単）

ターミナルでプロジェクトフォルダに移動し:

```bash
chmod +x pack_for_sharing.sh
./pack_for_sharing.sh
```

デスクトップのひとつ上に `drive-upload-tool.zip` ができます。これをメール・Slack・社内ドライブで渡し、相手には **`SETUP_FOR_TEAM.md`** を読んでもらいます。

### 手順：GitHub で渡す

1. リポジトリを作成（Private 推奨）
2. `credentials.json` と `token.json` は `.gitignore` 済みなのでコミットされない
3. 相手を Collaborator に追加、または ZIP を Release に添付

### 共有後、相手がやること（要約）

1. ZIP を解凍
2. `python3 -m venv .venv` → `pip install -r requirements.txt`
3. 自分用の `credentials.json` を用意（または社内共有のものを配置）
4. `python upload_to_drive.py ./sample.txt` で動作確認

詳細は **`SETUP_FOR_TEAM.md`**（受け取った人向け）を参照。
