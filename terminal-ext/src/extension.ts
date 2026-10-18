import * as vscode from "vscode";
import * as fs from "fs";
import * as net from "net";
import * as path from "path";
import * as os from "os";

let output: vscode.OutputChannel;
let windowId: string;
let socketServer: net.Server | undefined;

const registryDir = path.join(os.homedir(), ".terminal-ext", "windows");

// Fixed vocabulary: the socket never accepts arbitrary text, only these
// literal, pre-approved commands. This keeps a compromised connection to
// the socket from doing anything beyond invoking one of these exact strings.
const ALLOWED_COMMANDS = ["sendText"] as const;
const ALLOWED_PAYLOADS = ["/compact"] as const;
type AllowedCommand = (typeof ALLOWED_COMMANDS)[number];
type AllowedPayload = (typeof ALLOWED_PAYLOADS)[number];

interface SocketMessage {
  command: AllowedCommand;
  target: string;
  payload: AllowedPayload;
}

function isSocketMessage(value: unknown): value is SocketMessage {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  const keys = Object.keys(value);
  if (keys.length !== 3 || !keys.every((k) => ["command", "target", "payload"].includes(k))) {
    return false;
  }
  const v = value as Record<string, unknown>;
  return (
    typeof v.command === "string" &&
    (ALLOWED_COMMANDS as readonly string[]).includes(v.command) &&
    typeof v.target === "string" &&
    typeof v.payload === "string" &&
    (ALLOWED_PAYLOADS as readonly string[]).includes(v.payload)
  );
}

function socketPath(): string {
  return path.join(registryDir, `${vscode.env.sessionId}.sock`);
}

function registryPath(): string {
  return path.join(registryDir, `${vscode.env.sessionId}.json`);
}

function writeRegistry(): void {
  try {
    fs.mkdirSync(registryDir, { recursive: true, mode: 0o700 });
    fs.chmodSync(registryDir, 0o700);
    const workspaceFolders = (vscode.workspace.workspaceFolders ?? []).map((f) => f.uri.fsPath);
    const entry = {
      sessionId: vscode.env.sessionId,
      workspaceFolders,
      terminals: vscode.window.terminals.map((t) => t.name),
      socketPath: socketPath(),
      updatedAt: Date.now(),
    };
    fs.writeFileSync(registryPath(), JSON.stringify(entry, null, 2));
  } catch (e) {
    output.appendLine(`[${windowId}] failed to write registry: ${e}`);
  }
}

function removeRegistry(): void {
  try {
    fs.unlinkSync(registryPath());
  } catch {
    // best effort
  }
}

const MAX_LINE_LENGTH = 4096;

function startSocketServer(): void {
  const sockPath = socketPath();
  try {
    fs.mkdirSync(registryDir, { recursive: true, mode: 0o700 });
    fs.unlinkSync(sockPath);
  } catch {
    // stale socket may not exist, that's fine
  }

  const server = net.createServer((conn) => {
    let buffer = "";
    conn.on("data", (chunk) => {
      buffer += chunk.toString("utf8");
      if (buffer.length > MAX_LINE_LENGTH) {
        conn.write(JSON.stringify({ ok: false, error: "message too long" }) + "\n");
        conn.destroy();
        return;
      }
      let newlineIndex: number;
      while ((newlineIndex = buffer.indexOf("\n")) !== -1) {
        const line = buffer.slice(0, newlineIndex);
        buffer = buffer.slice(newlineIndex + 1);
        handleSocketLine(line, conn);
      }
    });
    conn.on("error", () => {
      // best effort; client disconnected or similar
    });
  });

  server.on("error", (e) => {
    output.appendLine(`[${windowId}] socket server error: ${e}`);
  });

  server.listen(sockPath, () => {
    try {
      fs.chmodSync(sockPath, 0o600);
    } catch (e) {
      output.appendLine(`[${windowId}] failed to chmod socket: ${e}`);
    }
    output.appendLine(`[${windowId}] socket listening at ${sockPath}`);
  });

  socketServer = server;
}

function handleSocketLine(line: string, conn: net.Socket): void {
  let parsed: unknown;
  try {
    parsed = JSON.parse(line);
  } catch {
    conn.write(JSON.stringify({ ok: false, error: "invalid JSON" }) + "\n");
    return;
  }

  if (!isSocketMessage(parsed)) {
    conn.write(JSON.stringify({ ok: false, error: "message rejected: not an allowed command/payload" }) + "\n");
    output.appendLine(`[${windowId}] rejected socket message: ${line}`);
    return;
  }

  const terminal = vscode.window.terminals.find((t) => t.name === parsed.target);
  if (!terminal) {
    conn.write(JSON.stringify({ ok: false, error: `no terminal named ${parsed.target}` }) + "\n");
    return;
  }

  terminal.sendText(parsed.payload, true);
  output.appendLine(`[${windowId}] socket: sent ${parsed.payload} to terminal ${parsed.target}`);
  conn.write(JSON.stringify({ ok: true }) + "\n");
}

function stopSocketServer(): void {
  socketServer?.close();
  try {
    fs.unlinkSync(socketPath());
  } catch {
    // best effort
  }
}

function openSplitTerminal(cmd?: string, name?: string): void {
  const targetColumn = vscode.window.tabGroups.activeTabGroup.viewColumn;
  const options: vscode.TerminalOptions = {
    location: { viewColumn: targetColumn },
  };
  if (name) {
    options.name = name;
  }
  const terminal = vscode.window.createTerminal(options);
  terminal.show();
  if (cmd) {
    terminal.sendText(cmd, true);
  }
}

function findTerminal(name?: string): vscode.Terminal | undefined {
  if (!name) {
    return vscode.window.activeTerminal;
  }
  return vscode.window.terminals.find((t) => t.name === name);
}

function sendText(text: string, name?: string): void {
  const terminal = findTerminal(name);
  if (!terminal) {
    return;
  }
  terminal.sendText(text, true);
}

export function activate(context: vscode.ExtensionContext): void {
  output = vscode.window.createOutputChannel("Terminal Ext");
  windowId = `${vscode.workspace.name ?? "no-workspace"}:${vscode.env.sessionId.slice(0, 8)}`;
  output.appendLine(`[${windowId}] activated`);

  writeRegistry();
  startSocketServer();

  context.subscriptions.push(
    output,
    vscode.window.onDidOpenTerminal(() => writeRegistry()),
    vscode.window.onDidCloseTerminal(() => writeRegistry()),
    vscode.window.registerUriHandler({
      handleUri(uri: vscode.Uri) {
        const params = new URLSearchParams(uri.query);
        if (uri.path === "/openTerminal") {
          const cmd = params.get("cmd") ?? undefined;
          const name = params.get("name") ?? undefined;
          openSplitTerminal(cmd, name);
        } else if (uri.path === "/sendText") {
          const text = params.get("text");
          const name = params.get("name") ?? undefined;
          if (text) {
            sendText(text, name);
          }
        }
      },
    }),
    vscode.commands.registerCommand("terminal-ext.openSplitTerminal", () => openSplitTerminal())
  );
}

export function deactivate(): void {
  stopSocketServer();
  removeRegistry();
}
