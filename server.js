import express from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import url from 'url';

const __filename = url.fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.OPENCLAW_PORT || 8080;

app.use(cors());
app.use(express.json());

// Load config if present
let config = {};
const configPath = path.join(path.dirname(__dirname), 'openclaw.json');
try {
  if (fs.existsSync(configPath)) {
    config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
  }
} catch {}

// Health check
app.get('/health', (_req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Basic info endpoint
app.get('/api/info', (_req, res) => {
  res.json({
    name: 'OpenClaw Gateway',
    version: '0.1.0',
    port: PORT,
    models: config?.agents?.defaults?.model || 'unknown',
  });
});

// Serve dashboard from canvas/
const dashboardDir = path.join(__dirname, 'canvas');
if (fs.existsSync(dashboardDir)) {
  app.use('/', express.static(dashboardDir, { index: 'index.html' }));
} else {
  app.get('/', (_req, res) => {
    res.send(`
      <html>
        <head><title>OpenClaw</title></head>
        <body style="font-family: system-ui; padding: 24px">
          <h1>OpenClaw Gateway</h1>
          <p>Dashboard is not packaged. Health is <a href="/health">/health</a>.</p>
        </body>
      </html>
    `);
  });
}

app.listen(PORT, () => {
  console.log(`OpenClaw Gateway listening on :${PORT}`);
});
