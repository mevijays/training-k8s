#!/bin/bash
set -e
# Change to the GitHub workspace directory
cd "$GITHUB_WORKSPACE"
# Find all SQL files recursively in the workspace
sql_files=$(find . -type f -name "*.sql")

error_found=false

for file in $sql_files; do
  if grep -Eiq '^\s*(DELETE|UPDATE)' "$file"; then
    if ! grep -Eiq 'WHERE.*TENANT_ID' "$file"; then
      echo "Error: $file contains DELETE or UPDATE statement without WHERE TENANT_ID clause."
      error_found=true
    fi
  fi
done

if $error_found; then
  exit 1
fi
