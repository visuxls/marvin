import { spawn } from "node:child_process";
import { createInterface } from "node:readline";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const nextBin = require.resolve("next/dist/bin/next");

const localUrlPattern = /Local:\s+(https?:\/\/\S+)/;

let localUrl = null;
let opened = false;

const child = spawn(
  process.execPath,
  [nextBin, "dev", ...process.argv.slice(2)],
  {
    stdio: ["inherit", "pipe", "pipe"],
    env: process.env,
  },
);

function watchStream(stream, writer) {
  const rl = createInterface({ input: stream });
  rl.on("line", (line) => {
    writer.write(`${line}\n`);
    maybeScheduleOpen(line);
  });
}

watchStream(child.stdout, process.stdout);
watchStream(child.stderr, process.stderr);

child.on("exit", (code, signal) => {
  process.exit(code ?? (signal ? 1 : 0));
});

function maybeScheduleOpen(line) {
  if (opened || process.env.CI) {
    return;
  }

  const match = line.match(localUrlPattern);
  if (!match) {
    return;
  }

  localUrl = match[1];
  void openWhenReady(localUrl);
}

async function openWhenReady(url) {
  for (let attempt = 0; attempt < 60; attempt += 1) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        openBrowser(url);
        opened = true;
        return;
      }
    } catch {
      // Server still starting.
    }
    await new Promise((resolve) => setTimeout(resolve, 200));
  }
}

function openBrowser(url) {
  const platform = process.platform;
  const command =
    platform === "darwin" ? "open" : platform === "win32" ? "start" : "xdg-open";
  const args = platform === "win32" ? ["", url] : [url];

  spawn(command, args, { detached: true, stdio: "ignore" }).unref();
}
