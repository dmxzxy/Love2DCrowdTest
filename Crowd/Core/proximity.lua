local proximity = {
  pool = {},
};

function proximity.clear()
  for k,v in pairs(proximity.pool) do
    proximity.pool[k] = nil;
  end
end

function proximity.addItem(idx, minx, miny, maxx, maxy)
  local newItem = {
    x = (minx + maxx)/2,
    y = (miny + maxy)/2,
    idx = idx,
  }
  table.insert(proximity.pool, newItem)
end

function proximity.queryItems(minx, miny, maxx, maxy, idxs, maxIdxs)
  local n = 0;
  idxs = idxs or {};

  for k,v in pairs(proximity.pool) do
    local item = proximity.pool[k];
    if item.x >= minx and item.x <= maxx 
      and item.y >= miny and item.y <= maxy then
      --
      if n <= maxIdxs then
        idxs[n+1] = item.idx;
        n = n + 1;
      end
    end
  end

  return n;
end

return proximity;