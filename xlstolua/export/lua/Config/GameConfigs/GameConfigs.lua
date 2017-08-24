GameConfigs = {}
skill_tripleCards_effect = require "Config.GameConfig.skill_tripleCards_effect"
function skill_tripleCards_effect.get(id)
  return skill_tripleCards_effect["items"][tostring(id)];
end
GameConfigs.skill_tripleCards_effect = skill_tripleCards_effect
system_beginBattlePosition = require "Config.GameConfig.system_beginBattlePosition"
function system_beginBattlePosition.get(id)
  return system_beginBattlePosition["items"][tostring(id)];
end
GameConfigs.system_beginBattlePosition = system_beginBattlePosition
system_config = require "Config.GameConfig.system_config"
function system_config.get(id)
  return system_config["items"][tostring(id)];
end
GameConfigs.system_config = system_config
