# MongoDB Atlas Setup Guide

## Step-by-Step MongoDB Atlas Configuration

### 1. Create MongoDB Atlas Account

1. Go to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Click "Try Free" or "Sign Up"
3. Fill in your details and create account

### 2. Create Cluster

1. Click "Build a Database"
2. Choose "FREE" tier (M0)
3. Select cloud provider (AWS, Google Cloud, or Azure)
4. Choose region (closest to your users)
5. Click "Create"

### 3. Set Up Database Access

1. Go to "Database Access" in left sidebar
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Create username and password (save these!)
5. Select "Read and write to any database"
6. Click "Add User"

### 4. Set Up Network Access

1. Go to "Network Access" in left sidebar
2. Click "Add IP Address"
3. For development: Click "Allow Access from Anywhere" (0.0.0.0/0)
4. For production: Add specific IP addresses
5. Click "Confirm"

### 5. Create Database and Collection

1. Go to "Browse Collections"
2. Click "Create Database"
3. Database name: `rag_demo`
4. Collection name: `documents`
5. Click "Create"

### 6. Create Vector Search Index

1. Go to "Search" tab in your cluster
2. Click "Create Search Index"
3. Choose "JSON Editor"
4. Paste this configuration:

```json
{
	"mappings": {
		"dynamic": true,
		"fields": {
			"embedding": {
				"dimensions": 1536,
				"similarity": "cosine",
				"type": "knnVector"
			}
		}
	}
}
```

5. Click "Create"

### 7. Get Connection String

1. Click "Connect" on your cluster
2. Choose "Connect your application"
3. Copy the connection string
4. Replace `<password>` with your actual password
5. Replace `<dbname>` with `rag_demo`

**Example connection string:**

```
mongodb+srv://username:yourpassword@cluster0.xxxxx.mongodb.net/rag_demo?retryWrites=true&w=majority
```

### 8. Test Connection

Use this Python script to test your connection:

```python
from pymongo import MongoClient

# Replace with your connection string
uri = "mongodb+srv://username:password@cluster.mongodb.net/rag_demo"

try:
    client = MongoClient(uri)
    # Test connection
    client.admin.command('ping')
    print("✅ Connected to MongoDB Atlas!")

    # Test database access
    db = client.rag_demo
    collection = db.documents
    print("✅ Database and collection accessible!")

except Exception as e:
    print(f"❌ Connection failed: {e}")
```

## Environment Variable Setup

### For Render:

1. Go to your service in Render Dashboard
2. Click "Environment" tab
3. Add these variables:

```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/rag_demo
MONGODB_DB=rag_demo
MONGODB_COLLECTION=documents
MONGODB_ATLAS_INDEX_NAME=vector_index
```

### For Vercel:

1. Go to your project in Vercel Dashboard
2. Click "Settings" → "Environment Variables"
3. Add the same variables as above

## Common Issues & Solutions

### Issue: "Authentication failed"

- **Solution**: Check username/password in connection string
- **Solution**: Ensure user has correct permissions

### Issue: "Network access denied"

- **Solution**: Add your IP to Network Access
- **Solution**: Use "Allow Access from Anywhere" for testing

### Issue: "Vector search index not found"

- **Solution**: Create the vector search index as shown above
- **Solution**: Wait for index to finish building (can take a few minutes)

### Issue: "Connection timeout"

- **Solution**: Check your internet connection
- **Solution**: Verify the connection string format
- **Solution**: Ensure cluster is running

## Security Best Practices

1. **Use strong passwords** for database users
2. **Limit network access** to specific IPs in production
3. **Regularly rotate** database passwords
4. **Monitor access logs** for suspicious activity
5. **Use VPC peering** for production deployments

## Cost Optimization

1. **Free tier**: 512MB storage, shared RAM
2. **Monitor usage** to avoid unexpected charges
3. **Set up billing alerts** for spending limits
4. **Use M0 tier** for development and testing
5. **Scale up gradually** as needed



