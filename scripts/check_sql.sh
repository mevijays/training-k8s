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
    
    # Read entire file into variable
    while IFS= read -r line || [ -n "$line" ]; do
        # Skip liquibase comments and empty lines
        if [[ "$line" =~ ^--liquibase ]] || [[ "$line" =~ ^--changeset ]] || [[ "$line" =~ ^--comment ]] || [[ "$line" =~ ^--rollback ]] || [[ -z "${line// }" ]]; then
            continue
        fi
        
        # Convert to lowercase and remove inline comments
        line_lower=$(echo "$line" | tr '[:upper:]' '[:lower:]' | sed 's/--.*//g')
        
        # Store statement lines
        if [[ "$line_lower" =~ ^[[:space:]]*(update|delete)[[:space:]] ]]; then
            current_statement="$line_lower"
            is_dml=true
        elif [[ $is_dml == true && ! "$line_lower" =~ \; ]]; then
            current_statement="$current_statement $line_lower"
        elif [[ $is_dml == true && "$line_lower" =~ \; ]]; then
            current_statement="$current_statement $line_lower"
            # Check complete statement
            echo "Checking statement: $current_statement"
            if ! [[ "$current_statement" =~ where[[:space:]]+.*tenant_id ]]; then
                echo "❌ Error: Missing WHERE TENANT_ID clause in:"
                echo "$current_statement"
                error_found=true
            fi
            is_dml=false
        fi
    done < "$file"
done

if $error_found; then
    echo "❌ Validation failed"
    exit 1
else
    echo "✅ All statements validated successfully"
fi
