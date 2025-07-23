#!/bin/bash

echo "🗄️ Portal AI Music - Database Schema Setup"

# Configuration
RESOURCE_GROUP="rg-portal-ai-music-dev"
SQL_SERVER="sql-portal-ai-music-dev"
SQL_DATABASE="portal-ai-music-db"

# Check if create_schema.sql exists
if [ ! -f "create_schema.sql" ]; then
    echo "❌ create_schema.sql not found. Please run setup-azure-integration.sh first"
    exit 1
fi

echo "📊 Database Schema Setup Options:"
echo "1. Using Azure CLI with SQL authentication"
echo "2. Using sqlcmd (if installed locally)"
echo "3. Manual SQL Script (copy-paste to Azure Portal)"

read -p "Choose option (1-3): " option

case $option in
    1)
        echo "🔐 Setting up SQL authentication..."
        echo "Note: You'll need SQL Server admin credentials"
        
        read -p "SQL Server admin username: " SQL_ADMIN
        read -s -p "SQL Server admin password: " SQL_PASSWORD
        echo
        
        # Create the schema using Azure CLI
        az sql db query \
            --server $SQL_SERVER \
            --database $SQL_DATABASE \
            --admin-user $SQL_ADMIN \
            --admin-password $SQL_PASSWORD \
            --file create_schema.sql
        
        if [ $? -eq 0 ]; then
            echo "✅ Database schema created successfully!"
        else
            echo "❌ Schema creation failed. Check credentials and permissions."
        fi
        ;;
        
    2)
        echo "💻 Using sqlcmd..."
        
        read -p "SQL Server admin username: " SQL_ADMIN
        read -s -p "SQL Server admin password: " SQL_PASSWORD
        echo
        
        sqlcmd -S $SQL_SERVER.database.windows.net \
               -d $SQL_DATABASE \
               -U $SQL_ADMIN \
               -P $SQL_PASSWORD \
               -i create_schema.sql \
               -e
        
        if [ $? -eq 0 ]; then
            echo "✅ Database schema created successfully!"
        else
            echo "❌ Schema creation failed. Install sqlcmd or use Azure Portal."
        fi
        ;;
        
    3)
        echo "📋 Manual SQL Script Setup:"
        echo "1. Go to Azure Portal → SQL databases → $SQL_DATABASE"
        echo "2. Click 'Query editor' or 'Query editor (preview)'"
        echo "3. Login with your SQL credentials"
        echo "4. Copy and paste the following SQL script:"
        echo "=========================================="
        cat create_schema.sql
        echo "=========================================="
        echo "5. Click 'Run' to execute the script"
        echo ""
        echo "📍 Direct link: https://portal.azure.com/#@/resource/subscriptions/{subscription-id}/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Sql/servers/$SQL_SERVER/databases/$SQL_DATABASE/queryEditor"
        ;;
        
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

# Test the database connection
echo ""
echo "🧪 Testing database schema..."

# Create a simple test script
cat > test_database.sql << 'EOF'
-- Test database schema
SELECT 'Tables created successfully!' AS Status;

-- Check if tables exist
SELECT 
    TABLE_NAME,
    CASE 
        WHEN TABLE_NAME IN ('music_catalog', 'generated_music', 'user_sessions', 'training_data', 'music_templates') 
        THEN 'Required table exists' 
        ELSE 'Additional table' 
    END AS TableStatus
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;

-- Check sample data
SELECT COUNT(*) AS SampleDataCount FROM music_catalog;
SELECT COUNT(*) AS TemplateCount FROM music_templates;
EOF

echo "📋 To test your database schema, run this SQL in Azure Portal Query Editor:"
echo "=========================================="
cat test_database.sql
echo "=========================================="

# Cleanup
rm -f test_database.sql

echo ""
echo "✅ Database setup instructions provided!"
echo "🔗 Next step: Run deploy-azure-backend.sh to deploy the integrated backend"
