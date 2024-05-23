local std = require('include.stdlib')
local effil = require('effil')
require('strong') -- luarock

local Droid = std.class {
	tts = { false };
	event = std.event;
	tools = { false };
	logs = effil.channel();

	['<'] = function(o)
		print('-- started --')
		o.event.on('shutdown', o.shutdown)
	end;

	log = function(o, msg)
		o.logs:push(msg .. '\n')
	end;

	tool = function(o, name)
		for _, tl in ipairs(o.tools) do
			if tl.object.name == name then
				return tl.object
			end
		end
	end;

	loop = function(o)
		-- install
		local installer = { false }
		for _, tool in ipairs(o.tools) do
			if tool.object.name == 'apt' then
				installer = tool.object
			end
			if installer and tool.deps ~= nil then
				if tool.deps.init ~= nil then
					for _, init in ipairs(tool.deps.init) do
						local ok = installer:install(init)
						if not ok then
							o:log("Error! Missing dependency: " .. init)
							return o.event.dispatch('shutdown')
						end
					end
				end
				-- lazy install, no check
				if tool.deps.lazy ~= nil then
					for _, lazy in ipairs(tool.deps.lazy) do
						installer:install(lazy)
					end
				end
			end
		end
		-- todo: init call stack & return addressing
		-- todo: create entry point
		o.event.dispatch('initialized', o)
		print('init complete')
		-- trigger shutdown
		o.event.dispatch('shutdown', o)
	end;

	shutdown = function(o)
		print('-- stopped: logs<' .. tostring(o.logs:size()) ..'> --')
	end;
}

return Droid
