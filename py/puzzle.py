import pygame
from pygame.locals import *
from map import *
from support import draw_text

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

SCR_RECT = Rect(0, 0, disp_w, disp_h) # 画面サイズ

# PlayerCharacter クラスの定義 ==========================================================================================================================================

class PlayerCharacter:

    # コンストラクタ
    def __init__(self, init_pos, img_path):
        self.pos = pygame.Vector2(init_pos) # 自キャラ位置
        self.size = pygame.Vector2(48, 48)  # 自キャラサイズ (48×48)
        self.dir = 0                    # 自キャラ向き (下向き)
        img_raw = pygame.image.load(img_path)
        self.__img_arr = []
        for i in range(4):
            self.__img_arr.append([])
            for j in range(3):
                p = pygame.Vector2(32*j, 32*i)
                tmp = img_raw.subsurface(pygame.Rect(p, (32, 32)))
                tmp = pygame.transform.scale(tmp, self.size)
                self.__img_arr[i].append(tmp)
            self.__img_arr[i].append(self.__img_arr[i][1])

    def turn_to(self, dir):
        self.dir = dir
    
    def move_to(self, vec):
        self.pos += vec

    def get_dp(self):
        return self.pos*48
    
    def get_img(self, frame):
        return self.__img_arr[self.dir][frame//12%4]
    
# =======================================================================================================================================================================


# 画像の読み込み
def load_img(filename, colorkey=None):
    img = pygame.image.load(filename).convert()
    if (filename != "./data/img/tiles/floor.png") or (filename != "./data/img/tiles/wall.png"):
        colorkey = (255, 255, 255)
        img.set_colorkey(colorkey, RLEACCEL)
    return img

def main():

    # 初期化処理
    pygame.init()
    pygame.display.set_caption('音をつたえるあかりちゃん')
    screen = pygame.display.set_mode(SCR_RECT.size) # ディスプレイの大きさ
    
    Map.imgs[0]  = load_img("./data/img/tiles/floor.png")          # 床
    Map.imgs[1]  = load_img("./data/img/tiles/wall.png")           # 壁
    Map.imgs[2]  = load_img("./data/img/tiles/shutter_close.png")  # 障害物(閉)
    Map.imgs[3]  = load_img("./data/img/tiles/shutter_open.png")   # 障害物(開)
    Map.imgs[4]  = load_img("./data/img/tiles/red_note.png")       # 赤音符
    Map.imgs[5]  = load_img("./data/img/tiles/red_switch.png")     # 赤スイッチ
    Map.imgs[6]  = load_img("./data/img/tiles/blue_note.png")      # 青音符
    Map.imgs[7]  = load_img("./data/img/tiles/blue_switch.png")    # 青スイッチ
    Map.imgs[8]  = load_img("./data/img/tiles/purple_note.png")    # 紫音符
    Map.imgs[9]  = load_img("./data/img/tiles/purple_switch.png")  # 紫スイッチ
    Map.imgs[10] = load_img("./data/img/tiles/goal_inactive.png")  # ゴール(off)
    Map.imgs[11] = load_img("./data/img/tiles/goal_active.png")    # ゴール(on)
    Map.imgs[12] = load_img("./data/img/tiles/shutter_red.png")    # 障害物(開)+赤音符
    Map.imgs[13] = load_img("./data/img/tiles/shutter_blue.png")   # 障害物(開)+青音符
    Map.imgs[14] = load_img("./data/img/tiles/shutter_purple.png") # 障害物(開)+紫音符
    Map.imgs[15] = load_img("./data/img/tiles/background.png")     # 字幕の背景
    map = Map()

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 15)
    frame = 0
    switch_counter = 0 # スイッチに音符が何個乗ったか
    notes_counter = 0  # スイッチ(音符)の個数はいくつか 
    shutter_notes = 0  # 柵音符がいくつあるか
    exit_flag = False
    exit_code = '000'
    Stageclear = False

    # 自キャラ移動関連のパラメータ設定
    cmd_move = -1 # 移動コマンドの管理変数
    m_vec = [
        pygame.Vector2(0, 1),  # 0: 下移動
        pygame.Vector2(-1, 0), # 1: 左移動
        pygame.Vector2(1, 0),  # 2: 右移動
        pygame.Vector2(0, -1)  # 3: 上移動
    ]

    # 自キャラの各ステージの開始座標
    init_pos_list = [[2,  8],
                     [2,  8],
                     [2,  8],
                     [2,  8],
                     [2,  8],
                     [2,  2],
                     [2,  8],
                     [7,  8],
                     [13, 2],
                     [2,  2],
                     [7,  8]]
    init_pos = (init_pos_list[0+map.area_count][0], init_pos_list[0+map.area_count][1])

    # 自キャラの生成・初期化
    akari = PlayerCharacter((init_pos), './data/img/pictSQ_Akari.png')

    # ゲームループ ======================================================================================================================================================
    while not exit_flag:

        # マップ数を同期
        area_checker = map.area_count

        # 背景描画
        screen.fill(CREAM)

        # マップ描画
        map.draw(screen)

        # 操作方法を画面下部に常に表示
        draw_text(screen, 'WASDキー：移動  Rキー：最初から', disp_w//2, disp_h//2 + 265, 25, WHITE)

        # 説明文の表示
        if (map.area_count == 0):
            draw_text(screen, 'ルールその１：旗に触れるとゴール！', disp_w//2, disp_h//2 - 100, 30, WHITE)
        elif (map.area_count == 1):
            draw_text(screen, 'ルールその２：音符を押して全部の音符を', disp_w//2 - 20, disp_h//2 - 100, 30, WHITE)
            draw_text(screen, 'スイッチに乗せるとゴールが開くよ！', disp_w//2 + 40, disp_h//2 - 70, 30, WHITE)
        elif (map.area_count == 2):
            draw_text(screen, 'ルールその３：スイッチを起動すると', disp_w//2 - 30, disp_h//2 - 100, 30, WHITE)
            draw_text(screen, '障害物が開閉するよ！', disp_w//2 + 84, disp_h//2 - 70, 30, WHITE)
        elif (map.area_count == 3):
            draw_text(screen, 'ルールその４：同じ形の音符しかスイッチに乗らないよ！', disp_w//2, disp_h//2 - 120, 25, WHITE)
            draw_text(screen, 'スイッチに乗せた音符は動かせなくなる！', disp_w//2, disp_h//2 - 90, 25, WHITE)
        elif (map.area_count == 4):
            draw_text(screen, 'ルール説明は以上！いってらっしゃい！', disp_w//2, disp_h//2 - 100, 30, WHITE)

        # Thank you for playing!
        if (map.area_count == 10):
            draw_text(screen, 'Thank you for playing!!', disp_w//2, disp_h//2 - 30, 50, BLACK)
        
        # 音符の数を計測
        if (notes_counter == 0):
            for x in range(map.row):
                for y in range(map.col):
                    if (map.map[x+map.row*map.area_count][y] == 4 or map.map[x+map.row*map.area_count][y] == 6 or map.map[x+map.row*map.area_count][y] == 8):
                        notes_counter += 1
        
        # システムイベントの検出
        cmd_move = -1

        for event in pygame.event.get():
            if (event.type == pygame.QUIT): # ウィンドウの✖の押下
                exit_flag = True      # ゲームを終了させる
                exit_code = '001'

            # キー入力の受け取り処理
            if (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_s):
                    cmd_move = 0
                elif (event.key == pygame.K_a):
                    cmd_move = 1
                elif (event.key == pygame.K_d):
                    cmd_move = 2
                elif (event.key == pygame.K_w):
                    cmd_move = 3

                elif (event.key == pygame.K_SPACE and Stageclear): # ステージクリア後ならば
                    map.area_count += 1                        # Spaceキーで次のステージへ飛ばす
                    Stageclear = False                         # Stageclear を初期化する
                    frame = 0                                  # いろいろ初期化
                    switch_counter = 0
                    notes_counter = 0
                    shutter_notes = 0
                    map.red_note_move = 0
                    map.blue_note_move = 0
                    map.purple_note_move = 0
                    init_pos_list = [[2,  8],
                                     [2,  8],
                                     [2,  8],
                                     [2,  8],
                                     [2,  8],
                                     [2,  2],
                                     [2,  8],
                                     [7,  8],
                                     [13, 2],
                                     [2,  2],
                                     [7,  8]] # 自キャラの各ステージの開始座標
                    init_pos = (init_pos_list[0+map.area_count][0], init_pos_list[0+map.area_count][1])
                    akari = PlayerCharacter(init_pos, './data/img/pictSQ_Akari.png')

                elif (event.key == pygame.K_r): # Rキーの入力
                    if (Stageclear == False):
                        for i in range(map.row):
                            for j in range(map.col):
                                if (map.map[i+map.row*map.area_count][j] != map.init_map[i+map.row*map.area_count][j]):
                                    map.map[i+map.row*map.area_count][j] = map.init_map[i+map.row*map.area_count][j]
                        akari = PlayerCharacter(init_pos, './data/img/pictSQ_Akari.png')
                        frame = 0
                        switch_counter = 0
                        shutter_notes = 0
                        map.red_note_move = 0
                        map.blue_note_move = 0
                        map.purple_note_move = 0

                elif (event.key == pygame.K_ESCAPE): # Escapeキーの入力
                    exit_flag = True           # ゲームを終了させる
                    exit_code = '001'

        # ステージクリア時の描画
        if Stageclear:
            draw_text(screen, 'Stage Clear!!', disp_w//2, disp_h//2, 70, BLACK)
            draw_text(screen, "Press 'space Key' to next stage", disp_w//2, disp_h//2 + 60, 30, BLACK)

        # 移動コマンドの処理
        switch_checker = switch_counter # スイッチに乗っている音符の数を同期させる
        if (cmd_move != -1 and Stageclear == False):
            akari.turn_to(cmd_move)
            af_pos = akari.pos + m_vec[cmd_move] # 移動後の仮座標

            # 音符の移動
            if (map.red_note_move != -1): # 赤音符と重なるならば
                if (cmd_move == 0): # 上から押したとき(＝音符が下に動くとき)
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 4 and map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] == 0): # 音符の下が床であれば
                        map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 4 and map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] == 3): # 音符の下が障害物(開)であれば
                        map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] = 12
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        shutter_notes += 1
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 4 and map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] == 5 and shutter_notes == 0): # 音符の下がスイッチであれば
                        map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        map.red_note_move = -1
                        switch_counter += 1
                elif (cmd_move == 1): # 右から押したとき(＝音符が左に動くとき)
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 4 and map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] == 0): # 音符の左が床であれば
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 4 and map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] == 3): # 音符の左が障害物(開)であれば
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] = 12
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        shutter_notes += 1
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 4 and map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] == 5 and shutter_notes == 0): # 音符の左がスイッチであれば
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        map.red_note_move = -1
                        switch_counter += 1
                elif (cmd_move == 2): # 左から押したとき(＝音符が右に動くとき)
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 4 and map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] == 0): # 音符の右が床であれば
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 4 and map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] == 3): # 音符の左が障害物(開)であれば
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] = 12
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        shutter_notes += 1
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 4 and map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] == 5 and shutter_notes == 0): # 音符の左がスイッチであれば
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        map.red_note_move = -1
                        switch_counter += 1
                elif (cmd_move == 3): # 下から押したとき(＝音符が上に動くとき)
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 4 and map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] == 0): # 音符の上が床であれば
                        map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 4 and map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] == 3): # 音符の左が障害物(開)であれば
                        map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] = 12
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        shutter_notes += 1
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 4 and map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] == 5 and shutter_notes == 0): # 音符の上がスイッチであれば
                        map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        map.red_note_move = -1
                        switch_counter += 1

            if (map.blue_note_move != -1):
                if (cmd_move == 0): # 上から押したとき(＝音符が下に動くとき)
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 6 and map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] == 0): # 音符の下が床であれば
                        map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 6 and map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] == 3): # 音符の下が障害物(開)であれば
                        map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] = 13
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        shutter_notes += 1
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 6 and map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] == 7 and shutter_notes == 0): # 音符の下がスイッチであれば
                        map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        map.blue_note_move = -1
                        switch_counter += 1
                elif (cmd_move == 1): # 右から押したとき(＝音符が左に動くとき)
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 6 and map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] == 0):
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 6 and map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] == 3):
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] = 13
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        shutter_notes += 1
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 6 and map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] == 7 and shutter_notes == 0):
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        map.blue_note_move = -1
                        switch_counter += 1
                elif (cmd_move == 2): # 左から押したとき(＝音符が右に動くとき)
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 6 and map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] == 0):
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 6 and map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] == 3): # 音符の下が障害物(開)であれば
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] = 13
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        shutter_notes += 1
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 6 and map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] == 7 and shutter_notes == 0):
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        map.blue_note_move = -1
                        switch_counter += 1
                elif (cmd_move == 3): # 下から押したとき(＝音符が上に動くとき)
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 6 and map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] == 0):
                        map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 6 and map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] == 3): # 音符の下が障害物(開)であれば
                        map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] = 13
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        shutter_notes += 1
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 6 and map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] == 7 and shutter_notes == 0):
                        map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        map.blue_note_move = -1
                        switch_counter += 1
            
            if (map.purple_note_move != -1):
                if (cmd_move == 0): # 上から押したとき(＝音符が下に動くとき)
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 8 and map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] == 0): # 音符の下が床であれば
                        map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 8 and map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] == 3): # 音符の下が障害物(開)であれば
                        map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] = 14
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        shutter_notes += 1
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 8 and map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] == 9 and shutter_notes == 0):  # 音符の下がスイッチであれば
                        map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        map.purple_note_move = -1
                        switch_counter += 1
                elif (cmd_move == 1): # 右から押したとき(＝音符が左に動くとき)
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 8 and map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] == 0):
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 8 and map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] == 3):
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] = 14
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        shutter_notes += 1
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 8 and map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] == 9 and shutter_notes == 0):
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        map.purple_note_move = -1
                        switch_counter += 1
                elif (cmd_move == 2): # 左から押したとき(＝音符が右に動くとき)
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 8 and map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] == 0):
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 8 and map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] == 3):
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] = 14
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        shutter_notes += 1
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 8 and map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] == 9 and shutter_notes == 0):
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        map.purple_note_move = -1
                        switch_counter += 1
                elif (cmd_move == 3): # 下から押したとき(＝音符が上に動くとき)
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 8 and map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] == 0):
                        map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 8 and map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] == 3):
                        map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] = 14
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        shutter_notes += 1
                    if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 8 and map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] == 9 and shutter_notes == 0):
                        map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] = map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)]
                        map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 0
                        map.purple_note_move = -1
                        switch_counter += 1
                        
            # プレイヤーの移動
            if (Stageclear == False):
                if (0 <= af_pos.x <= map_s.x-1) and (0 <= af_pos.y <= map_s.y-1): # 画面内に収まるならば
                    if (map.goal_possible(af_pos.x, af_pos.y)): # ゴールに到着するならば
                        Stageclear = True

                    # 音符が障害物(開)を通過できるようにする
                    if (cmd_move == 0): # 上から重なったとき
                        if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 12):   # 赤柵音符に重なるならば
                            if (map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] == 0):
                                map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] = 4     # 目の前に赤音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                                shutter_notes -= 1
                            elif (map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] == 3):
                                map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] = 12 # 目の前に赤柵音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3    # 障害物(開)を再描画
                        elif (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 13): # 青柵音符に重なるならば
                            if (map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] == 0):
                                map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] = 6     # 目の前に青音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                                shutter_notes -= 1
                            elif (map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] == 3):
                                map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] = 13     # 目の前に青柵音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                        elif (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 14): # 紫柵音符に重なるならば
                            if (map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] == 0):
                                map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] = 8     # 目の前に紫音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                                shutter_notes -= 1
                            elif (map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] == 3):
                                map.map[int(af_pos.y+map.row*map.area_count)+1][int(af_pos.x)] = 14     # 目の前に紫柵音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                    elif (cmd_move == 1): # 右から重なったとき
                        if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 12):   # 赤柵音符に重なるならば
                            if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] == 0):
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] = 4     # 目の前に赤音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                                shutter_notes -= 1
                            elif (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] == 3):
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] = 12     # 目の前に赤柵音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                        elif (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 13): # 青柵音符に重なるならば
                            if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] == 0):
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] = 6     # 目の前に青音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                                shutter_notes -= 1
                            elif (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] == 3):
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] = 13     # 目の前に青柵音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                        elif (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 14): # 紫柵音符に重なるならば
                            if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] == 0):
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] = 8     # 目の前に紫音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                                shutter_notes -= 1
                            elif (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] == 3):
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)-1] = 14     # 目の前に紫柵音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                    elif (cmd_move == 2): # 左から重なったとき
                        if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 12):   # 赤柵音符に重なるならば
                            if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] == 0):
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] = 4     # 目の前に赤音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                                shutter_notes -= 1
                            elif (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] == 3):
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] = 12     # 目の前に赤柵音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                        elif (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 13): # 青柵音符に重なるならば
                            if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] == 0):
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] = 6     # 目の前に青音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                                shutter_notes -= 1
                            elif (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] == 3):
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] = 13     # 目の前に青柵音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                        elif (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 14): # 紫柵音符に重なるならば
                            if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] == 0):
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] = 8     # 目の前に紫音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                                shutter_notes -= 1
                            elif (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] == 3):
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)+1] = 14     # 目の前に紫柵音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                    elif (cmd_move == 3): # 下から重なったとき
                        if (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 12):   # 赤柵音符に重なるならば
                            if (map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] == 0):
                                map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] = 4     # 目の前に赤音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                                shutter_notes -= 1
                            elif (map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] == 3):
                                map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] = 12     # 目の前に赤柵音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                        elif (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 13): # 青柵音符に重なるならば
                            if (map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] == 0):
                                map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] = 6     # 目の前に青音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                                shutter_notes -= 1
                            elif (map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] == 3):
                                map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] = 13     # 目の前に青柵音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                        elif (map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] == 14): # 紫柵音符に重なるならば
                            if (map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] == 0):
                                map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] = 8     # 目の前に紫音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                                shutter_notes -= 1
                            elif (map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] == 3):
                                map.map[int(af_pos.y+map.row*map.area_count)-1][int(af_pos.x)] = 14     # 目の前に紫柵音符を再生成
                                map.map[int(af_pos.y+map.row*map.area_count)][int(af_pos.x)] = 3       # 障害物(開)を再描画
                    
                    # プレイヤーの移動処理
                    if (map.is_movable(af_pos.x, af_pos.y)): # 壁、柵、音符、柵音符に重ならないならば
                        akari.move_to(m_vec[cmd_move]) # キャラ座標を実際に更新


        # 柵の開閉の処理
        for x in range(map.row):
            for y in range(map.col):
                if (switch_checker != switch_counter): # 新たにスイッチが押されたら
                    if (map.map[x+map.row*map.area_count][y] == 2):   # 閉じてた柵は開ける
                        map.map[x+map.row*map.area_count][y] = 3
                    elif (map.map[x+map.row*map.area_count][y] == 3): # 開けてた柵は閉じる
                        map.map[x+map.row*map.area_count][y] = 2

        # スイッチに音符がすべて乗ったかを判定
        if (switch_counter == notes_counter): # スイッチに音符がすべて乗ったら
            for x in range(map.row):
                for y in range(map.col):
                    if (map.map[x+map.row*map.area_count][y] == 10):
                        map.map[x+map.row*map.area_count][y] = 11 # ゴールを有効化する

        # エリアチェンジ後ゴールを無効化する
        if (area_checker != map.area_count):
            for i in range(map.row):
                for j in range(map.col):
                    if (map.map[i+map.row*map.area_count][j] != map.init_map[i+map.row*map.area_count][j]):
                        map.map[i+map.row*map.area_count][j] = map.init_map[i+map.row*map.area_count][j]
        
        # 自キャラの描画
        screen.blit(akari.get_img(frame), akari.get_dp())

        # アニメーション用フレーム
        if (Stageclear == False):
            frame += 1

        # 画面の更新と同期
        pygame.display.update()
        clock.tick(60)

# =======================================================================================================================================================================
            
    pygame.quit()
    return exit_code

if __name__ == "__main__":
    code = main()
    print(f'プログラムを「コード{code}」で終了しました')