local Vector2 = require("Vector2");
local BattleAgent = require("Crowd.BattleAgent");
local proximity = require("Crowd.Core.proximity");

local BattleCrowd = {};
local this = BattleCrowd;

BattleCrowd.createAgentParamTemplate = {
  mass = 1.0,
  radius = 10.0,
  maxSpeed = 1.0,
};

local function sqr(num)
  return num*num;
end

local function integrate(ag, dt)
  local maxAcceleration = ag.maxAcceleration;
  local maxDelta = maxAcceleration * dt;
  local dv = Vector2.sub(ag.nvel, ag.vel);
  local ds = Vector2.magnitude(dv);
  if ds > maxDelta then
    dv = Vector2.mul(dv, maxDelta/ds);
  end
  ag.vel = Vector2.add(ag.vel,dv);
  if Vector2.magnitude(ag.vel) > 0.00001 then
    ag.pos = Vector2.add(ag.pos, Vector2.mul(ag.vel, dt));
    ag.forward = Vector2.normalized(ag.vel);
  else
    Vector2.set(ag.vel, 0, 0);
  end
end

local function getNeighbours(pos, range, skip, result, maxResult, agents)
  result = result or {};

  local n = 0;

  local idxs = {};
  local num = proximity.queryItems(pos.x-range,pos.y-range,pos.x+range,pos.y+range,idxs,32);
  for i = 1, num do
    local ag = agents[idxs[i]];
    if ag ~= skip then
      local diff = Vector2.sub(pos, ag.pos);
      local distSqr = Vector2.sqrtMagnitude(diff);
      if distSqr <= sqr(range) then
        if n <= maxResult then
          result[n+1] = {
            idx = idxs[i],
            dist = distSqr,
          };
          n = n + 1;
        end
      end
    end
  end

  return n;
end


function BattleCrowd.new(maxAgents)
  local newCrowd = {
    maxAgents = maxAgents,
    agents = {},

    --temp use
    activeAgents = {},
  };

  for i = 1, maxAgents do
    local newAgent = BattleAgent.new();
    newAgent.idx = i;
    newCrowd.agents[i] = newAgent;
  end

  return newCrowd;
end

function BattleCrowd.addAgent(crowd, pos, param)
  local idx = -1;
  for i = 1, crowd.maxAgents do
    if not crowd.agents[i].active then
      idx = i;
      break;
    end
  end

  if idx == -1 then
    return nil;
  end

  local agent = crowd.agents[idx];
  --param set
  BattleCrowd.updateAgentParam(crowd, idx, param);
  agent.pos = Vector2.clone(pos);
  agent.active = true;
  return agent;
end

function BattleCrowd.updateAgentParam(crowd, idx, param)
  local maxAgents = crowd.maxAgents;
  if idx < 0 or idx >= maxAgents then
    return;
  end
  local agent = crowd.agents[idx];
  agent.mass = param.mass;
  agent.radius = param.radius;
  agent.maxSpeed = param.maxSpeed;
end

function BattleCrowd.getAgent(crowd, idx)
  local maxAgents = crowd.maxAgents;
  if idx <= 0 or idx > maxAgents then
    return nil;
  end
  return crowd.agents[idx];
end

function BattleCrowd.getAgentCount(crowd)
  return crowd.maxAgents;
end

function BattleCrowd.requestMoveTarget(crowd, idx, pos)
  local maxAgents = crowd.maxAgents;
  if idx < 0 or idx >= maxAgents then
  end
  local agent = crowd.agents[idx];
  agent.targetPos = Vector2.clone(pos);
  agent.targetState = 1;
end

function BattleCrowd.getActiveAgents(crowd, agents, maxAgents)
  local n = 0;
  for i = 1, maxAgents do
    local ag = crowd.agents[i];
    if ag.active and n < maxAgents then
      agents[n + 1] = ag;
      n = n + 1;
    end
  end
  return n;
end

function BattleCrowd.update(crowd, dt)
  local agents = crowd.activeAgents;
  local nagents = BattleCrowd.getActiveAgents(crowd, agents, crowd.maxAgents);

  proximity.clear();
  for i = 1, nagents do
    local ag = agents[i];
    local pos = ag.pos;
    local r = ag.radius;
    proximity.addItem(i, pos.x-r, pos.y-r, pos.x+r, pos.y+r);
  end

  for i = 1, nagents do
    local ag = agents[i];
    ag.nneis = getNeighbours(ag.pos, ag.radius*12.0, ag, ag.neis, 32, agents);
  end

  for i = 1, nagents do
    local ag = agents[i];
    if ag.targetState ~= 0 then
      local dvel = Vector2.new();
      local dir = Vector2.sub(ag.targetPos, ag.pos);
      Vector2.normalize(dir);
      Vector2.copy(dvel, dir);

      local slowDownRadius = ag.radius*2;
      local dis = Vector2.distance(ag.targetPos, ag.pos);
      local speedScale = math.min(dis, slowDownRadius)/slowDownRadius;
      dvel = Vector2.mul(dvel, ag.maxSpeed*speedScale);
      ag.dvel = dvel;
    end
  end

  for i = 1, nagents do
    local ag = agents[i];
    if ag.targetState ~= 0 then
      ag.nVelocity = Vector2.new();
      Vector2.copy(ag.nvel, ag.dvel);   
    end
  end

  for i = 1, nagents do
    local ag = agents[i];
    if ag.targetState ~= 0 then
      integrate(ag, dt); 
    end
  end

  for iter = 1, 4 do
    for i = 1, nagents do
      local ag = agents[i];
      Vector2.set(ag.disp,0,0);
      local w = 0;
      for j = 1, ag.nneis do
        local nag = agents[ag.neis[j].idx];
        local diff = Vector2.sub(ag.pos, nag.pos);
        local dist = Vector2.sqrtMagnitude(diff);
        if dist < sqr(ag.radius + nag.radius) then
          dist = math.sqrt(dist);
          local pen = (ag.radius + nag.radius) - dist;
          if dist < 0.00001 then
            if ag.idx > nag.idx then
              Vector2.set(diff, -ag.dvel.y, ag.dvel.x);
            else
              Vector2.set(diff, ag.dvel.y, -ag.dvel.x);
            end
            pen = 0.01;
          else
            local massWight = nag.mass/(ag.mass + nag.mass);
            pen = (1.0/dist) * (pen*massWight) * 0.7;
          end
          Vector2.copy(ag.disp, Vector2.add(ag.disp, Vector2.mul(diff,pen)));
          w = w + 1.0;
        end
      end
      if w > 0.0001 then
        local iw = 1.0/w;
        Vector2.mul(ag.disp, iw);
      end
    end
    for i = 1, nagents do
      local ag = agents[i];
      Vector2.copy(ag.pos, Vector2.add(ag.pos, ag.disp));
    end
  end

end


return BattleCrowd;