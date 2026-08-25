import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
// web-tree-sitter runs the official Tree-sitter Bash grammar as WASM, which
// works in Pi's Bun runtime (native Node Tree-sitter bindings do not).
const TreeSitter = require("web-tree-sitter");
import {
  isToolCallEventType,
  type ExtensionAPI,
} from "@earendil-works/pi-coding-agent";

type Policy = {
  /** In whitelist mode, every external executable must be listed in allowed. */
  mode: "whitelist" | "blacklist";
  allowed: string[];
  blocked: string[];
};

const POLICY_FILE = "guardrail-policy.json";
let parser: any;

const DEFAULT_POLICY: Policy = {
  mode: "whitelist",
  // Shells and interpreters are deliberately absent: allowing one defeats a
  // command allowlist because it can execute arbitrary code.
  allowed: ["git", "rg", "grep", "find", "ls", "cat", "sed", "awk"],
  blocked: ["bash", "sh", "zsh", "fish", "dash", "sudo", "su", "doas", "env", "eval", "exec", "source", ".", "xargs", "curl", "wget", "nc", "ncat", "netcat"],
};

const SHELL_BUILTINS = new Set([
  "cd", "pwd", "echo", "printf", "true", "false", "test", "[", "[[", "wait", "read", "export", "unset", "umask", "ulimit", "set", "shift", "type", "hash", "dirs", "pushd", "popd",
]);
const DYNAMIC_NODE_TYPES = new Set([
  "command_substitution", "process_substitution", "variable_expansion", "expansion",
  "heredoc_redirect", "function_definition",
]);

function normalise(items: string[] | undefined): Set<string> {
  return new Set((items ?? []).map((item) => item.trim()).filter(Boolean));
}

async function loadPolicy(): Promise<Policy> {
  const file = resolve(__dirname, POLICY_FILE);
  try {
    const parsed = JSON.parse(await readFile(file, "utf8")) as Partial<Policy>;
    if (parsed.mode !== "whitelist" && parsed.mode !== "blacklist") {
      throw new Error('"mode" must be "whitelist" or "blacklist"');
    }
    if (!Array.isArray(parsed.allowed) || !Array.isArray(parsed.blocked)) {
      throw new Error('"allowed" and "blocked" must be arrays');
    }
    return { mode: parsed.mode, allowed: parsed.allowed, blocked: parsed.blocked };
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return DEFAULT_POLICY;
    throw error;
  }
}

function walk(node: any, visit: (node: any) => void): void {
  visit(node);
  for (const child of node.namedChildren) walk(child, visit);
}

/** Extract every command_name from Tree-sitter's official Bash AST. */
function executableCommands(command: string): string[] {
  const tree = parser.parse(command);
  if (tree.rootNode.hasError) throw new Error("Bash syntax could not be parsed safely");

  const executables: string[] = [];
  walk(tree.rootNode, (node) => {
    if (DYNAMIC_NODE_TYPES.has(node.type)) {
      throw new Error(`dynamic Bash construct is not permitted: ${node.type}`);
    }
    if (node.type !== "command") return;

    const name = node.namedChildren.find((child: any) => child.type === "command_name");
    if (!name) throw new Error("Bash command has no static executable name");
    if (name.namedChildCount !== 1 || name.namedChildren[0].type !== "word") {
      throw new Error(`dynamic Bash executable is not permitted: ${name.text}`);
    }

    const executable = name.text;
    if (executable.includes("/") || executable.includes("$")) {
      throw new Error(`path-based or dynamic executable is not permitted: ${executable}`);
    }
    if (!SHELL_BUILTINS.has(executable)) executables.push(executable);
  });
  return executables;
}

export default async function (pi: ExtensionAPI) {
  await TreeSitter.Parser.init();
  const grammarPath = require.resolve("tree-sitter-bash/tree-sitter-bash.wasm");
  const language = await TreeSitter.Language.load(grammarPath);
  parser = new TreeSitter.Parser();
  parser.setLanguage(language);

  pi.on("tool_call", async (event, ctx) => {
    if (!isToolCallEventType("bash", event)) return;

    let policy: Policy;
    let commands: string[];
    try {
      policy = await loadPolicy();
      commands = executableCommands(event.input.command);
    } catch (error) {
      // Policy errors and syntax we cannot safely analyse are denied.
      return {
        block: true,
        reason: `Guardrail blocked this Bash call because it cannot safely analyse it (${(error as Error).message}). Do not retry this command or attempt to bypass the guardrail. Find an allowed alternative; if this goal genuinely requires the blocked operation, ask the user for permission before proceeding.`,
      };
    }

    const allowed = normalise(policy.allowed);
    const blocked = normalise([...DEFAULT_POLICY.blocked, ...policy.blocked]);
    for (const executable of commands) {
      if (blocked.has(executable)) {
        return {
          block: true,
          reason: `Guardrail blocked the executable "${executable}". Do not retry it or attempt to bypass this restriction. Find an allowed alternative; if the task can only be completed with "${executable}", ask the user for permission before proceeding.`,
        };
      }
      if (policy.mode === "whitelist" && !allowed.has(executable)) {
        return {
          block: true,
          reason: `Guardrail does not whitelist the executable "${executable}". Do not retry it or attempt to bypass this restriction. Find an allowed alternative; if the task can only be completed with "${executable}", ask the user for permission before proceeding.`,
        };
      }
    }
  });
}
