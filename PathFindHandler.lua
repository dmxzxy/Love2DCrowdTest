local priority_queue = require("priority_queue");
local battlefield = require("battlefield");

local PathFindHandler = {
  queue = nil;
};
local this = PathFindHandler;

local function heuristic1(node, goal)
  local dx = math.abs(node.cIndex - goal.cIndex)
  local dy = math.abs(node.rIndex - goal.rIndex)
  local d = 1
  return d * (dx + dy)
end

--因为上一种启发因子 应该最好用在等宽高的cell里面比较好 上一种速度更快 如果宽高一致的话最好用上面这个
local function heuristic2(node, goal)
  local posNode = node.center;
  local posGoal = goal.center;

  local dx = posNode.x - posGoal.x;
  local dy = posNode.y - posGoal.y;
  local d = math.sqrt(dx*dx + dy*dy);
  return d;
end

local function heuristic(node, goal)
  if heuristicChoose then
    return heuristic2(node, goal)
  else
    return heuristic1(node, goal)
  end   
end


--启发式A*寻路(启发因子--到目标点的距离)
local function doFind(startpos, goalpos, field)
  local starting_node = battlefield.getGridByPosition(field,startpos);
  local goal_node = battlefield.getGridByPosition(field,goalpos);

  local closed = {};
  local open = {};
  this.queue = priority_queue.new_queue();

  starting_node.g = 0;
  priority_queue.insert(this.queue, starting_node);
  open[starting_node] = true;

  while priority_queue.get_max(this.queue) ~= goal_node do
    local current = priority_queue.extract_max(this.queue);
    if current == nil then
      print("current is empty")
      return nil;
    end
    closed[current] = true;
    open[current] = false;

    local nbors = battlefield.getGridNborsByIndex(field,current.index);
    if nbors == nil then
      print("index = "..current.index.."is empty")
      return nil;
    end
    for k, v in pairs(nbors) do
      local neighbour = battlefield.getGridByIndex(field,v.index);
      local cost = current.g + v.cost;
      if open[neighbour] == true and cost < neighbour.g then
        open[neighbour] = false;
        priority_queue.remove(this.queue,neighbour);
      end
      if closed[neighbour] == true and cost < neighbour.g then
        closed[neighbour] = false;
      end
      if not closed[neighbour] and not open[neighbour] then
        neighbour.g = cost;
        open[neighbour] = true;
        priority_queue.remove(this.queue,neighbour);
        neighbour.f = neighbour.g + heuristic(neighbour, goal_node)
        priority_queue.insert(this.queue,neighbour)
        neighbour.parent = current
      end
    end
  end

  local path = {};
  local current = goal_node;
  local i = 1;
  while current ~= starting_node do
    path[i] = current;
    current = current.parent;
    i = i+1;
  end
  path[i] = current;
  return path
end

local function clearPathFindingVariable(collisionData)
  for _, node in pairs(collisionData.gridlist) do
    node.g = nil;
    node.f = nil;
    node.parent = nil;
  end
  priority_queue.destroy(this.queue);
  this.queue = nil;
end

function PathFindHandler.find(startpos,goalpos,collisionData)
  local path = doFind(startpos,goalpos,collisionData);
  clearPathFindingVariable(collisionData);
  return path;
end


return PathFindHandler;