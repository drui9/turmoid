local std = require('include.stdlib')
local requests = require('include.network.requests.init')

local main = function(conf)
	local endpoint = 'http://localhost:8000/auth'
	headers = {
		['CAVA-AUTH'] = conf['cava-auth']
	}
	local rep = requests:get(endpoint, headers)
	local out = xpcall(rep:json())
	std.inspect(out)
end

return main
