local Point24Core = {}

local operators = {
  add = function(l, r)
    return l + r
  end,
  sub = function(l, r)
    return l - r
  end,
  mul = function(l, r)
    return l * r
  end,
  div = function(l, r)
    return l / r
  end,
  rsub = function(l, r)
    return r - l
  end,
  rdiv = function(l, r)
    return r / l
  end
}

local operatorTranslators = {
  add = function(strl, strr)
    if string.len(strl) > 2 then strl = string.format("(%s)", strl) end
    if string.len(strr) > 2 then strr = string.format("(%s)", strr) end
    return string.format("%s + %s", strl, strr)
  end,
  sub = function(strl, strr)
    if string.len(strl) > 2 then strl = string.format("(%s)", strl) end
    if string.len(strr) > 2 then strr = string.format("(%s)", strr) end
    return string.format("%s - %s", strl, strr)
  end,
  mul = function(strl, strr)
    if string.len(strl) > 2 then strl = string.format("(%s)", strl) end
    if string.len(strr) > 2 then strr = string.format("(%s)", strr) end
    return string.format("%s * %s", strl, strr)
  end,
  div = function(strl, strr)
    if string.len(strl) > 2 then strl = string.format("(%s)", strl) end
    if string.len(strr) > 2 then strr = string.format("(%s)", strr) end
    return string.format("%s / %s", strl, strr)
  end,
  rsub = function(strl, strr)
    if string.len(strl) > 2 then strl = string.format("(%s)", strl) end
    if string.len(strr) > 2 then strr = string.format("(%s)", strr) end
    return string.format("%s - %s", strr, strl)
  end,
  rdiv = function(strl, strr)
    if string.len(strl) > 2 then strl = string.format("(%s)", strl) end
    if string.len(strr) > 2 then strr = string.format("(%s)", strr) end
    return string.format("%s / %s", strr, strl)
  end
}


local Calculator_way1 = {}

Calculator_way1.getVaild = function(set)
  if #set < 2 then
    if set[1] == 24 then
      return true
    else
      return false
    end
  end
  
  for i = 1, #set do
    for j = i+1, #set do
      for k, op in pairs(operators) do
        local newSet = {op(set[i], set[j])}
        for index, value in ipairs(set) do
          if index ~= i and index ~= j then
            table.insert(newSet, value)
          end
        end
        if Calculator_way1.getVaild(newSet) then
          return true
        end
      end
    end
  end
  return false
end

Calculator_way1.getSolutions = function(set, solutions)
  if #set < 2 then
    if set[1][1] == 24 then
      table.insert(solutions, set[1][2])
      return true
    end
    return false
  end
  
  for i = 1, #set do
    for j = i+1, #set do
      for k, op in pairs(operators) do
        local trans = operatorTranslators[k]
        local newSet = {{op(set[i][1], set[j][1]), trans(set[i][2], set[j][2])}}
        for index, value in ipairs(set) do
          if index ~= i and index ~= j then
            table.insert(newSet, {set[i][1], set[i][2]})
          end
        end
        Calculator_way1.getSolutions(newSet, solutions)
      end
    end
  end
  return #solutions > 0
end

function Point24Core.newCalculator()
  return function(set, solutions)
    local buildSet = {}
    for i = 1, #set do
      buildSet[i] = { set[i], tostring(set[i]) }
    end
    return Calculator_way1.getSolutions(buildSet, solutions)
  end
end

function Point24Core.newVaildChecker()
  return function(set)
    return Calculator_way1.getVaild(set)
  end  
end


return Point24Core