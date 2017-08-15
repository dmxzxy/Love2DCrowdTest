GameConfigs = {}
item = require "Config.GameConfig.item"
function item.get(id)
  return item["items"][tostring(id)];
end
GameConfigs.item = item
script_multlang = require "Config.GameConfig.script_multlang"
function script_multlang.get(id)
  return script_multlang["items"][tostring(id)];
end
GameConfigs.script_multlang = script_multlang
