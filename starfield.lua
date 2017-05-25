local rand01 = love.math.random

local starfield = {};

function starfield.new(w,h,speed,maxStars)
  local newfield = {
    w = w,
    h = h,
    x = w/2,
    y = h/2,
    k1 = 5*w,
    k2 = 5*h,
    speed = speed,
    stars = {},
    maxStars = maxStars,
  };

  for i = 1, maxStars do
    newfield.stars[i] = starfield.newStar(newfield);
  end

  return newfield;
end



function starfield.update(field, dt)
  for i=1, field.maxStars do
    local s = field.stars[i]

    --print(i, s.z, s.vz, s.sx, s.sy)
    s.z = s.z - s.vz - field.speed
    s.sx = s.x / s.z * 100 + field.x
    s.sy = s.y / s.z * 100 + field.y
    --print(i, s.z, s.vz, s.sx, s.sy)

    if s.sx < 0 or s.sx > field.w or
     s.sy < 0 or s.sy > field.h or
     s.sx == field.x and s.sy == field.y or
     s.z < 1 or s.z > 1000 then
      starfield.resetStar(field, s)
    end
  end
end

function starfield.newStar(field)
  local newStar = {
    x = 0,
    y = 0,
    z = 0,
    vz = 0,
    sx = 0,
    sy = 0,
    ox = 0,
    oy = 0,
  };
  starfield.resetStar(field, newStar);
  return newStar;
end

function starfield.resetStar(field, s)
  s.x = field.k1*(rand01() - 0.5);
  s.y = field.k2*(rand01() - 0.5);
  s.z = rand01() * 900 + 100;
  s.vz = rand01() * 5.0 + 0.5;
  s.sx = s.x / s.z * 100 + field.x
  s.sy = s.y / s.z * 100 + field.y
  s.ox = s.sx
  s.oy = s.sy
end

return starfield;