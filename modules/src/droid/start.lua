-- imports
local std = require('include.stdlib')
local Droid = require('proj.droid.droid')
local apt = require('proj.droid.tools.apt')
local tmux = require('proj.droid.tools.tmux')

local main = function(config)
	if config ~= nil then
		print('config: ')
		std.inspect(config)
	end
	-- start initialize droid
	local droid = Droid()
	-- load tools
	apt(droid)
	tmux(droid)
	-- enter loop
	droid:loop()
end
-- export main
return main
