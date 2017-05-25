Util = {};

function Util.round(num, precision)
	return tonumber(string.format("%." .. (precision or 0) .. "f", num));
end


return Util;