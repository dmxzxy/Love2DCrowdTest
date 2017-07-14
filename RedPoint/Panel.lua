
Panel = class("Panel");
Panel.instanceKey = 1;

function Panel:ctor(redPointType)
	self.instanceKey = Panel.instanceKey + 1;
	self.redPointType = redPointType;
	
	self:onEnter();
end

function Panel:pressButton()
	RedPointMgr:toggleRedPoint(self.redPointType);
end

function Panel:onEnter()
	RedPointMgr:activeRedPoint(self.redPointType, self.instanceKey, function(state)
		if state then
			print("RedPoint is Open");
		else
			print("RedPoint is Close")
		end
	end)
end

function Panel:onExit()
	RedPointMgr:deactiveRedPoint(self.redPointType, self.instanceKey);
end

function Panel:destroy()
	self:onExit();
end

return Panel;