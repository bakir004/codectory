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
  whitelist: string[];
  blacklist: string[];
};

const POLICY_FILE = "guardrail-policy.json";
let parser: any;

const DEFAULT_POLICY: Policy = {
  whitelist: [],
  blacklist: ["curl"],
};

const SHELL_BUILTINS = new Set([
  "cd", "pwd", "echo", "printf", "true", "false", "test", "[", "[[", "wait", "read", "export", "unset", "umask", "ulimit", "set", "shift", "type", "hash", "dirs", "pushd", "popd",
]);
function normalise(items: string[] | undefined): Set<string> {
  return new Set((items ?? []).map((item) => item.trim()).filter(Boolean));
}

async function loadPolicy(): Promise<Policy> {
  const file = resolve(__dirname, POLICY_FILE);
  try {
    const parsed = JSON.parse(await readFile(file, "utf8")) as Partial<Policy>;
    if (!Array.isArray(parsed.whitelist) || !Array.isArray(parsed.blacklist)) {
      throw new Error('"whitelist" and "blacklist" must be arrays');
    }
    const whitelist = normalise(parsed.whitelist);
    const blacklist = normalise(parsed.blacklist);
    const overlap = [...whitelist].filter((item) => blacklist.has(item));
    if (overlap.length) {
      throw new Error(`an executable cannot be in both lists: ${overlap.join(", ")}`);
    }
    return { whitelist: [...whitelist], blacklist: [...blacklist] };
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
    if (node.type !== "command") return;

    const name = node.namedChildren.find((child: any) => child.type === "command_name");
    if (!name) return;
    const executable = name.text.split("/").at(-1) ?? name.text;
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
      // This guardrail blocks curl only; do not turn an unparseable command
      // into a broader restriction.
      return;
    }

    const allowed = normalise(policy.whitelist);
    const blocked = normalise(policy.blacklist);
    for (const executable of commands) {
      if (blocked.has(executable)) {
        return {
          block: true,
          reason: `Guardrail blocked the executable "${executable}". Do not retry it or attempt to bypass this restriction. Find an allowed alternative; if the task can only be completed with "${executable}", ask the user for permission before proceeding.`,
        };
      }
      if (allowed.size && !allowed.has(executable)) {
        return {
          block: true,
          reason: `Guardrail does not whitelist the executable "${executable}".`,
        };
      }
    }
  });
}
