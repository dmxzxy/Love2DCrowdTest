require("Common.Util")
require("Common.Dump");
local starfield = require("starfield");
local battlefield = require("battlefield");
local starfieldDrawer = require("Drawer.starfieldDrawer");
local battlefieldDrawer = require("Drawer.battlefieldDrawer");
local PathFindHandler = require("PathFindHandler");
local Vector2 = require("Vector2");
local World = require("World.World");
local WorldDrawer = require("World.WorldDrawer");
local WorldInputHandler = require("World.WorldInputHandler");

local kWorld = nil;
local kStarfield = nil;
local kBattleField = nil;
local currentPath = nil;

local beginPoint = nil;

local Count = 120;
local offsetX = 20;
local offsetY = 20;
local scale = 1;
local lastFindPathTime = 0;


function love.load()
  if arg[#arg] == "-debug" then require("mobdebug").start() end
  W, H = love.graphics.getDimensions()
  
  kWorld = World.new();
  kStarfield = starfield.new(W, H, 0, 1024);
  kBattleField = battlefield.new(1300, 600, 16);
--    kBattleField = battlefield.new(100, 100, 25);

  WorldInputHandler.world = kWorld;
  WorldInputHandler.xOffset = offsetX;
  WorldInputHandler.yOffset = offsetY;
end

function love.update(dt)
  starfield.update(kStarfield, dt);
  World.update(kWorld, dt);
  
  if Count % 120 == 0 then
    local stats = love.graphics.getStats()
    memUsage = stats.texturememory + Util.round(collectgarbage("count"), 2)
    love.window.setTitle("BeatFever Mania -- "..love.timer.getFPS().." FPS || Game Memory: "..Util.round(memUsage/1024, 2).."kb")
  end
end

function love.draw ()
  local mousX,mousY = love.mouse.getPosition();
  
  love.graphics.scale(scale, scale)
  starfieldDrawer.draw(kStarfield);
  battlefieldDrawer.draw(offsetX, offsetY, kBattleField);

  WorldDrawer.draw(kWorld, offsetX, offsetY);
  
  if beginPoint ~= nil then
    love.graphics.setColor(64, 0, 64);
    love.graphics.circle("fill", beginPoint.x + offsetX, beginPoint.y + offsetY, 8, 8)
  end

  if currentPath ~= nil then
    local points = {};
    local index = 1;
    love.graphics.setColor(255, 128, 0);
    for k,v in pairs(currentPath) do
      points[index] = offsetX + v.center.x;
      index = index + 1;
      points[index] = offsetY + v.center.y;
      index = index + 1;
    end
    if #points >= 4 then
      love.graphics.setColor(0, 255, 0);
      love.graphics.setLineWidth( 4 )
      love.graphics.line(points);
      local ptNum = #points/2;
      for i = 1, ptNum do
        love.graphics.setColor(64, 0, 64);
        love.graphics.circle("fill", points[2*i-1], points[2*i], 4, 20);
      end
    end
  end

  love.graphics.setColor(255, 255, 255);
  love.graphics.print("find path time = "..lastFindPathTime, 0, 630);

  if openSmooth then
    love.graphics.setColor(255, 255, 255);
    love.graphics.print("openSmooth = true", 0, 650);
  end

  if heuristicChoose then
    love.graphics.setColor(255, 255, 255);
    love.graphics.print("heuristicChoose = true", 0, 665);
  end

  Count = Count + 1
end

function love.keypressed (k)
  if k == 'escape' then
    love.event.quit()
  end
end


local function all_nonzero_subsets_in_order(set)  -- Input is a key set.
  local set_arr = {}
  for key in pairs(set) do set_arr[#set_arr + 1] = key end

  local n = #set_arr
  local t = 1  -- The set of the next subset to return.

  -- c[i] is the index of the ith item to return.
  -- We only return set_arr[c[1], ... , c[t]].
  local c = {1, n + 1, 0}

  return function ()
    -- Return nil if we're done.
    if t > n then return nil end

    -- Build the return set based on c.
    local ret = {}
    for i = 1, t do ret[set_arr[c[i]]] = true end

    -- Walk up j to see how we can increment c.
    local j = 1
    while c[j] + 1 == c[j + 1] do
      c[j] = j
      j = j + 1
    end

    -- Calculate the next c values.
    if j > t then
      -- We're done with the current t.
      t = t + 1
      for i = 1, t do c[i] = i end
      c[t + 1], c[t + 2] = n + 1, 0
    else
      -- Not done with t; set up the next c values.
      c[j] = c[j] + 1
    end

    return ret
  end
end

local function next_hit(from, dir)
  if dir > 0 then
    return math.floor(from + 1)
  else
    return math.ceil (from - 1)
  end
end

local function min(t)
  local m
  for _, v in pairs(t) do
    if m == nil or v < m then
      m = v
    end
  end
  return m
end

local function sign(x)
  if x > 0 then return  1 end
  if x < 0 then return -1 end
  return 0
end



local function path_is_ok(x1, y1, x2, y2, isCollisionFunc)
  local hitfunc = isCollisionFunc or function(c,r)
    return false;
  end
  --print(x1, y1, x2, y2);
  local grid = {x1, y1}
  local p    = {x1 + 0.5, y1 + 0.5}
  local dir  = {x2 - x1, y2 - y1}

  local total_dist = 0  -- Measured in units of the dir vectors.
  local t = {}  -- Tracks incremental movement along the ray.
  local q = {}  -- Helps track potential next points.

  while true do

    -- Find the next_hit distance t for each coord i.
    for i = 1, 2 do
      t[i] = math.huge
      if dir[i] ~= 0 then
        --print('processing dir[' .. i .. ']')
        q[i] = next_hit(p[i], dir[i])
        t[i] = (q[i] - p[i]) / dir[i]
      end
    end

    -- min_set = { i : t[i] = min(t) }, as a key set.
    local min_set = {}
    local t_min = min(t)

    -- We're done if we've passed the destination point, which is distance 1
    -- away from the start point in units of the dir vector.
    total_dist = total_dist + t_min
    if total_dist > 1 then return true end

    for i = 1, 2 do
      -- We allow for 0.001 tolerance of machien precision error.
      if math.abs(t[i] - t_min) < 0.001 then min_set[i] = true end
    end

    -- Move p forward by distance t_min.
    for i = 1, 2 do
      p[i] = p[i] + t_min * dir[i]
    end

    -- Check for any collisions.
    for s in all_nonzero_subsets_in_order(min_set) do
      local h = {}
      for i = 1, 2 do
        -- s is a key set
        h[i] = grid[i] + (s[i] and 1 or 0) * sign(dir[i])
      end
      -- Is there a wall between grid and h?
      --print(x1, y1, x2, y2, h[1], h[2], hitfunc(h[1], h[2]));
      if hitfunc(h[1], h[2]) then return false end
    end

    -- Officially move the grid pt forward.
    for i = 1, 2 do
      grid[i] = grid[i] + (min_set[i] and 1 or 0) * sign(dir[i])
    end
  end

  assert(false, 'should not get out of while loop here')
end

local function cutOverPoints(path)
  if path == nil then
    return nil;
  end
  local newPath = {};
  local numPoint = #path;
  if numPoint < 3 then
    return path;
  end

  table.insert(newPath,path[1]);
  table.insert(newPath,path[2]);

  for i = 3, numPoint do  	
    local curPoint = newPath[#newPath-1];
    local nextPoint = newPath[#newPath];
    local secondPoint = path[i];

    local diffCurR = nextPoint.rIndex - curPoint.rIndex;
    local diffCurC = nextPoint.cIndex - curPoint.cIndex;

    local diffNextR = secondPoint.rIndex - nextPoint.rIndex;
    local diffNextC = secondPoint.cIndex - nextPoint.cIndex;

    if math.atan2(diffCurR,diffCurC) == math.atan2(diffNextR,diffNextC) then
      table.remove(newPath,#newPath);
      table.insert(newPath,secondPoint);
    else
      table.insert(newPath,secondPoint);
    end
  end

  return newPath;
end

local function smoothPath(path)
  local function isCollision(c, r)
    local index = (r-1) * kBattleField.colCount + (c-1)
    if kBattleField.gridlist[index].value > 0 then return true end

    return false
  end

  local num_pts = #path;
  for i = 1, num_pts do
    while true do
      -- Check to see if we can go straight from pt i to pt i + 2.
      local j = i + 2
      if j > #path then break end
      local isOk = path_is_ok(path[i].cIndex, path[i].rIndex, path[j].cIndex, path[j].rIndex, isCollision);
      if isOk then
        table.remove(path, j-1);
      else
        break
      end
    end
  end
  return path
end

lastBeginPoint = nil;
lastEndPoint = nil;
openSmooth = false;
heuristicChoose = true;

function love.mousepressed(x, y, button, istouch)
  WorldInputHandler.mousepressed(x,y,button,istouch);
--  if button == 1 then -- Versions prior to 0.10.0 use the MouseConstant 'l'
--    if beginPoint == nil then
--      beginPoint = Vector2.new(x-offsetX, y-offsetY);
--    else
--      local endPoint = Vector2.new(x-offsetX, y-offsetY);
--      local time = os.clock();
--      lastBeginPoint = beginPoint;
--      lastEndPoint = endPoint;
--      local path = PathFindHandler.find(beginPoint, endPoint, kBattleField);
--      if openSmooth then
--        currentPath = smoothPath(cutOverPoints(path));
--      else
--        currentPath = (cutOverPoints(path));
--      end
--      beginPoint = nil;
--      lastFindPathTime = (os.clock()-time);
--    end
--  end
end

shapeType = 1;
rotDir = 1;

function love.keyreleased( key, scancode )
  if key == "s" then
    openSmooth = not openSmooth;
    if lastBeginPoint and lastEndPoint then
      local path = PathFindHandler.find(lastBeginPoint, lastEndPoint, kBattleField);
      if openSmooth then
        currentPath = smoothPath(cutOverPoints(path));
      else
        currentPath = (cutOverPoints(path));
      end
    end
  end

  if key == "h" then
    heuristicChoose = not heuristicChoose;
    if lastBeginPoint and lastEndPoint then
      local path = PathFindHandler.find(lastBeginPoint, lastEndPoint, kBattleField);
      if openSmooth then
        currentPath = smoothPath(cutOverPoints(path));
      else
        currentPath = (cutOverPoints(path));
      end
    end
  end
  
  if key == "n" then
    shapeType = shapeType + 1;
    if shapeType > 6 then
      shapeType = 1;
    end
  end
  
  if key == "r" then
    rotDir = rotDir + 1;
    if rotDir > 4 then
      rotDir = 1;
    end
  end

end

