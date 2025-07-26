// NUCLEAR DEPLOYMENT FORCE FILE v2.0.0
// Build timestamp: 2024-12-08T${Date.now()}
// This file exists solely to force Azure Static Web Apps to rebuild
// and deploy the latest changes instead of serving cached content

export const DEPLOYMENT_CONFIG = {
  version: '2.0.0',
  buildTime: new Date().toISOString(),
  forceRedeploy: true,
  apiOverride: '/api',
  description: 'Nuclear deployment to fix persistent caching issues'
};

console.log('🚀 NUCLEAR DEPLOYMENT CONFIG:', DEPLOYMENT_CONFIG);
