local Vector2 = require("Vector2");

local BattleAgent = {};

function BattleAgent.new()
  local newAgent = {
    idx = 0,
    
    pos = Vector2.new(),
    forward = Vector2.new(0,1),
    
    mass = 1,
    radius = 1.0,
    maxSpeed = 1.0,
    maxAcceleration = 200.0,
    
    disp = Vector2.new(0,0),
    dvel = Vector2.new(0,0),
    nvel = Vector2.new(0,0),
    vel = Vector2.new(0,0),
    
    neis = {},
    nneis = 0,
    
    targetState = 0,
    targetPos = Vector2.new();
    
    active = false,
  };
  
  return newAgent;
end


return BattleAgent;