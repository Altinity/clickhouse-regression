#!/bin/bash
sudo chown -R $(whoami):$(whoami) $SUITE/

echo ""
echo "Artifacts will be uploaded to $SUITE_REPORT_INDEX_URL"
echo "Review new fails (brisk) at $SUITE_LOG_FILE_PREFIX_URL/brisk-new-fails.log.txt"
echo "Review new fails (nice) at $SUITE_LOG_FILE_PREFIX_URL/nice-new-fails.log.txt"
