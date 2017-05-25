local BattleCrowd = require("Crowd.BattleCrowd");
local Vector2 = require("Vector2");

local WorldInputHandler = {
  world = nil,
  xOffset = 0,
  yOffset = 0,
};
local this = WorldInputHandler;

function WorldInputHandler.mousepressed(x, y, button, istouch)
  local world = WorldInputHandler.world;
  local crowd = world.crowd;
  if world == nil then
    return;
  end
  x = x - this.xOffset;
  y = y - this.yOffset;

  if button == 1 then
    for k,v in pairs(world.selectAgentIdxs) do
      BattleCrowd.requestMoveTarget(crowd, k, Vector2.new(x,y));
    end
  end
  
  if button == 2 then
    local param = BattleCrowd.createAgentParamTemplate;
    local pt = math.random(0,1);
    if pt == 1 then
    param.radius = 4;--math.random(2, 3);
    param.maxSpeed = 50;
    param.mass = 1;
    else
    param.radius = 16;--math.random(2, 3);
    param.maxSpeed = 50;
    param.mass = 6;
    end
    
    BattleCrowd.addAgent(crowd, Vector2.new(x,y), param);
  end
  
  if button == 3 then
    local agentCount = BattleCrowd.getAgentCount(crowd);
    for i = 1, agentCount do
      local agent = BattleCrowd.getAgent(crowd, i);
      if agent.active then
        if Vector2.distanceSquared(agent.pos, Vector2.new(x,y)) <= agent.radius*agent.radius then
          if world.selectAgentIdxs[i] then
            world.selectAgentIdxs[i] = nil;
          else
            world.selectAgentIdxs[i] = true;
          end
        end
      end
    end
  end
end

return WorldInputHandler;