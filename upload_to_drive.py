"""
ローカルファイルを Google ドライブにアップロードするスクリプト

使い方:
  python upload_to_drive.py ./sample.txt
  python upload_to_drive.py ./photo.jpg --folder-id フォルダID
"""

import argparse
import mimetypes
import os
import sys
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ファイルの作成・読み取り権限（アップロードに必要）
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# 初回認証後に保存されるトークン（2回目以降はブラウザ不要）
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"


def get_drive_service():
    """Google ドライブ API に接続するためのサービスオブジェクトを返す"""
    creds = None

    # 以前ログインした情報があれば読み込む
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # トークンがない、または期限切れの場合は再認証
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

    return build("drive", "v3", credentials=creds)


def upload_file(local_path: str, folder_id: Optional[str] = None) -> dict:
    """
    ローカルファイルを Google ドライブにアップロードする

    Args:
        local_path: アップロードするファイルのパス
        folder_id: 保存先フォルダの ID（省略時はマイドライブ直下）

    Returns:
        API が返すファイル情報（id, name, webViewLink など）
    """
    if not os.path.isfile(local_path):
        raise FileNotFoundError(f"ファイルが見つかりません: {local_path}")

    file_name = os.path.basename(local_path)
    mime_type, _ = mimetypes.guess_type(local_path)
    if mime_type is None:
        mime_type = "application/octet-stream"

    file_metadata = {"name": file_name}
    if folder_id:
        file_metadata["parents"] = [folder_id]

    media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
    service = get_drive_service()

    # files().create で新規ファイルとしてアップロード
    result = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id,name,webViewLink")
        .execute()
    )
    return result


def main():
    parser = argparse.ArgumentParser(description="ローカルファイルを Google ドライブにアップロード")
    parser.add_argument("file", help="アップロードするファイルのパス")
    parser.add_argument(
        "--folder-id",
        help="保存先フォルダの ID（Google ドライブの URL から取得可能）",
        default=None,
    )
    args = parser.parse_args()

    try:
        info = upload_file(args.file, args.folder_id)
        print("アップロード完了!")
        print(f"  ファイル名: {info.get('name')}")
        print(f"  ファイル ID: {info.get('id')}")
        if info.get("webViewLink"):
            print(f"  リンク: {info.get('webViewLink')}")
    except FileNotFoundError as e:
        print(f"エラー: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"アップロードに失敗しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
