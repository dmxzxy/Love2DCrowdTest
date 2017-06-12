local BattleCrowd = require("Crowd.BattleCrowd");
local Vector2 = require("Vector2");


local World = {};

function World.new()
  local newWorld = {
    crowd = BattleCrowd.new(128),
    selectAgentIdxs = {},
    
    sampleTime = 0,
    sampleCount = 0,
  }
  return newWorld;
end

function World.update(world, dt)
  local startTime = os.clock();
  
  local crowd = world.crowd;
  BattleCrowd.update(crowd, dt);
  
  world.sampleTime = world.sampleTime + os.clock() - startTime;
  world.sampleCount = world.sampleCount + 1;
  if world.sampleCount > 1000 then
    print("World/update " .. (world.sampleTime));
    world.sampleTime = 0;
    world.sampleCount = 0;
  end
end

return World;