local std = require('include.stdlib')
local popen = std.popen

local Apt = std.class {
	name = 'apt';
	pending = {};
	app = { false };

	-- initialize tool
	['<'] = function(o, app)
		local info = {
			['object'] = o;
		}
		table.insert(app.tools, info)
		o.app = app
		app.event.on('initialized', o.init)
	end;

	-- start module
	init = function(app)
		local o = app:tool('apt')
		print(o.name .. ' started.')
	end;

	-- install package
	install = function(o, pkg)
		assert(pkg, 'Missing package name!')
		local found = o:check(pkg)
		if found then
			return found
		end
		local ret, out = popen('apt-get install -y ' .. pkg .. ' 2> /dev/null')
		if ret ~= 0 then
			table.insert(o.pending, pkg)
			print('Marked ' .. pkg .. ' for installation.')
		else
			local index = table.findIndex(o.pending, function(x)
				return x == pkg
			end)
			table.remove(o.pending, index)
			return true
		end
	end;

	-- check installed
	check = function(o, pkg)
		assert(pkg, 'Missing package name!')
		if table.includes(o.pending, pkg) then -- prev install failed 
			return
		end
		local ret, out = popen('dpkg -s ' .. pkg .. ' 2> /dev/null')
		if ret == 0 and #out ~= 0 then
			out = string.split(out, '\n')
			return std.fun.grep('ok installed', out):length() == 1
		end
	end
}
return Apt
