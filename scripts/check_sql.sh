#!/bin/bash
set -e

echo "Starting SQL files validation..."

# Change to the GitHub workspace directory
cd "$GITHUB_WORKSPACE"

# Find all SQL files recursively in the workspace
sql_files=$(find . -type f -name "*.sql")

if [ -z "$sql_files" ]; then
    echo "No SQL files found to check."
    exit 0
fi

error_found=false

for file in $sql_files; do
    echo "Checking file: $file"
    
    # Read file and preserve newlines in statements
    while IFS= read -r -d ';' statement || [ -n "$statement" ]; do
        # Skip empty or comment-only statements
        if [[ -z "${statement// }" ]] || [[ "$statement" =~ ^[[:space:]]*-- ]]; then
            continue
        fi
        
        # Normalize statement to single line for checking
        normalized_stmt=$(echo "$statement" | tr '\n' ' ' | sed 's/[[:space:]]\+/ /g' | sed 's/^ *//;s/ *$//')
        
        if echo "$normalized_stmt" | grep -Eiq '^[[:space:]]*(DELETE|UPDATE)'; then
            echo "Checking statement: $normalized_stmt"
            if ! echo "$normalized_stmt" | grep -Eiq 'WHERE.*TENANT_ID'; then
                echo "❌ Error in $file:"
                echo "   Statement missing WHERE TENANT_ID clause:"
                echo "$statement;"
                error_found=true
            else
                echo "✅ Valid statement with WHERE TENANT_ID clause"
            fi
        fi
    done < "$file"
done

if $error_found; then
    echo "❌ Validation failed: Found statements without TENANT_ID filter"
    exit 1
else
    echo "✅ All SQL files passed validation"
fi
