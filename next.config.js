/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverComponentsExternalPackages: ['@prisma/client'],
  },
  images: {
    domains: ['images.unsplash.com'],
    unoptimized: true,
  },
  // Support for audio files
  webpack: (config, { isServer }) => {
    config.module.rules.push({
      test: /\.(mp3|wav|ogg|m4a)$/,
      use: {
        loader: 'file-loader',
        options: {
          publicPath: '/_next/static/sounds/',
          outputPath: 'static/sounds/',
        },
      },
    });

    // Fix for Prisma in serverless environments
    if (isServer) {
      config.externals.push('_http_common');
    }

    return config;
  },
  // Environment variables
  env: {
    NEXTAUTH_URL: process.env.NEXTAUTH_URL,
    NEXTAUTH_SECRET: process.env.NEXTAUTH_SECRET,
  },
  trailingSlash: false,
  // Skip static optimization for API routes with database connections
  experimental: {
    serverComponentsExternalPackages: ['@prisma/client'],
    outputFileTracingIncludes: {
      '/api/**/*': ['./node_modules/@prisma/client/runtime/*'],
    },
  },
};

export default nextConfig;
