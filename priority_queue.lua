local priority_queue = {};

local this = priority_queue;

function priority_queue.new_queue()
  local queue = {};
  queue.heap_size = 0;
  return queue
end

function priority_queue.siftdown(queue, i)
  if i > 0 and i <= queue.heap_size then
    local n = queue[i]
    local bigger = 1;
    if this.left(i) <= queue.heap_size and queue[this.left(i)].f < n.f then
      bigger = this.left(i)
    else
      bigger = i
    end
    if this.right(i) <= queue.heap_size and queue[this.right(i)].f < queue[bigger].f then
      bigger = this.right(i)
    end
    if bigger ~= i then
      this.swap(queue, i, bigger)
      this.siftdown(queue, bigger)
    end
  end
end

function priority_queue.siftup(queue, i)
  if i > queue.heap_size then
    return
  end
  local s1 = queue[i];
  while i > 1 and s1.f < queue[this.parent(i)].f do
    queue[i] = queue[this.parent(i)]
    queue[i].heap_index = i
    i = this.parent(i)
  end
  queue[i] = s1
  queue[i].heap_index = i
end

function priority_queue.build_heap(queue)
  for i=queue.heap_size/2, 1, -1 do
    this.siftdown(queue, i)
  end
end

function priority_queue.heap_sort(queue)
  this.build_heap(queue)
  local n = queue.heap_size
  while queue.heap_size >= 2 do
    this.swap(queue, queue.heap_size, 1)
    queue.heap_size = queue.heap_size - 1
    this.siftdown(queue, 1)
  end
  local i = 1
  local j = n
  queue.heap_size = n
  while i < j do
    this.swap(queue, i, j);
    i = i + 1;
    j = j - 1;
  end
end

function priority_queue.extract_max(queue)
  if queue.heap_size < 1 then
    return nil
  end
  local max = queue[1]
  max.heap_index = nil
  queue[1] = queue[queue.heap_size]
  queue[1].heap_index = 1
  queue[queue.heap_size] = nil
  queue.heap_size = queue.heap_size-1
  if queue.heap_size ~= 0 then
    this.siftdown(queue, 1)
  end
  return max
end

function priority_queue.get_max(queue)
  if queue.heap_size < 1 then
    return nil
  end
  return queue[1]
end

function priority_queue.insert(queue, node)
  queue.heap_size = queue.heap_size+1;
  local i = queue.heap_size;
  queue[i] = node;
  node.heap_index = i;
  this.siftup(queue, i);
end

function priority_queue.swap(queue, i, j)
  if i > 0 and j > 0 and i <= queue.heap_size and j <= queue.heap_size then
    queue[i], queue[j] = queue[j], queue[i]
    queue[i].heap_index, queue[j].heap_index = i, j
  end
end

function priority_queue.remove(queue, node)
  local index = node.heap_index
  if not index or not queue[index] then
    return
  end
  if index == queue.heap_size then
    queue[index] = nil
    queue.heap_size = queue.heap_size - 1
  else
    queue[index] = queue[queue.heap_size]
    queue[index].heap_index = index
    queue[queue.heap_size] = nil
    queue.heap_size = queue.heap_size - 1
    node.heap_index = nil
    if index == 1 then
      this.siftdown(queue, index)
    elseif queue[index].f < queue[this.parent(index)].f then
      this.siftup(queue, index)
    elseif index ~= queue.heap_size then
      if this.right(index) <= queue.heap_size and queue[index].f > queue[this.right(index)].f then
        this.siftdown(queue, index)
      elseif this.left(index) <= queue.heap_size and queue[index].f > queue[this.left(index)].f then
        this.siftdown(queue, index)
      end
    end
  end
end

function priority_queue.left(i)
  return i*2
end

function priority_queue.right(i)
  return i*2+1
end

function priority_queue.parent(i)
  return (i/2) - (i/2)%1;
end

function priority_queue.destroy(queue)
  if queue == nil then
    return;
  end

  queue.heap_size = nil;
  for key, var in pairs(queue) do
    var.heap_index = nil;
  end
end

return priority_queue;
