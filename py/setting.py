import pygame

# 初期化・グローバル変数
# PlayerCharacter と main の両方から参照する変数
scale_factor = 2
chip_s = int(24*scale_factor)  # マップチップ基本サイズ
map_s = pygame.Vector2(16, 12) # マップの横・縦の配置数
disp_w = int(chip_s*map_s.x)   # ディスプレイの横の大きさ (wide)
disp_h = int(chip_s*map_s.y)   # ディスプレイの縦の大きさ (height)

red_note_move = 0    # 赤スイッチに重なったか
blue_note_move = 0   # 青スイッチに重なったか
purple_note_move = 0 # 紫スイッチに重なったか

# 色を定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CREAM = (255, 255, 220)

SCR_RECT = pygame.Rect(0, 0, disp_w, disp_h) # 画面サイズ