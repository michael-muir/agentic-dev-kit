local demo = require("demo")

describe("demo", function()
    it("DEMO-AC-1 adds two integers", function()
        assert.are.equal(5, demo.add(2, 3))
    end)
end)
