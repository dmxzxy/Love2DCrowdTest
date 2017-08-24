GameConfigs = {}

--system_beginBattlePosition.lua
system_beginBattlePosition.lua = require "Config.GameConfig.system_beginBattlePosition.lua"
function system_beginBattlePosition.lua.get(id)
  return system_beginBattlePosition.lua["items"][tostring(id)];
end
GameConfigs.system_beginBattlePosition.lua = system_beginBattlePosition.lua

--system_config.lua
system_config.lua = require "Config.GameConfig.system_config.lua"
function system_config.lua.get(id)
  return system_config.lua["items"][tostring(id)];
end
GameConfigs.system_config.lua = system_config.lua

--skill_tripleCards_effect.lua
skill_tripleCards_effect.lua = require "Config.GameConfig.skill_tripleCards_effect.lua"
function skill_tripleCards_effect.lua.get(id)
  return skill_tripleCards_effect.lua["items"][tostring(id)];
end
GameConfigs.skill_tripleCards_effect.lua = skill_tripleCards_effect.lua

