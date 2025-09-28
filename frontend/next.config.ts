import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow all hosts for Replit proxy
  serverExternalPackages: [],
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'ALLOWALL',
          },
        ],
      },
    ];
  },
  // Proxy API requests to backend in production
  async rewrites() {
    if (process.env.NODE_ENV === 'production') {
      return [
        {
          source: '/api/:path*',
          destination: 'http://localhost:8000/:path*',
        },
      ];
    }
    return [];
  },
};

export default nextConfig;
