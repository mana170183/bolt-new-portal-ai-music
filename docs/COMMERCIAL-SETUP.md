# Commercial Setup Guide

This guide covers setting up Portal AI Music for commercial production use with enterprise-grade security, scalability, and legal compliance.

## 🏢 Commercial Requirements

### Legal Compliance
- **Data Sources**: Only CC0 and public domain music datasets
- **Generated Music**: 100% royalty-free with perpetual license
- **Terms of Service**: Clear licensing for commercial use
- **Privacy Policy**: GDPR and CCPA compliant

### Security Requirements
- **Authentication**: JWT-based with Azure AD B2C integration
- **API Security**: Rate limiting, CORS, HTTPS only
- **Data Protection**: Encrypted storage, secure file access
- **Monitoring**: Application Insights, security alerts

### Scalability Requirements
- **Auto-scaling**: Azure App Service with load balancing
- **CDN**: Azure CDN for global content delivery
- **Caching**: Redis for session management and rate limiting
- **Database**: Azure Cosmos DB for user data and analytics

## 🔐 Security Setup

### 1. Azure Key Vault Configuration

```bash
# Create Key Vault
az keyvault create \
  --name portal-ai-music-vault \
  --resource-group portal-ai-music-rg \
  --location "East US"

# Store secrets
az keyvault secret set \
  --vault-name portal-ai-music-vault \
  --name "jwt-secret-key" \
  --value "$(openssl rand -hex 32)"

az keyvault secret set \
  --vault-name portal-ai-music-vault \
  --name "azure-storage-connection" \
  --value "your_storage_connection_string"
```

### 2. Azure AD B2C Setup

```bash
# Create Azure AD B2C tenant
az ad b2c tenant create \
  --country-code US \
  --display-name "Portal AI Music" \
  --domain-name portalaimusic

# Configure user flows for sign-up/sign-in
# This is done through Azure Portal
```

### 3. API Management Configuration

```bash
# Create API Management instance
az apim create \
  --name portal-ai-music-apim \
  --resource-group portal-ai-music-rg \
  --publisher-name "Portal AI Music" \
  --publisher-email "admin@portalaimusic.com" \
  --sku-name Developer
```

## 💳 Payment Integration

### Stripe Setup

1. **Create Stripe Account**
   - Sign up at https://stripe.com
   - Complete business verification
   - Get API keys from Dashboard

2. **Configure Webhooks**
   ```javascript
   // webhook endpoint: /api/stripe/webhook
   const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
   
   app.post('/api/stripe/webhook', express.raw({type: 'application/json'}), (req, res) => {
     const sig = req.headers['stripe-signature'];
     let event;
   
     try {
       event = stripe.webhooks.constructEvent(req.body, sig, process.env.STRIPE_WEBHOOK_SECRET);
     } catch (err) {
       return res.status(400).send(`Webhook signature verification failed.`);
     }
   
     // Handle the event
     switch (event.type) {
       case 'payment_intent.succeeded':
         // Upgrade user plan
         break;
       case 'customer.subscription.deleted':
         // Downgrade user plan
         break;
     }
   
     res.json({received: true});
   });
   ```

3. **Subscription Plans**
   ```javascript
   const plans = {
     free: {
       price: 0,
       daily_limit: 5,
       max_duration: 30,
       features: ['Basic genres', 'MP3 download']
     },
     creator: {
       price: 1900, // $19.00
       daily_limit: 100,
       max_duration: 180,
       features: ['All genres', 'WAV + MP3', 'Priority generation']
     },
     professional: {
       price: 4900, // $49.00
       daily_limit: -1, // unlimited
       max_duration: 600,
       features: ['Unlimited', 'All formats', 'API access', 'Custom training']
     }
   };
   ```

## 📊 Analytics and Monitoring

### Application Insights Setup

```bash
# Create Application Insights
az monitor app-insights component create \
  --app portal-ai-music-insights \
  --location "East US" \
  --resource-group portal-ai-music-rg \
  --application-type web
```

### Custom Metrics

```python
from applicationinsights import TelemetryClient

tc = TelemetryClient(os.getenv('APPINSIGHTS_INSTRUMENTATIONKEY'))

# Track music generation
tc.track_event('music_generated', {
    'user_id': user_id,
    'genre': genre,
    'mood': mood,
    'duration': duration,
    'generation_time': generation_time
})

# Track API usage
tc.track_metric('api_requests_per_minute', requests_count)
tc.track_metric('generation_success_rate', success_rate)
```

## 🚀 Performance Optimization

### 1. Redis Caching

```python
import redis
import json

redis_client = redis.from_url(os.getenv('REDIS_URL'))

# Cache user quotas
def get_user_quota(user_id):
    cached = redis_client.get(f"quota:{user_id}")
    if cached:
        return json.loads(cached)
    
    # Fetch from database
    quota = fetch_quota_from_db(user_id)
    redis_client.setex(f"quota:{user_id}", 3600, json.dumps(quota))
    return quota

# Rate limiting with Redis
def check_rate_limit(user_id, limit=10, window=3600):
    key = f"rate_limit:{user_id}"
    current = redis_client.get(key)
    
    if current is None:
        redis_client.setex(key, window, 1)
        return True
    
    if int(current) >= limit:
        return False
    
    redis_client.incr(key)
    return True
```

