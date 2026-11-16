-- agentic-dev-kit standards pack: lua-default
std = "max"                 -- union of Lua 5.1-5.4 and LuaJIT globals; narrow it (e.g. "lua54") per project
max_line_length = 120
unused_args = true
unused_secondaries = true
allow_defined_top = false   -- no accidental globals
exclude_files = { ".agentic/**", "lua_modules/**", ".luarocks/**" }

files["spec/**/*.lua"] = { std = "+busted" }
files["tests/**/*.lua"] = { std = "+busted" }
files["**/*_spec.lua"] = { std = "+busted" }
