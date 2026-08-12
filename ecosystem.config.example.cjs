module.exports = {
  apps: [
    {
      name: "radar-api",
      cwd: "/opt/radar-tech-ia/apps/api",
      script: ".venv/bin/uvicorn",
      args: "radar_api.main:app --host 127.0.0.1 --port 4101",
      interpreter: "none",
      env: {
        APP_ENV: "production",
      },
    },
    {
      name: "radar-web",
      cwd: "/opt/radar-tech-ia/apps/web",
      script: "node_modules/next/dist/bin/next",
      args: "start --hostname 127.0.0.1 --port 4100",
      interpreter: "node",
      env: {
        NODE_ENV: "production",
        NEXT_TELEMETRY_DISABLED: "1",
      },
    },
  ],
};
