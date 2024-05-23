#!/data/data/com.termux/files/usr/bin/lua
local std = require('include.stdlib')
local file = io.open('turmoid.json')
-- load project config
local projdata = file:read('*all')
local proj = std.json.decode(projdata)

-- load main func
local enter = require('proj.' .. proj.main .. '.start')

-- search main & launch
local done = false
local retcode = nil
if proj.projects then
	for _, project in ipairs(proj.projects) do
		if done == true then break end
		for k, v in pairs(project) do
			if k == proj.main then
				retcode = enter(v)
				done = true
				break
			end
		end
	end
end

-- start without config
if done == false then
	done = true
	enter()
end

-- print return vals
if done then
	print('-- done --')
	if retcode ~= nil then
		print('retcode: ' .. tostring(retcode))
	end
end
