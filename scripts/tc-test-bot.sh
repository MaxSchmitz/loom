#!/bin/bash
# Simple test bot: replies "test" to any message received.
set -euo pipefail

WATCH_CHAT_ID="${TC_CHAT_ID:?Set TC_CHAT_ID}"
REPLY_TO="${TC_REPLY_TO:?Set TC_REPLY_TO (email or phone)}"

echo "Watching chat $WATCH_CHAT_ID, replying to $REPLY_TO..."

imsg watch --chat-id "$WATCH_CHAT_ID" --json | while IFS= read -r msg; do
  TEXT=$(echo "$msg" | jq -r '.text // empty')
  IS_FROM_ME=$(echo "$msg" | jq -r '.is_from_me // false')

  if [ "$IS_FROM_ME" = "true" ] || [ -z "$TEXT" ]; then
    continue
  fi

  echo "Got message: $TEXT"
  imsg send --to "$REPLY_TO" --text "test"
  echo "Sent reply: test"
done
