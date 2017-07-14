RedPointMgr = {
	activeRedPoints = {},
};

local function newRedPoint(_type)
	local newRedPoint = {
		type = _type,
		isOpen = false,
		callbacks = {},
	}
	return newRedPoint;
end


function RedPointMgr:activeRedPoint(type, instanceKey, onChange)
	print("RedPointMgr:activeRedPoint "..type.." "..instanceKey);
	self.activeRedPoints[type] = self.activeRedPoints[type] or newRedPoint(type);
	local redPoint = self.activeRedPoints[type];
	redPoint.callbacks[instanceKey] = onChange;
	
	local isOpen = self:checkRedPoint(redPoint);
	self:switchRedPoint(redPoint, isOpen);
end

function RedPointMgr:deactiveRedPoint(type, instanceKey)
	print("RedPointMgr:deactiveRedPoint "..type.." "..instanceKey);
end

function RedPointMgr:toggleRedPoint(type)
	local redPoint = self.activeRedPoints[type];
	self:switchRedPoint(redPoint, false);
end

function RedPointMgr:switchRedPoint(redPoint, isOpen)
	if redPoint.isOpen ~= isOpen then
		redPoint.isOpen = isOpen;
		for k,v in pairs(redPoint.callbacks) do
			v(redPoint.isOpen);
		end
	end
end


function RedPointMgr:notifyMsg(msg)
	
end

function RedPointMgr:checkRedPoint(redPoint)
	return true;
end