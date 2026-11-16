// agentic-dev-kit standards pack: javascript-recommended
// Needs devDependencies: eslint, @eslint/js, globals.
import js from "@eslint/js";
import globals from "globals";

export default [
  { ignores: ["dist/**", "build/**", "coverage/**", "node_modules/**", ".agentic/**"] },
  js.configs.recommended,
  {
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: { ...globals.node, ...globals.browser },
    },
    rules: {
      eqeqeq: ["error", "always"],
      "no-var": "error",
      "prefer-const": "error",
      "no-implicit-globals": "error",
      "no-implicit-coercion": "error",
      "no-param-reassign": "error",
      "no-shadow": "error",
      "no-console": ["error", { allow: ["warn", "error"] }],
      "no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
      curly: ["error", "all"],
    },
  },
];
