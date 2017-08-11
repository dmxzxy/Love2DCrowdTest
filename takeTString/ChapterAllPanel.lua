

local ChapterAllPanel = class("ChapterAllPanel",BasePanel);

function ChapterAllPanel:ctor(parentGo,args)
	ChapterAllPanel.super.ctor(self,"ChapterAllPanel","panels_chapter","ChapterAllPanel",parentGo,extra);
  if args then
    self.chapterId = args.chapterId or nil;
  end
  NCenter.add(self,Notification.View.World.Main.Refresh,function(newChapterConfigId)
    log("Notification.View.World.Main.Refresh,newChapterConfigId:"..tostring(newChapterConfigId));
    self.chapterId = newChapterConfigId;
    
    self:onShow();
    local event = GameData.StoryPlot.buildTriggerEvent(StoryPlotTriggerType.Tap_WorldMap_Area);
    event.param1 = newChapterConfigId;
    GameData.StoryPlot.receiveTriggerEvent(event);
  end);
  
  NCenter.add(self,Notification.View.StoryPlot.Main.EnterStory,function(type)
    local goChapterUI = self.goChapterUI;
    goChapterUI:SetActive(false);
  end)
  
  NCenter.add(self,Notification.View.StoryPlot.Main.ExitStory,function()
    local goChapterUI = self.goChapterUI;
    goChapterUI:SetActive(true);
  end)
  
  self.chapterToIndexMap = {};
end

local kTotalChapterCount = 13;

function ChapterAllPanel:onStart()
  ChapterAllPanel.super.onStart(self);
  

  
--  self:initServiceHeader("",function()
--    Navigator.backToMainPage();
--  end,true);
  
  -- 章节表
  local chapterList = {};
  for key, _ in ascByKey(GameConfigs.ChapterHash.items) do
    local chapterConfig = GameConfigs.ChapterHash.get(key); 
    table.insert(chapterList,chapterConfig);    
  end
--  dump(chapterList);
  self.chapterList = chapterList;
  
  local goRoot = self.go;
  self.goRoot = goRoot;
  -- 地区格子
  local goBlocks = self:find("goBlocks");
  self.goBlocks = goBlocks;
  
  local goBlockTips = self:find("goBlockTips");
  self.goBlockTips = goBlockTips;
  
  local goBlockList = ui.pickGroup(goBlocks,"goBlock%d",kTotalChapterCount,function(go,i)
    local imgChosen = ui.pickC(go,"imgChosen","Image");
    imgChosen.enabled = false;
    go.imgChosen = imgChosen;
    local imgBuilding = ui.pickC(go,"imgBuilding","Image");   
    go.imgBuilding = imgBuilding;
    local goLine = ui.pick(go,"goLine");
    goLine:SetActive(false);
    go.goLine = goLine;
    local lb = ui.pickC(goLine,"Text","Text");
    goLine.lb = lb;
    local btn = ui.pickC(go,"btn","Button");
    go.btn = btn;
    local img = ui.pickC(go,"btn","Image");
    img.eventAlphaThreshold = 0.01;
    btn.onClick:AddListener(function()
		snd.normalClick();

      -- 弹窗
      self:onShowZone(i);
    end);
  end);
  self.goBlockList = goBlockList;
  log("初始化 goBlockList:");
