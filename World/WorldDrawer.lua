local Vector2 = require("Vector2");
local BattleCrowd = require("Crowd.BattleCrowd");

local WorldDrawer = {};

function WorldDrawer.drawAgent(agent, offsetX, offsetY, idxSel)
  if agent == nil then
    return;
  end
  if not agent.active then
    return;
  end
  
  local pos = agent.pos;
  local forward = agent.forward;
  local radius = agent.radius;
  local drawPos = Vector2.new(pos.x+offsetX, pos.y+offsetY);
  love.graphics.setColor(0, 255, 0, 255);
  love.graphics.circle("fill", drawPos.x, drawPos.y, radius, 100);
  
  love.graphics.setColor(0, 0, 255, 255);
  local lineTo = Vector2.add(drawPos, Vector2.mul(forward, radius));
  love.graphics.line(drawPos.x, drawPos.y, lineTo.x, lineTo.y);
  
  if idxSel then
    love.graphics.setColor(255, 0, 0, 255);
    love.graphics.circle("line", drawPos.x, drawPos.y, radius, 100);
    
    
    local lineTo = Vector2.new(agent.targetPos.x+offsetX,agent.targetPos.y+offsetY);
    love.graphics.line(drawPos.x, drawPos.y, lineTo.x, lineTo.y);
  end
end


function WorldDrawer.draw(world, offsetX, offsetY)
  local crowd = world.crowd;
  local agentCount = BattleCrowd.getAgentCount(crowd);
  for i = 1, agentCount do
    local agent = BattleCrowd.getAgent(crowd, i);
    
    local idxSel = world.selectAgentIdxs[i];
    WorldDrawer.drawAgent(agent, offsetX, offsetY, idxSel);
  end
end

return WorldDrawer;