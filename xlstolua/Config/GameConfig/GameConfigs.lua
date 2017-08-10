GameConfigs = {}
item = require "Config.GameConfig.item"
function item.get(id)
  return item["items"][tostring(id)];
end
GameConfigs.item = item