--  dump(goBlockList);
  local goBlockTipList = ui.pickGroup(goBlockTips,"goBlock%d",kTotalChapterCount,function(go,i)
    ui.bindChildGameObjects(go);
    go.goLine.lbName.text = _T("未知区域");
    go.goLine:SetActive(false);
  end);
  self.goBlockTipList = goBlockTipList;
  
  local goChapterUI = ui.pick(goRoot,"goChapterUI");
  self.goChapterUI = goChapterUI;
  
  -- 收益按钮
  local btnProfit = ui.pickC(goChapterUI,"btnProfit","Button");
  btnProfit.onClick:AddListener(function()
		snd.normalClick();

    -- 弹窗
    ui.dialog(AllDialogs.ChapterShopIncomeDialogPanel.cls);
  end);
  self.btnProfit = btnProfit;
  -- 返回按钮
  local btnBack = ui.pickC(goChapterUI,"btnBack","Button")
  btnBack.onClick:AddListener(function()
		snd.play(999998);
    -- 返回
    Navigator.backToMainPage();
  end);
  self.btnBack = btnBack;
  -- 上一个按钮
  local btnLast = ui.pickC(goChapterUI,"btnLast","Button")
  btnLast.onClick:AddListener(function()
		snd.normalClick();

    -- 返回
  end);
  self.btnLast = btnLast;
  -- 下一个按钮
  local btnNext = ui.pickC(goChapterUI,"btnNext","Button")
  btnNext.onClick:AddListener(function()
		snd.normalClick();

    -- 返回
  end);
  self.btnNext = btnNext;
  -- 地区list
  local goScrollAreas = ui.pick(goChapterUI,"scrollAreas");
  goScrollAreas.goItems = {};
  
  self.goScrollAreas = goScrollAreas;
  
  local spriteContainerArea = ui.pickC(goRoot,"imgAreaSprites","SpriteContainer");
  self.spriteContainerArea = spriteContainerArea;
  local spriteContainerName = ui.pickC(goRoot,"imgNameSprites","SpriteContainer");
  self.spriteContainerName = spriteContainerName;
  local spriteContainerShop = ui.pickC(goRoot,"imgShopSprites","SpriteContainer");
  self.spriteContainerShop = spriteContainerShop;
  
  self:onShow();   
end

function ChapterAllPanel:onShow()
  local chapterList = self.chapterList;
  local spriteContainer = self.spriteContainerArea;
  
  log("ChapterAllPanel:onShow()======>");
  log(debug.traceback("", 2));
  
  local goBlockList = self.goBlockList;
  dump(goBlockList);
  local goBlockTipList = self.goBlockTipList;
  
  
--  for i, chapterConfig in ipairs(chapterList) do
  -- 设置地图
  for i=1, kTotalChapterCount do
    local goBlock = goBlockList[i];
    goBlock.index = i;
    
    local goBlockTip = goBlockTipList[i];
    local imgBuilding = goBlock.imgBuilding;
    local imgChosen = goBlock.imgChosen;
    local goLine = goBlockTip.goLine;
    local name = _T("未知区域");
    local chapterId = -1;
    local chapterConfig = chapterList[i];
    if chapterConfig then
      name = chapterConfig.name;
      chapterId = chapterConfig.chapterId;    
    else
      -- 未找到配置，用初始值
    end

    local lbName = goLine.lbName;
    lbName.text = _T(name);
    
    self.chapterToIndexMap[chapterId] = i;
    local chapter = GameData.Pve.chapters[chapterId];
    if chapter or GameData.Pve.isChapterUnlock(chapterId) then
--      imgBuilding.enabled = true;
      imgBuilding.color = unity.Color.white;       
    else
--      imgBuilding.enabled = true;
      imgBuilding.color = unity.Color.alphaWhite;
    end
  end
