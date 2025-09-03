# Deployment Guide: Render & Vercel

## Prerequisites

1. **GitHub Repository**: Push your code to GitHub
2. **MongoDB Atlas Account**: Set up a free cluster
3. **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)

## Method 1: Render Deployment

### Step 1: Set up MongoDB Atlas

1. **Create MongoDB Atlas Cluster**:

   - Go to [MongoDB Atlas](https://cloud.mongodb.com/)
   - Create a free cluster (M0 tier)
   - Choose your preferred cloud provider and region

2. **Create Database and Collection**:

   - Create a database named `rag_demo`
   - Create a collection named `documents`

3. **Set up Vector Search Index**:
   - Go to "Search" tab in your cluster
   - Click "Create Search Index"
   - Choose "JSON Editor" and paste this configuration:

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

4. **Get Connection String**:
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string

### Step 2: Deploy to Render

1. **Connect GitHub**:

   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select your repository

2. **Configure Service**:

   - **Name**: `rag-app` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

3. **Set Environment Variables**:
   Click "Environment" tab and add these variables:

```bash
# Required - Set these in Render Dashboard
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/

# Optional - These have defaults in render.yaml
VECTORSTORE=ATLAS
EMBEDDINGS=OPENAI
LLM_PROVIDER=OPENAI
OPENAI_MODEL=gpt-4o-mini
HF_EMBEDDINGS_MODEL=text-embedding-3-small
MONGODB_DB=rag_demo
MONGODB_COLLECTION=documents
MONGODB_ATLAS_INDEX_NAME=vector_index
```

4. **Deploy**:
   - Click "Create Web Service"
   - Render will automatically build and deploy your app
   - Wait for the build to complete (usually 2-5 minutes)

### Step 3: Test Your App

1. **Access your app**: `https://your-app-name.onrender.com`
2. **Upload a PDF/TXT file**
3. **Click "Ingest"**
4. **Ask questions about your document**

---

## Method 2: Vercel Deployment

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Set up MongoDB Atlas (Same as Render)

Follow the MongoDB Atlas setup from Method 1.

### Step 3: Deploy to Vercel

1. **Login to Vercel**:

```bash
vercel login
```

2. **Deploy**:

```bash
vercel
```

3. **Set Environment Variables**:
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Select your project
   - Go to "Settings" → "Environment Variables"
   - Add these variables:

```bash
# Required
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/

# Optional (these have defaults in vercel.json)
VECTORSTORE=ATLAS
EMBEDDINGS=OPENAI
LLM_PROVIDER=OPENAI
OPENAI_MODEL=gpt-4o-mini
HF_EMBEDDINGS_MODEL=text-embedding-3-small
MONGODB_DB=rag_demo
MONGODB_COLLECTION=documents
MONGODB_ATLAS_INDEX_NAME=vector_index
```

4. **Redeploy with Environment Variables**:

```bash
vercel --prod
```

---

## Environment Variables Explained

### Required Variables

| Variable         | Description                     | Example                                        |
| ---------------- | ------------------------------- | ---------------------------------------------- |
| `OPENAI_API_KEY` | Your OpenAI API key             | `sk-1234567890abcdef...`                       |
| `MONGODB_URI`    | MongoDB Atlas connection string | `mongodb+srv://user:pass@cluster.mongodb.net/` |

### Optional Variables (with defaults)

| Variable                   | Default        | Description                                  |
| -------------------------- | -------------- | -------------------------------------------- |
| `VECTORSTORE`              | `ATLAS`        | Use `ATLAS` for MongoDB or `FAISS` for local |
| `EMBEDDINGS`               | `OPENAI`       | Use `OPENAI` or `HF` (HuggingFace)           |
| `LLM_PROVIDER`             | `OPENAI`       | Use `OPENAI` or `OLLAMA`                     |
| `OPENAI_MODEL`             | `gpt-4o-mini`  | OpenAI model to use                          |
| `MONGODB_DB`               | `rag_demo`     | Database name                                |
| `MONGODB_COLLECTION`       | `documents`    | Collection name                              |
| `MONGODB_ATLAS_INDEX_NAME` | `vector_index` | Vector search index name                     |

---

## Where to Set Environment Variables

### Render Dashboard

1. Go to your service
2. Click "Environment" tab
3. Click "Add Environment Variable"
4. Enter key and value
5. Click "Save Changes"

### Vercel Dashboard

1. Go to your project
2. Click "Settings"
3. Click "Environment Variables"
4. Click "Add New"
5. Enter key and value
6. Select environment (Production/Preview/Development)
7. Click "Add"

---

## Troubleshooting

### Common Issues

1. **"MongoDB connection failed"**:

   - Check your `MONGODB_URI`
   - Ensure your IP is whitelisted in Atlas
   - Verify username/password

2. **"OpenAI API key invalid"**:

   - Check your `OPENAI_API_KEY`
   - Ensure it starts with `sk-`
   - Verify you have credits in your OpenAI account

3. **"Vector search index not found"**:

   - Create the vector search index in MongoDB Atlas
   - Use the JSON configuration provided above

4. **"Build failed"**:
   - Check the build logs in Render/Vercel
   - Ensure all dependencies are in `requirements.txt`

### Debug Commands

```bash
# Check environment variables
echo $OPENAI_API_KEY
echo $MONGODB_URI

# Test MongoDB connection
python -c "
from pymongo import MongoClient
client = MongoClient('$MONGODB_URI')
print('Connected:', client.admin.command('ping'))
"
```

---

## Cost Considerations

### Render

- **Free Tier**: 750 hours/month, 512MB RAM
- **Paid**: $7/month for 1GB RAM, unlimited hours

### Vercel

- **Free Tier**: 100GB bandwidth/month
- **Paid**: $20/month for unlimited bandwidth

### MongoDB Atlas

- **Free Tier**: 512MB storage, shared RAM
- **Paid**: $9/month for 2GB storage, dedicated RAM

### OpenAI

- **Cost**: Pay per token used
- **Estimate**: $0.01-0.10 per question (depending on model and response length)

---

## Security Best Practices

1. **Never commit API keys** to GitHub
2. **Use environment variables** for sensitive data
3. **Enable IP whitelisting** in MongoDB Atlas
4. **Monitor usage** and set up billing alerts
5. **Rotate API keys** regularly

---

## Next Steps

After successful deployment:

1. **Test with different file types** (PDF, TXT)
2. **Monitor performance** and costs
3. **Add authentication** if needed
4. **Scale up** resources as needed
5. **Set up monitoring** and alerts



