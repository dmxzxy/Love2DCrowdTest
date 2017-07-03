
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

local function smoothPath(finder, path)
  local function isCollision(c, r)
    return finder._grid:isWalkableAt(c, r, finder._walkable);
  end

  local num_pts = #path._nodes
  for i = 1, num_pts do
    while true do
      -- Check to see if we can go straight from pt i to pt i + 2.
      local j = i + 2
      if j > #path._nodes then break end
      local posx1, posy1 = path._nodes[i]:getPos();
      local posx2, posy2 = path._nodes[j]:getPos();
      local isOk = path_is_ok(posx1, posy1, posx2, posy2, isCollision);
      if isOk then
        table.remove(path._nodes, j-1);
      else
        break
      end
    end
  end
  return path
end

return function(finder, path)
  return smoothPath(finder, path);
end
