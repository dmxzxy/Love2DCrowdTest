local Vector2 = require("Vector2");
local battlefield = require("battlefield");

local battlefieldDrawer = {};

local ValueColor = {
  [0] = {255, 255, 255},
  [1] = {128, 64, 0},
};

local MouseRadius = 2;

local function boxCircleIntersect(c, h, p, r)
  local v = Vector2.abs(Vector2.sub(p, c));
  local u = Vector2.sub(v, h);
  u.x = math.max(u.x, 0);
  u.y = math.max(u.y, 0);
  return Vector2.dot(u, u) <= r * r;
end

local function draw_tile(x, y, sizeX, sizeY, offsetX, offsetY, value)
  local padding = 1;
  local minX = x * sizeX + offsetX + padding;
  local minY = y * sizeY + offsetY + padding;
  local sX = sizeX - padding*2;
  local sY = sizeY - padding*2;

  local mousX,mousY = love.mouse.getPosition();
  mousX = mousX - offsetX;
  mousY = mousY - offsetY;
  local c = Vector2.new(x * sizeX + sizeX/2, y * sizeY + sizeY/2);
  local p = Vector2.new(mousX, mousY);
  local h = Vector2.new(sizeX/2, sizeY/2);
  if boxCircleIntersect(c, h, p, MouseRadius) then
    love.graphics.setColor(255,0,0);
    love.graphics.rectangle('fill', minX, minY, sX, sY);
  else
    local color = ValueColor[value]
    color = color or {255, 255, 255}
    love.graphics.setColor(color[1], color[2], color[3]);
    love.graphics.rectangle('fill', minX, minY, sX, sY);
  end

  love.graphics.setColor(255,0,255);
  --love.graphics.rectangle('fill', c.x+offsetX, c.y+offsetY, 2, 2);
  love.graphics.points(c.x+offsetX, c.y+offsetY)
end

function battlefieldDrawer.draw(offsetX, offsetY, field)
  local mousX,mousY = love.mouse.getPosition();
  mousX = mousX - offsetX;
  mousY = mousY - offsetY;

  local rowCount = field.rowCount;
  local colCount = field.colCount;
  local tileSize = field.gridsize;

  local index = battlefield.positionToIndex(field,Vector2.new(mousX,mousY));
  --local mouseGridInfo = field.gridlist[index];
--  local c = Vector2.new((mouseGridInfo.cIndex-1) * tileSize + tileSize/2, (mouseGridInfo.rIndex-1) * tileSize + tileSize/2);
--  local dir = Vector2.sub(Vector2.new(mousX,mousY), c);
--  local a = Vector2.angle(dir);
--  local gridDir = 1;
--  if a >= 45 and a < 135 then gridDir = 1;
--  elseif a >= 135 and a < 225 then gridDir = 3;
--  elseif a >= 225 and a < 315 then gridDir = 4;
--  elseif (a >= 315 and a <= 360) or (a >= 0 and a < 45) then gridDir = 2;
--  end

  for r = 1, rowCount do
    for c = 1, colCount do
      local index = (r-1) * colCount + (c-1);
      local gridInfo = field.gridlist[index];
      draw_tile(c-1, r-1, tileSize, tileSize, offsetX, offsetY, gridInfo.value);
    end
  end
  
--  local mr,mc = battlefield.indexToCoordinate(field, index);
--  local indexs = battlefield.getAroundGridIndexs(field, mr, mc, 4, gridDir, shapeType);
--  --vd(indexs);
--  for k, index in pairs(indexs) do
--    local gridInfo = field.gridlist[index];
--    if gridInfo then
--      local c = Vector2.new((gridInfo.cIndex-1) * tileSize + tileSize/2, (gridInfo.rIndex-1) * tileSize + tileSize/2);
--      draw_tile(gridInfo.cIndex-1, gridInfo.rIndex-1, tileSize, tileSize, offsetX, offsetY, gridInfo.value);
--      --love.graphics.print(tostring(k), c.x+offsetX-5, c.y+offsetY-5);
--    end
--  end

--  love.graphics.setColor(0, 0, 255, 100);
--  love.graphics.line(mousX+offsetX, mousY+offsetX, c.x+offsetX, c.y+offsetX);
  
  love.graphics.setColor(0, 255, 0, 100);
  love.graphics.circle("fill", mousX+offsetX, mousY+offsetY, MouseRadius, 20);
end

return battlefieldDrawer;