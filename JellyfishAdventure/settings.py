import pygame

# 画面設定
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "海流に負けるな！クラゲちゃん"
FPS = 60

# 色定義 (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)      # クラゲの色（仮）
BLUE = (0, 0, 255)        # 海の色
RED = (255, 0, 0)         # ダメージ/敵
GREEN = (0, 255, 0)       # 海藻
YELLOW = (255, 255, 0)    # ダッシュチャージ

# 物理定数
GRAVITY = 0.1             # 重力加速度 (修正: 0.2 -> 0.1)
JELLY_SPEED = 1.0         # 通常移動速度 (修正: 1.5 -> 1.0)
DASH_POWER_MAX = 10       # 最大ダッシュ力 (修正: 12 -> 10)
FRICTION = 0.93           # 摩擦（減衰） (修正: 0.95 -> 0.93)

# ゲーム設定
PLAYER_START_HP = 3
OBSTACLE_SPAWN_RATE = 1500 # ミリ秒
