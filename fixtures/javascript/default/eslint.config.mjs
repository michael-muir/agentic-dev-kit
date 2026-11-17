import js from "@eslint/js";
import globals from "globals";

export default [
  { ignores: [".agentic/**", "node_modules/**"] },
  js.configs.recommended,
  { languageOptions: { globals: globals.node } },
];
