local std = require('stdlib')
local popen = std.popen

local Apt = std.class {
	name = 'apt';
	pending = {};

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

