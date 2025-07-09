#!/bin/bash

# Script to update database URLs in environment files

# Function to update environment variables
update_env_file() {
  local file="$1"
  local db_url="$2"
  local prisma_db_url="$3"
  local postgres_url="$4"

  if [ -f "$file" ]; then
    # Create a backup of the original file
    cp "$file" "${file}.bak"
    
    # Update DATABASE_URL if it exists, otherwise append it
    if grep -q "^DATABASE_URL=" "$file"; then
      sed -i '' "s|^DATABASE_URL=.*|DATABASE_URL=\"$db_url\"|" "$file"
    else
      echo "DATABASE_URL=\"$db_url\"" >> "$file"
    fi
    
    # Update PRISMA_DATABASE_URL if it exists, otherwise append it
    if grep -q "^PRISMA_DATABASE_URL=" "$file"; then
      sed -i '' "s|^PRISMA_DATABASE_URL=.*|PRISMA_DATABASE_URL=\"$prisma_db_url\"|" "$file"
    else
      echo "PRISMA_DATABASE_URL=\"$prisma_db_url\"" >> "$file"
    fi
    
    # Update POSTGRES_URL if it exists, otherwise append it
    if grep -q "^POSTGRES_URL=" "$file"; then
      sed -i '' "s|^POSTGRES_URL=.*|POSTGRES_URL=\"$postgres_url\"|" "$file"
    else
      echo "POSTGRES_URL=\"$postgres_url\"" >> "$file"
    fi
    
    echo "Updated $file"
  else
    echo "File $file does not exist"
  fi
}

# The database URLs from your input
DB_URL="postgres://21b02784a718c1f4c615bfa9d4f7c52dad63e24f1f889f99cc486c43ba217e42:sk_HAvgGZqr4UYuJUqa9M-h7@db.prisma.io:5432/?sslmode=require"
PRISMA_DB_URL="prisma+postgres://accelerate.prisma-data.net/?api_key=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGlfa2V5IjoiMDFKWlFHVlNLWDc3RFZKMFlLWVlUMTc4S1MiLCJ0ZW5hbnRfaWQiOiIyMWIwMjc4NGE3MThjMWY0YzYxNWJmYTlkNGY3YzUyZGFkNjNlMjRmMWY4ODlmOTljYzQ4NmM0M2JhMjE3ZTQyIiwiaW50ZXJuYWxfc2VjcmV0IjoiNmY0OWQxNjMtZTJjNi00ZTFhLWI0OGItNjdhM2YxN2Q4Mzk1In0.Clt6JfDH0Tundbd43JDZm5DHOGKm-5IrgHIXlSX1EQg"
POSTGRES_URL="postgres://21b02784a718c1f4c615bfa9d4f7c52dad63e24f1f889f99cc486c43ba217e42:sk_HAvgGZqr4UYuJUqa9M-h7@db.prisma.io:5432/?sslmode=require"

# Update .env and .env.local files
update_env_file "/Users/managobindasethi/portal-ai-music/.env" "$DB_URL" "$PRISMA_DB_URL" "$POSTGRES_URL"
update_env_file "/Users/managobindasethi/portal-ai-music/.env.local" "$DB_URL" "$PRISMA_DB_URL" "$POSTGRES_URL"

echo "Database URLs have been updated in environment files."