--  self.goBlockList = goBlockList;
--  self.goBlockTipList = goBlockTipList;
  -- 设置右边滚动列表
  local goScrollAreas = self.goScrollAreas;
  ui.setScrollReused(goScrollAreas,chapterList,
    function(go)
      local imgChosen = ui.pickC(go,"imgChosen","Image");
      go.imgChosen = imgChosen;
      imgChosen.enabled = false;
      local imgArea = ui.pickC(go,"imgArea","Image");
      go.imgArea = imgArea;
      local lbName = ui.pickC(go,"lbName","Text");
      go.lbName = lbName;
      local lbNotOpened = ui.pickC(go,"lbNotOpened","Text");
      go.lbNotOpened = lbNotOpened;
      local btn = ui.pickC(go,"","Button");
      btn.onClick:AddListener(function()
  		snd.normalClick();
        -- 弹窗
        local key = go.curKey;
        self:onShowZone(key);
      end);
    end,
    
    function(go,chapterConfig,key)
      -- 显示
      local lbName = go.lbName;
      local imgArea = go.imgArea;
      local lbNotOpened = go.lbNotOpened;
      go.curKey = key;
      lbName.text = _T(chapterConfig.name);
      imgArea.sprite = spriteContainer:Get(key);
      local chapterId = chapterConfig.chapterId;
      local chapter = GameData.Pve.chapters[chapterId];
      if chapter or GameData.Pve.isChapterUnlock(chapterId) then
        imgArea.color = unity.Color.white;       
        lbNotOpened.enabled = false;
      else
        imgArea.color = unity.Color.alphaWhite;
        lbNotOpened.enabled = true;
      end
    end);
    self.curItem = nil;
    
    local chapterId = self.chapterId;
    if chapterId then
      local index = self.chapterToIndexMap[chapterId];
      if index ~= nil then
        self:onShowZone(index);
      end
    end
end

function ChapterAllPanel:onShowZone(index)
  local spriteContainerName = self.spriteContainerName;
  local spriteContainerShop = self.spriteContainerShop;
  local chapterList = self.chapterList;
  local goBlockList = self.goBlockList;
  local goBlockTipList = self.goBlockTipList;
  local goScrollAreas = self.goScrollAreas;
  local goItems = goScrollAreas.goItems;
  local goBlock = goBlockList[index];
  local goBlockTip = goBlockTipList[index];
  local curBlock = self.curBlock;
  local curBlockTip = self.curBlockTip;
  if curBlock ~= nil then
    curBlock.imgChosen.enabled = false;
    curBlock.goLine:SetActive(false);
  end
  if curBlockTip ~= nil then
    curBlockTip.goLine:SetActive(false);
  end
  
  goBlock.imgChosen.enabled = true;
  goBlock.goLine:SetActive(false);
  goBlockTip.goLine:SetActive(true);
  curBlock = goBlock;
  curBlockTip = goBlockTip;
  self.curBlock = curBlock;
  self.curBlockTip = curBlockTip;
  
  local curItem = self.curItem;
  if curItem ~= nil then
    curItem.imgChosen.enabled = false;
  end
  local goItem = goItems[index];
  if goItem then
    goItem.imgChosen.enabled = true;
  end
  self.curItem = goItem;
  -- 弹窗
  local chapterConfig = chapterList[index];

  if chapterConfig then
    local chapter = GameData.Pve.chapters[chapterConfig.chapterId];
    local spriteName = spriteContainerName:Get(index);
    local spriteShop = spriteContainerShop:Get(index);
    local lastDialog = self.lastDialog;
    if lastDialog then
      lastDialog:dismiss();
    end
    if chapter then
      lastDialog = ui.dialog(AllDialogs.ManageChapterDialogPanel.cls,chapterConfig,spriteName,spriteShop);      
    elseif GameData.Pve.isChapterUnlock(chapterConfig.chapterId) then
      lastDialog = ui.dialog(AllDialogs.OpenChapterDialogPanel.cls,chapterConfig.chapterId,spriteName,spriteShop);  
    else
      ui.tips(_T("章节未解锁."));
    end
    if lastDialog then
      lastDialog:setOnDismiss(function(dialog)
        self.lastDialog = nil;
      end);
    end
    self.lastDialog = lastDialog;
  else
    local lastDialog = self.lastDialog;
    if lastDialog then
      lastDialog:dismiss();
    end
  end
  
end

function ChapterAllPanel:onDestroy()
  ChapterAllPanel.super.onDestroy(self);
  local lastDialog = self.lastDialog;
  if lastDialog then
    lastDialog:dismiss();
  end
end

return ChapterAllPanel;