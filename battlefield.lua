local Vector2 = require("Vector2");
local rand01 = love.math.random

local battlefield = {};
local this = battlefield;

function battlefield.new(width, height, gridsize)
  local rowCount = height/gridsize;
  local colCount = width/gridsize;
  local gridlist = {};
  
  local map = {};
  for c = 1, colCount do
    map[c] = {};
    for r = 1, rowCount do
      local value = 1;
      if (rand01() < 0.75) then
        value = 0;
      end
      map[c][r] = value;
    end
  end
  
  local newfield = {
    rowCount = rowCount,
    colCount = colCount,
    width = width,
    height = height,
    gridsize = gridsize,
    gridlist = gridlist,
    map = map,
    nborGrids = {},
  };
  
  for r = 1, rowCount do
    for c = 1, colCount do
      local index = (r-1) * colCount + (c-1);
      gridlist[index] = {
        index = index,
        rIndex = r,
        cIndex = c,
        value = map[c][r],
        center = Vector2.new((c-1)*gridsize + gridsize/2, (r-1)*gridsize + gridsize/2),
      };
    end
  end
  this.buildData(newfield);
  return newfield;
end

-- dir tip
--     4
--     |
-- 2 --+-- 3
--     |
--     1

function battlefield.getAroundGridIndexs(field, r, c, size, dir, shapeType)
  local indexs = {};
  
  local dirGrid = {0,1};
  if dir == 1 then
    dirGrid = {0,1};
  elseif dir == 2 then
    dirGrid = {1,0};
  elseif dir == 3 then
    dirGrid = {-1,0};
  elseif dir == 4 then
    dirGrid = {0,-1};
  end
  
  if shapeType == 1 then --方形
    for _r = -size, size do
      for _c = -size, size do
        local tr = r + _r;
        local tc = c + _c;
        local index = this.coordinateToIndex(tr, tc, field);
        table.insert(indexs, index);
      end
    end
  elseif shapeType == 2 then --十字形
    for _r = -size, size do
      for _c = -size, size do
        local tr = r + _r;
        local tc = c + _c;
        if _r == 0 or _c == 0 then
          local index = this.coordinateToIndex(tr, tc, field);
          table.insert(indexs, index);
        end
      end
    end
    
  elseif shapeType == 3 then --圆形
    for _r = -size, size do
      for _c = -size, size do
        local tr = r + _r;
        local tc = c + _c;
        if math.abs(_r) + math.abs(_c) <= size then
          local index = this.coordinateToIndex(tr, tc, field);
          table.insert(indexs, index);
        end
      end
    end
  elseif shapeType == 4 then --米字形
    for _r = -size, size do
      for _c = -size, size do
        local tr = r + _r;
        local tc = c + _c;
        if math.abs(_r) == math.abs(_c) or _r == 0 or _c == 0 then
          local index = this.coordinateToIndex(tr, tc, field);
          table.insert(indexs, index);
        end
      end
    end
  elseif shapeType == 5 then --射线
    for i = 0, size do
      for j = -1, 1 do
        local tr = r + i * dirGrid[2] + j * dirGrid[1];
        local tc = c + i * dirGrid[1] + j * dirGrid[2];
        local index = this.coordinateToIndex(tr, tc, field);
        table.insert(indexs, index);
      end
    end
  elseif shapeType == 6 then --扇形
    for i = 0, size do
      for j = -i, i do
        local tr = r + i * dirGrid[2] + j * dirGrid[1];
        local tc = c + i * dirGrid[1] + j * dirGrid[2];
        local index = this.coordinateToIndex(tr, tc, field);
        table.insert(indexs, index);
      end
    end
  end

  return indexs;
end

function battlefield.indexToCoordinate(field, index)
  local colCount = field.colCount;
  
  local r = math.floor(index/colCount);
  local c = index - r*colCount; 
  return r+1,c+1;
end

function battlefield.coordinateToIndex(r, c, field)
  local colCount = field.colCount;

  local index = (r-1) * colCount + (c-1);
  return index;
end

function battlefield.positionToIndex(field, pos)
  local gridSize = field.gridsize;
  local c = math.floor(pos.x/gridSize);
  local r = math.floor(pos.y/gridSize);

  local index = this.coordinateToIndex(r+1, c+1, field)
  return index;
end

function battlefield.getGridByPosition(field, pos)
  local index = this.positionToIndex(field, pos);
  return this.getGridByIndex(field, index);
end

function battlefield.getGridByIndex(field, index)
  return field.gridlist[index];
end

function battlefield.getGridNborsByIndex(field, index)
  local nborGrids = field.nborGrids;

  local nbors = nborGrids[index];

  return nbors;
end

local function isCollision(r, c, field)
  local rowCount = field.rowCount;
  local colCount = field.colCount;

  if r < 1 or c < 1 or r > rowCount or c > colCount then
    return true;
  end

  local index = this.coordinateToIndex(r,c,field);

  local grid = field.gridlist[index];
  if grid == nil then
    return true;
  end

  if grid ~= nil and grid.value ~= 0 then
    return true;
  end

  return false;
end

local function pushNborGrid(r, c, field)

  if isCollision(r, c, field) then
    return;
  end
  local colCount = field.colCount;
  local index = this.coordinateToIndex(r,c,field);
  field.nborGrids[index] = {};

  --right
  local _r = r + 1;
  local _c = c;
  if not isCollision(_r, _c, field) then
    local _index = this.coordinateToIndex(_r,_c,field);
    table.insert(field.nborGrids[index], {cost = 1,index = _index});
  end

  --left
  _r = r - 1;
  _c = c;
  if not isCollision(_r, _c, field) then
    local _index = this.coordinateToIndex(_r,_c,field);
    table.insert(field.nborGrids[index], {cost = 1,index = _index});
  end

  --top
  _r = r;
  _c = c + 1;
  if not isCollision(_r, _c, field) then
    local _index = this.coordinateToIndex(_r,_c,field);
    table.insert(field.nborGrids[index], {cost = 1,index = _index});
  end

  --bottom
  _r = r;
  _c = c - 1;
  if not isCollision(_r, _c, field) then
    local _index = this.coordinateToIndex(_r,_c,field);
    table.insert(field.nborGrids[index], {cost = 1,index = _index});
  end
end

function battlefield.buildData(field)
  if field == nil then
    return;
  end
  --build nbors grid
  local row = field.rowCount;
  local col = field.colCount;

  --clear
  field.nborGrids = {};

  --set unit data to field

  --build
  for r = 1, row do
    for c = 1, col do
      pushNborGrid(r,c,field);
    end
  end
end

return battlefield;