local starfieldDrawer = {};

function starfieldDrawer.draw(field)
  love.graphics.setLineStyle('smooth');
  for i=1, field.maxStars do
    local s = field.stars[i]
    local  b = 280 - s.z * 0.280
    if b > 255 then b = 255 end
    love.graphics.setColor(b, b, b)
    love.graphics.line(s.sx, s.sy, s.ox, s.oy)

    s.ox = s.sx
    s.oy = s.sy
  end
end

return starfieldDrawer;