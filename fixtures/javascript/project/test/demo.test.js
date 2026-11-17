import assert from "node:assert/strict";
import test from "node:test";

import { add } from "../src/demo.js";

test("DEMO-AC-1 adds two integers", () => {
  assert.equal(add(2, 3), 5);
});
