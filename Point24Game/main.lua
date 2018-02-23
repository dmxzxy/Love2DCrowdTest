
local Point24Core = require("Point24Core")
local poker = {
  {1,'!'}, {1,'@'}, {1,'#'}, {1,'$'}, 
  {2,'!'}, {2,'@'}, {2,'#'}, {2,'$'}, 
  {3,'!'}, {3,'@'}, {3,'#'}, {3,'$'}, 
  {4,'!'}, {4,'@'}, {4,'#'}, {4,'$'}, 
  {5,'!'}, {5,'@'}, {5,'#'}, {5,'$'}, 
  {6,'!'}, {6,'@'}, {6,'#'}, {6,'$'}, 
  {7,'!'}, {7,'@'}, {7,'#'}, {7,'$'}, 
  {8,'!'}, {8,'@'}, {8,'#'}, {8,'$'}, 
  {9,'!'}, {9,'@'}, {9,'#'}, {9,'$'}, 
  {10,'!'}, {10,'@'}, {10,'#'}, {10,'$'}, 
  {11,'!'}, {11,'@'}, {11,'#'}, {11,'$'}, 
  {12,'!'}, {12,'@'}, {12,'#'}, {12,'$'}, 
  {13,'!'}, {13,'@'}, {13,'#'}, {13,'$'}, 
}

local calculatedCount = 0
local totalCount = 0
local vaildCount = 0
local db = {}

local function Combination(data, out, need, start, picked)
  if picked == need then
    out.totalCount = out.totalCount and out.totalCount + 1 or 1
    
    out.result = out.result or {}
    table.insert(out.result, {out[1], out[2], out[3], out[4]})
    return
  end
  
  local _max = #data + 1 - need + picked
  for i = start, _max do
    out[picked+1] = data[i]
    Combination(data, out, need, i + 1, picked + 1)
  end
end

local co = nil
  
function love.load()
  
  local out = {}
  Combination(poker, out, 4, 1, 0)
  print(out.totalCount, #out.result)
  totalCount = out.totalCount
  
  local calculator = Point24Core.newCalculator()
  
  co = coroutine.create(function()
    local start = os.clock()
    for i = 1, #out.result do
      local v = out.result[i]
      local solutions = {}
      local ret = calculator({v[1][1], v[2][1], v[3][1], v[4][1]}, solutions)
      calculatedCount = calculatedCount + 1
      if ret then
        vaildCount = vaildCount + 1
      end
      if os.clock() - start > 1/60 then
        coroutine.yield()
        start = os.clock()
      end
    end
    co = nil
  end)
end

function love.update(dt)
  if co then
    assert(coroutine.resume(co))
  end
  
end

function love.draw()
  local curr = math.floor(100*calculatedCount/totalCount)
  
  love.graphics.setColor(0, 255, 255, 255)
  love.graphics.print('[', 0, 0)
  for i = 1, curr do
    love.graphics.print('=', (i-1)*6 + 6, 0)
  end
  for i = curr + 1, 100 do
    love.graphics.print(' ', (i-1)*6 + 6, 0)
  end
  love.graphics.print(']', 600 + 12, 0)
  
  love.graphics.setColor(0, 255, 0, 255)
  love.graphics.print(curr..'%', 300, 15)
  
  love.graphics.print(calculatedCount..'/'..totalCount..'   '..vaildCount, 0, 40)
  love.graphics.print(love.timer.getFPS(), 0, 80)
end
