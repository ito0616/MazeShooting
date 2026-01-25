import pygame
from settings import *
import os


from sprites import Jellyfish, Obstacle, Seaweed, Sunfish, Turtle, PlasticWaste, make_transparent
import random

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "title" # title, playing, game_over
        self.max_stage = 5  # ステージ数

        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.stage = 1
        
        # アセットの読み込み
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        
        # タイトル画像（クラゲ）
        self.title_image = pygame.image.load(os.path.join(assets_dir, "jellyfish_normal.png")).convert_alpha()
        self.title_image = pygame.transform.scale(self.title_image, (200, 200))
        # 白背景を透過
        self.title_image = make_transparent(self.title_image)
        
        # 背景画像
        self.bg_images = {}
        self.bg_images[1] = pygame.image.load(os.path.join(assets_dir, "bg_natural_ocean.jpg")).convert()
        self.bg_images[1] = pygame.transform.scale(self.bg_images[1], (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.bg_images[2] = pygame.image.load(os.path.join(assets_dir, "sea3.jpg")).convert()
        self.bg_images[2] = pygame.transform.scale(self.bg_images[2], (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.bg_images[3] = pygame.image.load(os.path.join(assets_dir, "sea1.jpg")).convert()
        self.bg_images[3] = pygame.transform.scale(self.bg_images[3], (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.bg_images[4] = pygame.image.load(os.path.join(assets_dir, "sea2.jpg")).convert()
        self.bg_images[4] = pygame.transform.scale(self.bg_images[4], (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.bg_images[5] = pygame.image.load(os.path.join(assets_dir, "sea4.jpg")).convert()
        self.bg_images[5] = pygame.transform.scale(self.bg_images[5], (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # ゲームオーバー画面用（sea5.jpg）
        self.bg_images['gameover'] = pygame.image.load(os.path.join(assets_dir, "sea5.jpg")).convert()
        self.bg_images['gameover'] = pygame.transform.scale(self.bg_images['gameover'], (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # タイトル用は1と同じ
        self.bg_image = self.bg_images[1]
        
        # 日本語フォント（システムフォントを使用）
        try:
            self.jp_font_large = pygame.font.SysFont("msgothic", 48)
            self.jp_font_medium = pygame.font.SysFont("msgothic", 32)
            self.jp_font_small = pygame.font.SysFont("msgothic", 24)
        except:
            self.jp_font_large = pygame.font.SysFont(None, 48)
            self.jp_font_medium = pygame.font.SysFont(None, 32)
            self.jp_font_small = pygame.font.SysFont(None, 24)
        
        # 障害物画像の読み込み（チュートリアル用）
        self.tutorial_images = {}
        obstacle_files = {
            'seaweed': 'seaweed.png',
            'sunfish': 'sunfish.png',
            'turtle': 'turtle.png',
            'waste': 'plastic_waste.png'
        }
        for name, filename in obstacle_files.items():
            img = pygame.image.load(os.path.join(assets_dir, filename)).convert_alpha()
            img = pygame.transform.scale(img, (150, 150))  # サイズを大きく変更
            img = make_transparent(img)
            self.tutorial_images[name] = img
        
        # チュートリアル会話データ
        self.tutorial_dialogues = [
            {"text": ["僕はクラゲのくらげちゃんだよ。", "今日は空を見に行くんだ。", "でも僕たちクラゲには天敵がいっぱいなんだ..."], "image": None},
            {"text": ["これは海藻だよ。", "ゆらゆら揺れていて当たると痛いんだ。"], "image": "seaweed"},
            {"text": ["これはマンボウ。", "僕を追いかけてくるから気をつけて！"], "image": "sunfish"},
            {"text": ["これはウミガメ。", "大きくてのんびり泳いでいるよ。"], "image": "turtle"},
            {"text": ["これはプラスチックごみ。", "海を汚す悪いやつだ。上から降ってくるよ。"], "image": "waste"},
            {"text": ["スペースキーを長押ししてダッシュ！", "マウスの方向に飛んでいくよ。", "上を目指して頑張ろう！"], "image": None}
        ]
        self.tutorial_index = 0
        self.tutorial_active = False
        self.death_cause = None  # ゲームオーバー時の原因
        
        # 死因別画像の読み込み
        self.death_images = {}
        death_img_files = {
            'seaweed': 'jellyfish_seaweed.jpg',
            'waste': 'jellyfish_plastic_waste.jpg',
            'turtle': 'jellyfish_turtle.jpg',
            'sunfish': 'jellyfish_sunfish.jpg'
        }
        for cause, filename in death_img_files.items():
            path = os.path.join(assets_dir, filename)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (400, 320)) # 画像サイズを大きく
                self.death_images[cause] = make_transparent(img)
            else:
                self.death_images[cause] = None




    def new_game(self):
        # プレイヤー配置（画面下部中央からスタート）
        self.player = Jellyfish((SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        self.all_sprites.add(self.player)
        
        self.last_spawn_time = pygame.time.get_ticks()
        
        # ステージ1はチュートリアル
        if self.stage == 1:
            self.tutorial_active = True
            self.tutorial_index = 0
        else:
            self.tutorial_active = False
            # 初期障害物を配置
            self.spawn_initial_obstacles()

    def spawn_initial_obstacles(self):
        """ステージ開始時に障害物を配置"""
        if self.stage == 1:
            # チュートリアル終了後、全種類1体ずつ配置
            obstacles_to_spawn = ['seaweed', 'sunfish', 'turtle', 'waste']
            y_positions = [200, 300, 400, 350]
            x_positions = [150, 500, 300, 650]
            
            for i, obs_type in enumerate(obstacles_to_spawn):
                pos = (x_positions[i], y_positions[i])
                if obs_type == 'seaweed':
                    obs = Seaweed(pos)
                elif obs_type == 'sunfish':
                    obs = Sunfish(pos, self.player)
                elif obs_type == 'turtle':
                    obs = Turtle(pos)
                elif obs_type == 'waste':
                    obs = PlasticWaste(pos)
                
                self.all_sprites.add(obs)
                self.obstacles.add(obs)
        else:
            # 他のステージは5-6体をランダム配置
            num_obstacles = random.randint(5, 6)
            for _ in range(num_obstacles):
                choice = random.choice(['seaweed', 'sunfish', 'turtle', 'waste'])
                
                if choice == 'seaweed':
                    pos = (random.randint(0, SCREEN_WIDTH), random.randint(100, SCREEN_HEIGHT))
                    obs = Seaweed(pos)
                elif choice == 'sunfish':
                    y = random.randint(50, SCREEN_HEIGHT - 50)
                    if random.random() < 0.5:
                        pos = (-50, y)
                    else:
                        pos = (SCREEN_WIDTH + 50, y)
                    obs = Sunfish(pos, self.player)
                elif choice == 'turtle':
                    pos = (random.randint(100, SCREEN_WIDTH-100), random.randint(100, SCREEN_HEIGHT-100))
                    obs = Turtle(pos)
                elif choice == 'waste':
                    pos = (random.randint(0, SCREEN_WIDTH), -30)
                    obs = PlasticWaste(pos)
                
                self.all_sprites.add(obs)
                self.obstacles.add(obs)

    def spawn_obstacle(self):
        # チュートリアル中は障害物なし
        if self.tutorial_active:
            return
            
        now = pygame.time.get_ticks()
        
        # ステージ1は障害物を1体ずつ（既にいたら出さない）
        if self.stage == 1:
            if len(self.obstacles) >= 1:
                return
            current_spawn_rate = 2000  # ゆっくり出す
        else:
            # ステージが進むほどスポーン間隔を短くする（難易度アップ）
            current_spawn_rate = max(500, OBSTACLE_SPAWN_RATE - (self.stage - 1) * 200)
        
        if now - self.last_spawn_time > current_spawn_rate:
            self.last_spawn_time = now
            choice = random.choice(['seaweed', 'sunfish', 'turtle', 'waste'])
            
            if choice == 'seaweed':
                # 画面下半分から出現
                pos = (random.randint(0, SCREEN_WIDTH), random.randint(SCREEN_HEIGHT // 2, SCREEN_HEIGHT))
                obs = Seaweed(pos)
            elif choice == 'sunfish':
                y = random.randint(50, SCREEN_HEIGHT - 50)
                # 左右どちらかから出現
                if random.random() < 0.5:
                    pos = (-50, y)
                else:
                    pos = (SCREEN_WIDTH + 50, y)
                obs = Sunfish(pos, self.player)  # プレイヤーを渡す
            elif choice == 'turtle':
                pos = (random.randint(100, SCREEN_WIDTH-100), random.randint(100, SCREEN_HEIGHT-100))
                obs = Turtle(pos)
            elif choice == 'waste':
                # 画面上部6割から出現
                pos = (random.randint(0, SCREEN_WIDTH), random.randint(-50, int(SCREEN_HEIGHT * 0.6)))
                obs = PlasticWaste(pos)
            
            self.all_sprites.add(obs)
            self.obstacles.add(obs)

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            
            if self.state == "title":
                self.title_scene()
            elif self.state == "playing":
                if self.tutorial_active:
                    self.tutorial_scene()
                else:
                    self.events()
                    self.update()
                    self.draw()

    def title_scene(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.state = "playing"
                    self.new_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # ボタンのクリック判定
                mouse_pos = pygame.mouse.get_pos()
                if self.start_button_rect.collidepoint(mouse_pos):
                    self.state = "playing"
                    self.new_game()
        
        # 背景画像を描画
        self.screen.blit(self.bg_image, (0, 0))
        
        # 半透明のオーバーレイ（タイトルを見やすく）
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 50, 100))
        self.screen.blit(overlay, (0, 0))
        
        # タイトル文字（日本語）
        title_text = self.jp_font_large.render("海に負けるな！くらげちゃん", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 80))
        self.screen.blit(title_text, title_rect)
        
        # クラゲの画像（透過済み）
        image_rect = self.title_image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
        self.screen.blit(self.title_image, image_rect)
        
        # スタートボタン
        self.start_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 150, 200, 50)
        pygame.draw.rect(self.screen, CYAN, self.start_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, self.start_button_rect, 3, border_radius=10)
        
        button_text = self.jp_font_medium.render("スタート", True, BLACK)
        button_text_rect = button_text.get_rect(center=self.start_button_rect.center)
        self.screen.blit(button_text, button_text_rect)
        
        # 操作説明
        help_text = self.jp_font_small.render("スペース長押し → マウス方向にダッシュ！", True, WHITE)
        help_rect = help_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
        self.screen.blit(help_text, help_rect)
        
        pygame.display.flip()

    def tutorial_scene(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.tutorial_index += 1
                    if self.tutorial_index >= len(self.tutorial_dialogues):
                        self.tutorial_active = False
                        # チュートリアル終了後、障害物を配置
                        self.spawn_initial_obstacles()
        
        # 背景描画
        self.screen.blit(self.bg_images[self.stage], (0, 0))
        self.all_sprites.draw(self.screen)
        
        if self.tutorial_index < len(self.tutorial_dialogues):
            dialogue = self.tutorial_dialogues[self.tutorial_index]
            
            # テキストボックス（画面下部）
            box_height = 150
            box_rect = pygame.Rect(20, SCREEN_HEIGHT - box_height - 20, SCREEN_WIDTH - 40, box_height)
            
            # 半透明の背景
            box_surface = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
            box_surface.fill((0, 0, 50, 200))
            self.screen.blit(box_surface, box_rect.topleft)
            pygame.draw.rect(self.screen, WHITE, box_rect, 3, border_radius=10)
            
            # テキスト表示
            y_offset = box_rect.top + 20
            for line in dialogue["text"]:
                text_surface = self.jp_font_medium.render(line, True, WHITE)
                self.screen.blit(text_surface, (box_rect.left + 20, y_offset))
                y_offset += 35
            
            # 障害物画像表示（画面中央上部）
            if dialogue["image"]:
                img = self.tutorial_images[dialogue["image"]]
                img_rect = img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
                self.screen.blit(img, img_rect)
            else:
                # クラゲ画像を表示
                img_rect = self.title_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
                self.screen.blit(self.title_image, img_rect)
            
            # 進行案内
            hint_text = self.jp_font_small.render("Enter または Space で次へ", True, YELLOW)
            hint_rect = hint_text.get_rect(bottomright=(box_rect.right - 10, box_rect.bottom - 10))
            self.screen.blit(hint_text, hint_rect)
        
        pygame.display.flip()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        self.all_sprites.update()
        self.spawn_obstacle()
        
        # 衝突判定
        if not self.player.invincible:
            hits = pygame.sprite.spritecollide(self.player, self.obstacles, False, pygame.sprite.collide_mask)
            if hits:
                self.player.hp -= 1
                self.player.invincible = True
                self.player.invincible_timer = pygame.time.get_ticks()
                
                # どの障害物に当たったかを記録
                hit_obstacle = hits[0]
                if isinstance(hit_obstacle, Seaweed):
                    self.death_cause = 'seaweed'
                elif isinstance(hit_obstacle, Sunfish):
                    self.death_cause = 'sunfish'
                elif isinstance(hit_obstacle, Turtle):
                    self.death_cause = 'turtle'
                elif isinstance(hit_obstacle, PlasticWaste):
                    self.death_cause = 'waste'
                else:
                    self.death_cause = None
                
                if self.player.hp <= 0:
                    self.game_over_scene()

        # クリア判定（上端到達）
        if self.player.rect.top <= 0:
            if self.stage >= self.max_stage:
                # 全ステージクリア！
                self.game_clear_scene()
            else:
                # ステージクリア画面
                self.stage_clear_scene()

    def draw(self):
        # ステージに応じた背景を使用
        if self.stage in self.bg_images:
            self.screen.blit(self.bg_images[self.stage], (0, 0))
        else:
            # ステージが範囲外の場合は深い青
            self.screen.fill((0, 0, 50))
        
        self.all_sprites.draw(self.screen)
        
        # HUD: HPとチャージ状況
        # HPバー（黒枠に赤の中身）
        pygame.draw.rect(self.screen, BLACK, (10, 10, PLAYER_START_HP * 30, 20))
        pygame.draw.rect(self.screen, RED, (10, 10, self.player.hp * 30, 20))
        pygame.draw.rect(self.screen, WHITE, (10, 10, PLAYER_START_HP * 30, 20), 2)
        
        # チャージバー
        if self.player.is_charging:
            charge_time = pygame.time.get_ticks() - self.player.charge_start_time
            bar_width = min(charge_time // 5, 200)
            pygame.draw.rect(self.screen, YELLOW, (10, 40, bar_width, 10))
            pygame.draw.rect(self.screen, WHITE, (10, 40, 200, 10), 1)

        # ステージ表示
        stage_text = self.jp_font_small.render(f"ステージ {self.stage}", True, WHITE)
        self.screen.blit(stage_text, (SCREEN_WIDTH - 120, 10))
        
        # チュートリアル表示（ステージ1のみ）
        if self.stage == 1:
            tutorial_text = self.jp_font_medium.render("スペースを長押ししてダッシュ！", True, WHITE)
            tutorial_rect = tutorial_text.get_rect(center=(SCREEN_WIDTH//2, 50))
            self.screen.blit(tutorial_text, tutorial_rect)
            
            goal_text = self.jp_font_small.render("↑ 上を目指せ！ ↑", True, YELLOW)
            goal_rect = goal_text.get_rect(center=(SCREEN_WIDTH//2, 80))
            self.screen.blit(goal_text, goal_rect)

        pygame.display.flip()

    def stage_clear_scene(self):
        # ステージクリア画面
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        # 次のステージへ
                        self.stage += 1
                        self.all_sprites.empty()
                        self.obstacles.empty()
                        self.new_game()
                        waiting = False
            
            # 現在のステージの背景を表示
            if self.stage in self.bg_images:
                self.screen.blit(self.bg_images[self.stage], (0, 0))
            
            # 半透明オーバーレイ
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 100, 150))
            self.screen.blit(overlay, (0, 0))
            
            # クリアテキスト
            clear_text = self.jp_font_large.render(f"Stage {self.stage} Clear!", True, YELLOW)
            clear_rect = clear_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(clear_text, clear_rect)
            
            # 次へ案内
            next_text = self.jp_font_medium.render("Enter または Space で次のステージへ", True, WHITE)
            next_rect = next_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            self.screen.blit(next_text, next_rect)
            
            pygame.display.flip()

    def game_over_scene(self):
        # 障害物別のメッセージ
        death_messages = {
            'seaweed': ["うわ～～、絡まって動けないーー！", "海藻に絡まってしまった..."],
            'waste': ["うわっ、なんだこれ！気持ち悪いよー！", "プラスチックごみに襲われてしまった..."],
            'turtle': ["うわっ、やめろー！く、食べるなー、ぐわー！", "ウミガメに食べられてしまった..."],
            'sunfish': ["や、やめろ、やめｒｒｒ、、、", "マンボウに食べられてしまった..."]
        }
        
        # デフォルトメッセージ
        if self.death_cause in death_messages:
            message_lines = death_messages[self.death_cause]
        else:
            message_lines = ["やられてしまった...", ""]
        
        # 第1段階：死因別メッセージ
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        waiting = False
            
            # 背景（現在のステージ）
            if self.stage in self.bg_images:
                self.screen.blit(self.bg_images[self.stage], (0, 0))
            else:
                self.screen.fill(BLACK)
            
            self.all_sprites.draw(self.screen)
            
            # 専用画像を表示
            if self.death_cause in self.death_images and self.death_images[self.death_cause]:
                target_img = self.death_images[self.death_cause]
                # 画像を大きく表示（400x320）
                img_rect = target_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
                self.screen.blit(target_img, img_rect)
            else:
                # 画像がない場合はタイトル画像を大きく表示
                target_img = pygame.transform.scale(self.title_image, (300, 300))
                img_rect = target_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
                self.screen.blit(target_img, img_rect)
            
            # テキストボックス
            box_height = 120
            box_rect = pygame.Rect(20, SCREEN_HEIGHT - box_height - 20, SCREEN_WIDTH - 40, box_height)
            box_surface = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
            box_surface.fill((100, 0, 0, 200))  # 赤っぽい
            self.screen.blit(box_surface, box_rect.topleft)
            pygame.draw.rect(self.screen, RED, box_rect, 3, border_radius=10)
            
            # メッセージ表示
            y_offset = box_rect.top + 20
            for line in message_lines:
                if line:
                    text_surface = self.jp_font_medium.render(line, True, WHITE)
                    self.screen.blit(text_surface, (box_rect.left + 20, y_offset))
                    y_offset += 35
            
            hint_text = self.jp_font_small.render("Enter または Space で次へ", True, YELLOW)
            hint_rect = hint_text.get_rect(bottomright=(box_rect.right - 10, box_rect.bottom - 10))
            self.screen.blit(hint_text, hint_rect)
            
            pygame.display.flip()
        
        # 第2段階：ゲームオーバー表示
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # タイトル画面に戻る
                        self.all_sprites.empty()
                        self.obstacles.empty()
                        self.stage = 1
                        self.state = "title"
                        waiting = False
                    if event.key == pygame.K_r:
                        # リスタート
                        self.all_sprites.empty()
                        self.obstacles.empty()
                        if self.stage == 1:
                            # ステージ1で死んだ場合はタイトルへ
                            self.stage = 1
                            self.state = "title"
                        else:
                            # ステージ2からやり直す
                            self.stage = 2
                            self.new_game()
                        waiting = False
                    if event.key == pygame.K_q:
                        self.running = False
                        waiting = False
            
            # sea5背景を表示 (ゲームオーバー用)
            if 'gameover' in self.bg_images:
                self.screen.blit(self.bg_images['gameover'], (0, 0))
            else:
                self.screen.fill(BLACK)
            
            # ゲームオーバーテキスト
            text = self.jp_font_large.render("GAME OVER", True, RED)
            rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(text, rect)
            
            # 操作案内
            if self.stage == 1:
                retry_text = self.jp_font_medium.render("Space: タイトルへ | Q: 終了", True, WHITE)
            else:
                retry_text = self.jp_font_medium.render("Rを押すとリスタート | Space: タイトルへ", True, WHITE)
            retry_rect = retry_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            self.screen.blit(retry_text, retry_rect)
            
            pygame.display.flip()

    def game_clear_scene(self):
        # ゲームクリア画面（2段階）
        # 第1段階：空を見た感動
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        waiting = False
            
            # sea4背景を表示
            self.screen.blit(self.bg_images[5], (0, 0))
            
            # テキストボックス
            box_height = 100
            box_rect = pygame.Rect(20, SCREEN_HEIGHT - box_height - 20, SCREEN_WIDTH - 40, box_height)
            box_surface = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
            box_surface.fill((0, 0, 50, 200))
            self.screen.blit(box_surface, box_rect.topleft)
            pygame.draw.rect(self.screen, WHITE, box_rect, 3, border_radius=10)
            
            # テキスト
            text_surface = self.jp_font_medium.render("うわー、すごい！これが空か～！", True, WHITE)
            self.screen.blit(text_surface, (box_rect.left + 20, box_rect.top + 20))
            
            hint_text = self.jp_font_small.render("Enter または Space で次へ", True, YELLOW)
            hint_rect = hint_text.get_rect(bottomright=(box_rect.right - 10, box_rect.bottom - 10))
            self.screen.blit(hint_text, hint_rect)
            
            pygame.display.flip()
        
        # 第2段階：ゲームクリア表示
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_t:
                        self.all_sprites.empty()
                        self.obstacles.empty()
                        self.stage = 1
                        self.state = "title"
                        waiting = False
                    if event.key == pygame.K_q:
                        self.running = False
                        waiting = False
            
            # クリア画面の描画
            self.screen.blit(self.bg_images[5], (0, 0))
            
            # 半透明オーバーレイ
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 100, 80))
            self.screen.blit(overlay, (0, 0))
            
            # クリアテキスト
            clear_text = self.jp_font_large.render("GAME CLEAR!", True, YELLOW)
            clear_rect = clear_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(clear_text, clear_rect)
            
            # クラゲ画像
            image_rect = self.title_image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            self.screen.blit(self.title_image, image_rect)
            
            # 操作案内
            help_text = self.jp_font_small.render("T: タイトルへ | Q: 終了", True, WHITE)
            help_rect = help_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
            self.screen.blit(help_text, help_rect)
            
            pygame.display.flip()

