# 受け取った方用：セットアップ手順

このフォルダは **Google ドライブへファイルをアップロードするツール** です。  
配布者から受け取ったら、次の順で進めてください。

---

## 含まれるもの / 含まれないもの

| ファイル | 説明 |
|---------|------|
| `upload_to_drive.py` | メインプログラム |
| `requirements.txt` | 必要なライブラリ一覧 |
| `README.md` | 全体の説明 |
| `sample.txt` | 動作確認用 |

**あなた自身で用意するもの（配布 ZIP には入っていません）**

| ファイル | 説明 |
|---------|------|
| `credentials.json` | Google Cloud から取得（後述） |
| `token.json` | 初回実行後に自動作成 |

---

## セットアップ（約20〜30分）

### 1. Python を入れる

Mac には通常 `python3` が入っています。ターミナルで確認:

```bash
python3 --version
```

### 2. フォルダに移動してライブラリを入れる

```bash
cd "（このフォルダのパス）"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Google Cloud の設定（各自の Google アカウントで）

配布者と **同じ手順** です。詳しくは `README.md` の「事前準備」を参照。

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクト作成
2. **Google Drive API** を有効化
3. **OAuth 同意画面** を設定（**テストユーザーに自分の Gmail を追加**）
4. **OAuth クライアント ID（デスクトップアプリ）** を作成
5. ダウンロードした JSON を **`credentials.json`** としてこのフォルダに保存

> **会社で1つの Google Cloud プロジェクトを共有する場合**  
> 配布者から `credentials.json` だけ渡してもらい、このフォルダに置いても構いません。  
> その場合、配布者が OAuth 同意画面の **テストユーザーにあなたの Gmail を追加** している必要があります。

### 4. 動作確認

```bash
source .venv/bin/activate
python upload_to_drive.py ./sample.txt
```

ブラウザで Google ログイン → **自分の** Google ドライブに `sample.txt` が上がれば成功です。

---

## よくある質問

**Q. 配布者のドライブに上がるの？**  
A. いいえ。ログインした **自分のアカウント** のドライブに上がります。

**Q. `credentials.json` を Slack に送ってもいい？**  
A. 社内の信頼できるメンバーに限り、チーム共有用 OAuth として渡すことはあります。社外や公開チャンネルには送らないでください。

**Q. エラー「アクセスがブロックされました」**  
A. OAuth 同意画面のテストユーザーに、ログインした Gmail が登録されているか確認してください。

---

## 使い方（再掲）

```bash
python upload_to_drive.py "./アップロードしたいファイル.pdf"
python upload_to_drive.py "./見積.pdf" --folder-id フォルダID
```