### 2. CDN Configuration

```bash
# Create CDN profile
az cdn profile create \
  --name portal-ai-music-cdn \
  --resource-group portal-ai-music-rg \
  --sku Standard_Microsoft

# Create CDN endpoint for static assets
az cdn endpoint create \
  --name portal-ai-music-static \
  --profile-name portal-ai-music-cdn \
  --resource-group portal-ai-music-rg \
  --origin portal-ai-music.azurestaticapps.net

# Create CDN endpoint for audio files
az cdn endpoint create \
  --name portal-ai-music-audio \
  --profile-name portal-ai-music-cdn \
  --resource-group portal-ai-music-rg \
  --origin portalaimusicstore.blob.core.windows.net
```

## 🔄 CI/CD Pipeline

### GitHub Actions Secrets

Required secrets for production deployment:

```bash
# Azure credentials
AZURE_CREDENTIALS
AZURE_STATIC_WEB_APPS_API_TOKEN
AZURE_APP_SERVICE_PUBLISH_PROFILE

# Application settings
VITE_API_URL
AZURE_STORAGE_CONNECTION_STRING
JWT_SECRET_KEY
STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET
APPINSIGHTS_INSTRUMENTATIONKEY

# Resource names
AZURE_RESOURCE_GROUP
AZURE_APP_SERVICE_NAME
AZURE_STATIC_WEB_APP_NAME
AZURE_STORAGE_ACCOUNT
```

### Environment Configuration

```yaml
# azure-pipelines.yml
variables:
  - group: portal-ai-music-prod
  - name: vmImageName
    value: 'ubuntu-latest'

stages:
- stage: Build
  jobs:
  - job: BuildFrontend
    steps:
    - task: NodeTool@0
      inputs:
        versionSpec: '18.x'
    - script: |
        npm ci
        npm run build
      env:
        VITE_API_URL: $(VITE_API_URL)

- stage: Deploy
  dependsOn: Build
  jobs:
  - deployment: DeployToProduction
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureWebApp@1
            inputs:
              azureSubscription: 'Azure-Production'
              appType: 'webAppLinux'
              appName: '$(AZURE_APP_SERVICE_NAME)'
```

## 📋 Production Checklist

### Pre-Launch
- [ ] Legal review of terms of service and privacy policy
- [ ] Security audit and penetration testing
- [ ] Load testing with expected traffic
- [ ] Backup and disaster recovery plan
- [ ] Monitoring and alerting setup
- [ ] SSL certificates configured
- [ ] Domain and DNS configuration
- [ ] Payment processing tested
- [ ] User authentication flow tested
- [ ] API rate limiting verified

### Post-Launch
- [ ] Monitor application performance
- [ ] Track user engagement metrics
- [ ] Monitor costs and optimize resources
- [ ] Regular security updates
- [ ] Customer support system
- [ ] Marketing and user acquisition
- [ ] Feature usage analytics
- [ ] A/B testing framework

## 💰 Cost Optimization

### Azure Cost Management

```bash
# Set up budget alerts
az consumption budget create \
  --budget-name portal-ai-music-budget \
  --amount 1000 \
  --time-grain Monthly \
  --start-date 2024-01-01 \
  --end-date 2024-12-31

# Monitor costs by resource group
az consumption usage list \
  --start-date 2024-01-01 \
  --end-date 2024-01-31 \
  --include-additional-properties \
  --include-meter-details
```

### Resource Optimization

1. **App Service**: Use B1 for development, P1V3 for production
2. **Storage**: Use Cool tier for long-term audio storage
3. **CDN**: Configure appropriate caching rules
4. **Database**: Use serverless Cosmos DB for variable workloads

## 🎯 Success Metrics

### Key Performance Indicators (KPIs)

1. **Technical Metrics**
   - API response time < 2 seconds
   - Music generation time < 30 seconds
   - Uptime > 99.9%
   - Error rate < 0.1%

2. **Business Metrics**
   - Monthly Active Users (MAU)
   - Conversion rate (free to paid)
   - Customer Lifetime Value (CLV)
   - Churn rate

3. **User Experience Metrics**
   - Time to first generation
   - User satisfaction score
   - Feature adoption rate
   - Support ticket volume

### Monitoring Dashboard

```javascript
// Custom dashboard metrics
const metrics = {
  daily_active_users: await getDailyActiveUsers(),
  music_generations_today: await getTodayGenerations(),
  revenue_this_month: await getMonthlyRevenue(),
  average_generation_time: await getAverageGenerationTime(),
  error_rate: await getErrorRate(),
  storage_usage: await getStorageUsage()
};
```

## 📞 Support and Maintenance

### Customer Support
- **Help Center**: Comprehensive documentation
- **Live Chat**: Business hours support
- **Email Support**: 24-hour response time
- **Community Forum**: User-to-user support

### Maintenance Schedule
- **Daily**: Monitor system health and performance
- **Weekly**: Review usage analytics and costs
- **Monthly**: Security updates and patches
- **Quarterly**: Performance optimization review

For additional support with commercial setup, contact our enterprise team at enterprise@portalaimusic.com