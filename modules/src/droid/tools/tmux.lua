local std = require('include.stdlib')

---
local Tmux = std.class {
	name = 'termux';
	app = { false };

	['<'] = function(o, app)
		local info = {
			['object'] = o;
			['deps'] = {
				['installer'] = 'apt';
				['lazy'] = { 'curl' };
				['init'] = { 'termux-api' };
			}
		}
		table.insert(app.tools, info)
		o.app = app
	end;

	-- load package
	init = function(o)
		print(o.name .. ' initialized.')
	end;
}

return Tmux
