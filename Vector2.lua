local Vector2 = {};

function Vector2.new(_x, _y)
  local x = _x or 0;
  local y = _y or 0;
  local vec2 = {
    x = x,
    y = y,
  };
  return vec2;
end

function Vector2.set(vec, x, y)
  vec.x = x;
  vec.y = y;
end

function Vector2.add(vec1, vec2)
  local x = vec1.x + vec2.x;
  local y = vec1.y + vec2.y;
  return Vector2.new(x, y);
end

function Vector2.sub(vec1, vec2)
  local x = vec1.x - vec2.x;
  local y = vec1.y - vec2.y;
  return Vector2.new(x, y);
end

function Vector2.mul(vec, num)
  local x = vec.x * num;
  local y = vec.y * num;
  return Vector2.new(x, y);
end

function Vector2.div(vec, num)
  local x = vec.x/num;
  local y = vec.y/num;
  return Vector2.new(x,y);
end

function Vector2.cross(vec1, vec2)
  return vec1.x*vec2.y-vec1.y*vec2.x;
end

function Vector2.dot(vec1, vec2)
  return vec1.x*vec2.x + vec1.y*vec2.y;
end

function Vector2.scale(vec, s)
  vec.x = vec.x*s;
  vec.y = vec.y*s;
  return vec;
end

--function Vector2.angle(vec1, vec2)
--  return math.deg( math.atan2(vec2.y-vec1.y, vec2.x-vec1.x) );
--end

function Vector2.angle(vec1)
  local angle = math.deg(math.atan2(vec1.y, vec1.x));
  if angle < 0 then
    angle = angle + 360;
  end
  return angle;
end

function Vector2.angleBetween(vec1, vec2)
  local angle1 = Vector2.angle(vec1)
  local angle2 = Vector2.angle(vec2)
  local angle = angle1 - angle2;
--  if angle < 0 then
--    angle = angle + 360;
--  end
  return angle;
end

function Vector2.clone(vec)
  return Vector2.new(vec.x, vec.y);
end

function Vector2.copy(vec1, vec2)
  vec1.x = vec2.x;
  vec1.y = vec2.y;
  return vec1;
end

function Vector2.magnitude(vec)
  return math.sqrt(vec.x*vec.x + vec.y*vec.y)
end

function Vector2.sqrtMagnitude(vec)
  return vec.x*vec.x + vec.y*vec.y;
end

function Vector2.normalized(vec)
  local m = Vector2.magnitude(vec);
  local x = vec.x/m;
  local y = vec.y/m;
  return Vector2.new(x,y);
end

function Vector2.normalize(vec)
  local m = Vector2.magnitude(vec);
  vec.x = vec.x/m;
  vec.y = vec.y/m;
  return vec;
end

function Vector2.distance(vec1, vec2)
  local diffX = vec1.x - vec2.x;
  local diffY = vec1.y - vec2.y;
  return math.sqrt(diffX*diffX + diffY*diffY);
end

function Vector2.distanceSquared(vec1, vec2)
  local diffX = vec1.x - vec2.x;
  local diffY = vec1.y - vec2.y;
  return diffX*diffX + diffY*diffY;
end

function Vector2.lerp(vec1, vec2, t)
  local t1 = 1 - t;
  local x = vec1.x*t1+vec2.x*t;
  local y = vec1.y*t1+vec2.y*t;
  return Vector2.new(x, y);
end

function Vector2.abs(vec)
  vec.x = math.abs(vec.x);
  vec.y = math.abs(vec.y);
  return vec;
end

function Vector2.tostring(vec)
  local str = "Vector2 ("..vec.x..","..vec.y..")";
  return str;
end

return Vector2;