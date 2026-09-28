import { randomBytes } from "node:crypto";
import { chmodSync, mkdirSync, openSync, writeFileSync, closeSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, resolve } from "node:path";

const target = process.argv[2] || resolve(homedir(), ".openclaw/secrets/hyperspace.env");
mkdirSync(dirname(target), { recursive: true, mode: 0o700 });
const fd = openSync(target, "wx", 0o600);
try {
  const hmac = randomBytes(32).toString("hex");
  writeFileSync(
    fd,
    [
      "# Fill HYPERSPACE_API_KEY with your backend API key.",
      "HYPERSPACE_API_KEY=",
      `HYPERSPACE_OWNERSHIP_HMAC_KEY=${hmac}`,
      "",
    ].join("\n"),
    { encoding: "utf8" },
  );
} finally {
  closeSync(fd);
  chmodSync(target, 0o600);
}
console.log(`Created private secret file: ${target}`);
