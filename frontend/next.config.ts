import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow all hosts for Replit proxy
  serverExternalPackages: [],
  // Enable static export for production
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
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
};

export default nextConfig;
