import { describe, expect, it } from "vitest";

import { add } from "./demo";

describe("demo", () => {
  it("DEMO-AC-1 adds two integers", () => {
    expect(add(2, 3)).toBe(5);
  });
});
