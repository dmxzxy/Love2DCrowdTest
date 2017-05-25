local BattleCrowd = require("Crowd.BattleCrowd");
local Vector2 = require("Vector2");


local World = {};

function World.new()
  local newWorld = {
    crowd = BattleCrowd.new(128),
    selectAgentIdxs = {},
  }
  return newWorld;
end

function World.update(world, dt)
  local crowd = world.crowd;
  BattleCrowd.update(crowd, dt);
end

return World;