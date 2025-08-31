import { defineConfig } from "vite";

export default defineConfig({
  base: "./", //Use relative paths so it works at any mount path
  plugins: [],
  publicDir: "public",
  server: {
    host: "localhost",
    port: "3000",
    allowedHosts: true, // Allows external connections like ngrok
    proxy: {
      // Proxy /api requests to the backend server
      "/api": {
        target: "http://0.0.0.0:7860", // Replace with your backend URL
        changeOrigin: true,
      },
    },
  },
});
