"""
Google Docs に新規ドキュメントを作成し、指定したテキストを挿入するスクリプト

使い方:
  python create_google_doc.py "こんにちは、Google Docs API です。"
  python create_google_doc.py "本文テキスト" --title "マイドキュメント"
"""

import argparse
import os
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Google ドキュメントの作成・編集権限
SCOPES = ["https://www.googleapis.com/auth/documents"]

TOKEN_FILE = "token_docs.json"
CREDENTIALS_FILE = "credentials.json"


def get_docs_service():
    """Google Docs API に接続するためのサービスオブジェクトを返す"""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print(
                    f"エラー: {CREDENTIALS_FILE} が見つかりません。\n"
                    "Google Cloud Console から OAuth クライアントの JSON を"
                    "ダウンロードし、このフォルダに credentials.json として保存してください。"
                )
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("docs", "v1", credentials=creds)


def create_document_with_text(title: str, text: str) -> dict:
    """
    新規ドキュメントを作成し、テキストを挿入する

    Args:
        title: ドキュメントのタイトル
        text: 本文に挿入する文字列

    Returns:
        作成したドキュメントの情報（documentId, title など）
    """
    service = get_docs_service()

    # ステップ1: 空のドキュメントを作成し、documentId を取得
    doc = service.documents().create(body={"title": title}).execute()
    document_id = doc["documentId"]

    # ステップ2: batchUpdate でテキストを挿入
    # index 1 = ドキュメント先頭（0 は API 上の予約位置）
    requests = [
        {
            "insertText": {
                "location": {"index": 1},
                "text": text,
            }
        }
    ]
    service.documents().batchUpdate(
        documentId=document_id,
        body={"requests": requests},
    ).execute()

    return {
        "documentId": document_id,
        "title": doc.get("title", title),
        "url": f"https://docs.google.com/document/d/{document_id}/edit",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Google Docs に新規ドキュメントを作成し、テキストを挿入"
    )
    parser.add_argument("text", help="ドキュメントに挿入するテキスト")
    parser.add_argument(
        "--title",
        default="API で作成したドキュメント",
        help="ドキュメントのタイトル（省略時: API で作成したドキュメント）",
    )
    args = parser.parse_args()

    try:
        info = create_document_with_text(args.title, args.text)
        print("ドキュメントを作成しました!")
        print(f"  タイトル: {info['title']}")
        print(f"  ドキュメント ID: {info['documentId']}")
        print(f"  開く URL: {info['url']}")
    except HttpError as e:
        if e.resp.status == 403 and "docs.googleapis.com" in str(e):
            print(
                "エラー: Google Docs API が有効になっていません。\n"
                "Google Cloud Console で次の手順を行ってください:\n"
                "  1. API とサービス → ライブラリ\n"
                "  2. 「Google Docs API」を検索\n"
                "  3. 「有効にする」をクリック\n"
                "  4. 1〜2分待ってから、もう一度このコマンドを実行\n"
                "\n"
                "直接開く URL:\n"
                "  https://console.cloud.google.com/apis/library/docs.googleapis.com"
            )
        else:
            print(f"作成に失敗しました: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"作成に失敗しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
