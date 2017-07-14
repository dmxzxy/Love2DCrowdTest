require("class");
require("Define");
require("RedPointMgr");
require("Panel");

function main()
	local panel1 = Panel.new(RedPointType.RedPoint_Type_1);
	panel1:pressButton();
	panel1:destroy();
	
	local panel2 = Panel.new(RedPointType.RedPoint_Type_2);
	panel2:pressButton();
	panel2:destroy();
end

main();