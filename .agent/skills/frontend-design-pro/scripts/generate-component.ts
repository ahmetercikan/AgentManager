/**
 * Usage:
 *   node generate-component.ts --help
 *   node generate-component.ts --name HeroGlass --out ./HeroGlass.tsx
 */

type Args = Record<string, string | boolean>;

function parseArgs(argv: string[]): Args {
    const args: Args = {};
    for (let i = 2; i < argv.length; i++) {
        const a = argv[i];
        if (a === "--help") args["help"] = true;
        else if (a.startsWith("--")) {
            const key = a.slice(2);
            const val = argv[i + 1] && !argv[i + 1].startsWith("--") ? argv[++i] : true;
            args[key] = val;
        }
    }
    return args;
}

const args = parseArgs(process.argv);

if (args.help) {
    console.log("Usage: node generate-component.ts --name <ComponentName> --out <path>");
    process.exit(0);
}

const name = String(args.name || "GlassComponent");
const out = String(args.out || `./${name}.tsx`);

const template = `export default function ${name}() {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl shadow-2xl shadow-black/20 p-6">
      <h2 className="text-xl font-semibold text-white">${name}</h2>
      <p className="mt-2 text-white/70">Glassmorphism ready.</p>
    </div>
  );
}
`;

import { writeFileSync } from "node:fs";
writeFileSync(out, template, "utf8");
console.log("Generated:", out);
