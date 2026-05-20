#!/bin/bash
# 他の方に渡す用 ZIP を作成（秘密情報・仮想環境は含めない）
set -e
cd "$(dirname "$0")"
OUT="../drive-upload-tool.zip"

zip -r "$OUT" \
  upload_to_drive.py \
  requirements.txt \
  README.md \
  SETUP_FOR_TEAM.md \
  sample.txt \
  .gitignore \
  -x "*.DS_Store"

echo "作成しました: $OUT"
echo "※ credentials.json / token.json / .venv は含まれていません"
