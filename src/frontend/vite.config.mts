import react from "@vitejs/plugin-react-swc";
import * as dotenv from "dotenv";
import path from "path";
import { defineConfig, loadEnv } from "vite";
import svgr from "vite-plugin-svgr";
import tsconfigPaths from "vite-tsconfig-paths";
import {
  API_ROUTES,
  BASENAME,
  PORT,
  PROXY_TARGET,
} from "./src/customization/config-constants";


export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  const envLangflowResult = dotenv.config({
    path: path.resolve(__dirname, "../../.env"),
  });

  const envLangflow = envLangflowResult.parsed || {};

  const apiRoutes = API_ROUTES || ["^/api/v1/", "^/api/v2/", "/health"];

  const target =
    env.VITE_PROXY_TARGET || PROXY_TARGET || "http://127.0.0.1:7860";

  const port = Number(env.VITE_PORT) || PORT || 3000;

  const proxyTargets = apiRoutes.reduce((proxyObj, route) => {
    proxyObj[route] = {
      target: target,
      changeOrigin: true,
      secure: false,
      ws: true,
      timeout: 120000, // 2 minutes timeout
      proxyTimeout: 120000, // 2 minutes proxy timeout
      configure: (proxy: any, _options: any) => {
        proxy.on('error', (err: any, _req: any, res: any) => {
          console.log('proxy error', err);
          // Handle connection errors gracefully
          if (err.code === 'ECONNREFUSED' || err.code === 'ETIMEDOUT') {
            console.log(`Backend connection failed. Please ensure the backend is running on ${target}`);
            if (res && !res.headersSent) {
              res.writeHead(503, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({
                error: 'Backend service unavailable',
                message: `Cannot connect to backend at ${target}. Please start the backend server.`,
                code: err.code
              }));
            }
          }
        });
        proxy.on('proxyReq', (_proxyReq: any, req: any, _res: any) => {
          console.log('Sending Request to the Target:', req.method, req.url);
        });
        proxy.on('proxyRes', (proxyRes: any, req: any, _res: any) => {
          console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
        });
      },
    };
    return proxyObj;
  }, {});

  return {
    base: BASENAME || "",
    build: {
      outDir: "build",
    },
    define: {
      "process.env.BACKEND_URL": JSON.stringify(
        envLangflow.BACKEND_URL ?? "http://127.0.0.1:7860",
      ),
      "process.env.ACCESS_TOKEN_EXPIRE_SECONDS": JSON.stringify(
        envLangflow.ACCESS_TOKEN_EXPIRE_SECONDS ?? 60,
      ),
      "process.env.CI": JSON.stringify(envLangflow.CI ?? false),
      "process.env.LANGFLOW_AUTO_LOGIN": JSON.stringify(
        envLangflow.LANGFLOW_AUTO_LOGIN ?? true,
      ),
    },
    plugins: [react(), svgr(), tsconfigPaths()],
    server: {
      port: port,
      proxy: {
        ...proxyTargets,
      },
    },
  };
});
