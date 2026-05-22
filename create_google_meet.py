"""
Google Meet API でオンラインミーティング（ミーティングスペース）を作成し、参加リンクを取得するスクリプト

使い方:
  # 新規ミーティングを作成し、参加リンクを表示
  python create_google_meet.py

  # アクセス種別を指定して作成（OPEN / TRUSTED / RESTRICTED）
  python create_google_meet.py --access-type OPEN

  # 既存ミーティングの参加リンクを取得（ミーティングコードまたはスペース ID）
  python create_google_meet.py --get abc-mnop-xyz
  python create_google_meet.py --get jQCFfuBOdN5z
"""

import argparse
import os
import sys
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ミーティングスペースの作成・参照
SCOPES = [
    "https://www.googleapis.com/auth/meetings.space.created",
    "https://www.googleapis.com/auth/meetings.space.readonly",
]

TOKEN_FILE = "token_meet.json"
CREDENTIALS_FILE = "credentials.json"


def get_meet_service():
    """Google Meet API に接続するためのサービスオブジェクトを返す"""
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

    return build("meet", "v2", credentials=creds)


def _space_name(identifier: str) -> str:
    """ミーティングコードまたはスペース ID から API 用の name を組み立てる"""
    if identifier.startswith("spaces/"):
        return identifier
    return f"spaces/{identifier}"


def format_space_info(space: dict) -> dict:
    """API レスポンスから表示用の情報を抽出する"""
    return {
        "name": space.get("name", ""),
        "meetingCode": space.get("meetingCode", ""),
        "meetingUri": space.get("meetingUri", ""),
        "activeConference": (space.get("activeConference") or {}).get("conferenceRecord"),
    }


def create_meeting_space(access_type: Optional[str] = None) -> dict:
    """
    新しいミーティングスペースを作成し、参加リンクを返す

    Args:
        access_type: OPEN / TRUSTED / RESTRICTED（省略時はアカウントのデフォルト）

    Returns:
        ミーティング情報（meetingUri, meetingCode など）
    """
    service = get_meet_service()
    body: dict = {}
    if access_type:
        body["config"] = {"accessType": access_type}

    space = service.spaces().create(body=body).execute()
    return format_space_info(space)


def get_meeting_space(identifier: str) -> dict:
    """
    既存のミーティングスペース情報と参加リンクを取得する

    Args:
        identifier: ミーティングコード（例: abc-mnop-xyz）またはスペース ID

    Returns:
        ミーティング情報（meetingUri, meetingCode など）
    """
    service = get_meet_service()
    space = service.spaces().get(name=_space_name(identifier)).execute()
    return format_space_info(space)


def print_meeting_info(info: dict, *, created: bool) -> None:
    """ミーティング情報を標準出力に表示する"""
    action = "作成" if created else "取得"
    print(f"ミーティングを{action}しました!")
    print(f"  参加リンク: {info['meetingUri']}")
    print(f"  ミーティングコード: {info['meetingCode']}")
    print(f"  スペース ID: {info['name']}")
    if info.get("activeConference"):
        print(f"  進行中の会議: {info['activeConference']}")
    else:
        print("  進行中の会議: なし")


def main():
    parser = argparse.ArgumentParser(
        description="Google Meet API でミーティングを作成、または参加リンクを取得"
    )
    parser.add_argument(
        "--get",
        metavar="CODE_OR_ID",
        help="既存ミーティングの参加リンクを取得（ミーティングコードまたはスペース ID）",
    )
    parser.add_argument(
        "--access-type",
        choices=["OPEN", "TRUSTED", "RESTRICTED"],
        default=None,
        help="作成時のアクセス種別（OPEN=誰でも参加可, TRUSTED=組織内, RESTRICTED=招待のみ）",
    )
    args = parser.parse_args()

    try:
        if args.get:
            info = get_meeting_space(args.get)
            print_meeting_info(info, created=False)
        else:
            info = create_meeting_space(args.access_type)
            print_meeting_info(info, created=True)
    except HttpError as e:
        if e.resp.status == 403 and "meet.googleapis.com" in str(e):
            print(
                "エラー: Google Meet API が有効になっていません。\n"
                "Google Cloud Console で次の手順を行ってください:\n"
                "  1. API とサービス → ライブラリ\n"
                "  2. 「Google Meet API」を検索\n"
                "  3. 「有効にする」をクリック\n"
                "  4. 1〜2分待ってから、もう一度このコマンドを実行\n"
                "\n"
                "直接開く URL:\n"
                "  https://console.cloud.google.com/apis/library/meet.googleapis.com"
            )
        elif e.resp.status == 404:
            print(
                "エラー: 指定されたミーティングが見つかりません。\n"
                "  ミーティングコード（例: abc-mnop-xyz）またはスペース ID を確認してください。"
            )
        else:
            print(f"処理に失敗しました: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"処理に失敗しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
