--- Demo module used by the agentic-dev-kit fixture tests.
local M = {}

--- Returns the sum of two integers.
---@param left integer
---@param right integer
---@return integer
function M.add(left, right)
    return left + right
end

return M
