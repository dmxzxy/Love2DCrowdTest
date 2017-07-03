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
local Tick = require("Common.Tick");
local piefiller = require("Common.piefiller");
local Prof = piefiller:new()
require("Common.lovedebug");

local Grid = require 'Common.jumper.grid'
local PF = require 'Common.jumper.pathfinder'

local kWorld = nil;
local kStarfield = nil;
local kBattleField = nil;
local kFinder = nil;
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

  Tick.framerate = -1;

  local grid = Grid(kBattleField.map)
  local walkable = function(v) return v~=1 end
  kFinder = PF(grid, 'ASTAR', walkable)
  kFinder:annotateGrid()
end

function love.update(dt)
  --Prof:attach()

  starfield.update(kStarfield, dt);
  World.update(kWorld, dt);

  if Count % 120 == 0 then
    local stats = love.graphics.getStats()
    memUsage = stats.texturememory + Util.round(collectgarbage("count"), 2)
    love.window.setTitle("BeatFever Mania -- "..love.timer.getFPS().." FPS || Game Memory: "..Util.round(memUsage/1024, 2).."kb")
  end
  --Prof:detach()
  --local data = Prof:unpack()
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

    for node, count in currentPath:nodes() do
      local r,c = node:getPos();
      local _i = battlefield.coordinateToIndex(r, c, kBattleField);
      local g = battlefield.getGridByIndex(kBattleField, _i);

      points[index] = offsetX + g.center.x;
      index = index + 1;
      points[index] = offsetY + g.center.y;
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

  local finderName = kFinder:getFinder()
  love.graphics.print(finderName, 0, 665);

  --Prof:draw({50})
  Count = Count + 1
end

function love.keypressed (k)
  if k == 'escape' then
    love.event.quit()
  end
end

local lastSX = nil;
local lastSY = nil;
local lastEX = nil;
local lastEY = nil;
local finderIndex = 1;
local PathSmooth = require("Common.PathSmooth");

function love.mousepressed(x, y, button, istouch)
  WorldInputHandler.mousepressed(x,y,button,istouch);
  if button == 1 then -- Versions prior to 0.10.0 use the MouseConstant 'l'
    if beginPoint == nil then
      beginPoint = Vector2.new(x-offsetX, y-offsetY);
    else
      local endPoint = Vector2.new(x-offsetX, y-offsetY);
      local time = os.clock();

      local starting_node = battlefield.getGridByPosition(kBattleField,beginPoint);
      local goal_node = battlefield.getGridByPosition(kBattleField,endPoint);

      local sx = starting_node.rIndex;
      local sy = starting_node.cIndex;
      local ex = goal_node.rIndex;
      local ey = goal_node.cIndex;

      local finderNames = PF:getFinders()
      kFinder:setFinder(finderNames[finderIndex]);

      local path = kFinder:getPath(sx, sy, ex, ey, 1);
      path = PathSmooth(kFinder, path);
      path:filter();
      currentPath = path;
      beginPoint = nil;
      lastSX = sx;
      lastSY = sy;
      lastEX = ex;
      lastEY = ey;
      lastFindPathTime = (os.clock()-time);
    end
  end
end

function love.keypressed(key)
  Prof:keypressed(key)
end

local smooth = true;

function love.keyreleased( key, scancode )
  if key == 'n' then
    local finderNames = PF:getFinders();
    finderIndex = finderIndex + 1;
    if finderIndex > #finderNames then
      finderIndex = 1;
    end
    kFinder:setFinder(finderNames[finderIndex])
  end
  if key == 'f' then
    local time = os.clock();
    local n = 1;
    for i = 1, n do
      local path = kFinder:getPath(lastSX, lastSY, lastEX, lastEY, 1);
      if smooth then
      path = PathSmooth(kFinder, path);
      path:filter();
      smooth = false;
      else
      smooth = true;
      end
      currentPath = path;
    end
    lastFindPathTime = (os.clock()-time)/n;
  end
end

