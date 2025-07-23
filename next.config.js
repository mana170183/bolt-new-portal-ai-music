/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverComponentsExternalPackages: ['@prisma/client'],
  },
  images: {
    domains: ['images.unsplash.com', 'blob.vercel-storage.com'],
  },
  output: 'standalone',
  // Support for audio files
  webpack: (config) => {
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
    return config;
  },
  // Environment variables
  env: {
    NEXTAUTH_URL: process.env.NEXTAUTH_URL,
    NEXTAUTH_SECRET: process.env.NEXTAUTH_SECRET,
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://portal-music-backend-new.ambitiousmeadow-4c2dba6f.uksouth.azurecontainerapps.io',
  },
  // API configuration
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'https://portal-music-backend-new.ambitiousmeadow-4c2dba6f.uksouth.azurecontainerapps.io'}/api/:path*`,
      },
      {
        source: '/api/legacy/:path*',
        destination: 'http://localhost:5000/api/:path*',
      },
    ];
  },
};

export default nextConfig;
