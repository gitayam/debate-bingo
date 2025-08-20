/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  typedRoutes: true,
  async rewrites() {
    // In Docker, backend is accessible via service name
    const backendUrl = process.env.BACKEND_URL || 'http://backend:8000';
    
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;