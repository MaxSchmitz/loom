#!/bin/bash
# Send an iMessage to Max and wait for his reply.
# Usage: loom-msg.sh "your message here" [timeout_seconds]
# Returns: Max's reply text on stdout. Exit 0 = got reply, exit 1 = timeout/error.
#
# Uses history polling instead of watch. Polls both chat 546 (email)
# and 605 (phone) since replies can land in either.

set -euo pipefail

SEND_TO="max.schmitz@gmail.com"
TIMEOUT="${2:-300}"  # default 5 min

TEXT="${1:?Usage: loom-msg.sh \"message\" [timeout_seconds]}"

# Get current max rowid across both chats
id1=$(imsg history --chat-id 546 --limit 1 --json 2>/dev/null | jq -r '.id // 0')
id2=$(imsg history --chat-id 605 --limit 1 --json 2>/dev/null | jq -r '.id // 0')
BEFORE_ID=$(( id1 > id2 ? id1 : id2 ))

# Send the message
imsg send --to "$SEND_TO" --text "$TEXT" >/dev/null 2>&1

# Poll history for a new message that isn't what we sent
ELAPSED=0
while [ $ELAPSED -lt "$TIMEOUT" ]; do
  sleep 5
  ELAPSED=$((ELAPSED + 5))

  for CHAT in 546 605; do
    REPLY=$(imsg history --chat-id "$CHAT" --limit 5 --json 2>/dev/null \
      | jq -r --argjson before "$BEFORE_ID" --arg sent "$TEXT" \
        'select(.id > $before and .text != $sent and .text != null and .text != "") | .text' \
        2>/dev/null \
      | head -1)

    if [ -n "$REPLY" ]; then
      echo "$REPLY"
      exit 0
    fi
  done
done

echo "TIMEOUT" >&2
exit 1
