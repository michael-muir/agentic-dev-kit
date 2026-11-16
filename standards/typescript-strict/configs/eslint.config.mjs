// agentic-dev-kit standards pack: typescript-strict
// Needs devDependencies: eslint, @eslint/js, typescript-eslint, typescript (Node 20.11+).
// @ts-check
import eslint from "@eslint/js";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["dist/**", "build/**", "coverage/**", "node_modules/**", ".agentic/**"] },
  eslint.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,
  {
    languageOptions: {
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
    },
    rules: {
      "@typescript-eslint/explicit-module-boundary-types": "error",
      "@typescript-eslint/consistent-type-imports": "error",
      "@typescript-eslint/switch-exhaustiveness-check": "error",
      eqeqeq: ["error", "always"],
      "no-console": ["error", { allow: ["warn", "error"] }],
    },
  },
  {
    files: ["**/*.test.ts", "**/*.spec.ts", "**/*.test.tsx", "**/*.spec.tsx", "tests/**", "test/**"],
    rules: { "@typescript-eslint/no-non-null-assertion": "off" },
  },
  { files: ["**/*.js", "**/*.mjs", "**/*.cjs"], ...tseslint.configs.disableTypeChecked },
);
