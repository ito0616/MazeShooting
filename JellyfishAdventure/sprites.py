import pygame
import math
from settings import *
import random
import os

def make_transparent(surface, threshold=230):
    """白っぽい背景を透明にする（しきい値以上のRGB値を透明化）"""
    surface = surface.copy()
    width, height = surface.get_size()
    for x in range(width):
        for y in range(height):
            r, g, b, a = surface.get_at((x, y))
            # 白っぽい（R,G,B全てがしきい値以上）なら透明に
            if r >= threshold and g >= threshold and b >= threshold:
                surface.set_at((x, y), (r, g, b, 0))
    return surface

class Jellyfish(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        # 画像ディレクトリの取得
        self.assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        
        # 画像の読み込み（通常時とダメージ時）
        self.image_normal = pygame.image.load(os.path.join(self.assets_dir, "jellyfish_normal.png")).convert_alpha()
        self.image_normal = pygame.transform.scale(self.image_normal, (60, 60))
        self.image_normal = make_transparent(self.image_normal)
        
        self.image_hit = pygame.image.load(os.path.join(self.assets_dir, "jellyfish_hit.png")).convert_alpha()
        self.image_hit = pygame.transform.scale(self.image_hit, (60, 60))
        self.image_hit = make_transparent(self.image_hit)

        # マスクの作成（より正確な当たり判定のため）
        self.mask = pygame.mask.from_surface(self.image_normal)

        self.image = self.image_normal
        self.rect = self.image.get_rect(center=pos)

        # 移動関連
        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)

        # パラメータ
        self.max_hp = PLAYER_START_HP
        self.hp = self.max_hp
        self.speed = JELLY_SPEED
        self.friction = FRICTION
        self.gravity = GRAVITY

        # ダッシュ・無敵関連
        self.is_charging = False
        self.charge_start_time = 0
        self.dash_power = 0
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 1000 # 1秒

    def input(self):
        keys = pygame.key.get_pressed()
        self.acc = pygame.math.Vector2(0, self.gravity) # 常に重力がかかる

        if keys[pygame.K_SPACE]:
            if not self.is_charging:
                self.is_charging = True
                self.charge_start_time = pygame.time.get_ticks()
            
            # チャージ中は落下のみ（移動入力無効）
            # 視覚効果：色が濃くなる
            color_val = max(0, 255 - (pygame.time.get_ticks() - self.charge_start_time) // 5)
            self.image.set_alpha(max(100, color_val)) # 少しずつ暗くなる

        else:
            # ダッシュ発動判定
            if self.is_charging:
                charge_duration = pygame.time.get_ticks() - self.charge_start_time
                # 最低300ms以上チャージしないとダッシュしない
                if charge_duration >= 300:
                    self.dash(charge_duration)
                self.is_charging = False
                self.image.set_alpha(255) # 元に戻す
            
            # 矢印キーでの移動は無効化（ダッシュのみで移動）


    def dash(self, duration):
        # チャージ時間に応じてパワー決定（最大値制限）
        power = min(duration / 50, DASH_POWER_MAX) # 500msでパワー10
        if power < 3: power = 3 # 最低保証

        # マウスカーソルの位置を取得
        mouse_pos = pygame.mouse.get_pos()
        # プレイヤーからマウスへの方向ベクトルを計算
        direction = pygame.math.Vector2(mouse_pos[0] - self.rect.centerx, 
                                         mouse_pos[1] - self.rect.centery)
        
        if direction.length() > 0:
            direction = direction.normalize()
        else:
            # マウスがプレイヤーと同じ位置なら上方向
            direction = pygame.math.Vector2(0, -1)

        self.vel += direction * power

    def update(self):
        self.input()

        # 無敵時間の処理
        if self.invincible:
            now = pygame.time.get_ticks()
            if now - self.invincible_timer > self.invincible_duration:
                self.invincible = False
                self.image = self.image_normal
            else:
                # 無敵中はダメージ画像にし、かつ点滅させる（仮の実装：アルファ値をいじるか描画を飛ばす）
                self.image = self.image_hit
                if (now // 100) % 2 == 0:
                    self.image.set_alpha(100)
                else:
                    self.image.set_alpha(255)
        else:
            self.image = self.image_normal
            self.image.set_alpha(255)

        # 物理挙動更新
        self.vel += self.acc
        self.vel *= self.friction # 摩擦
        self.pos += self.vel
        self.rect.center = self.pos

        # 画面端の制限
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = self.rect.centerx
            self.vel.x *= -0.5 # 跳ね返り
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.pos.x = self.rect.centerx
            self.vel.x *= -0.5
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.pos.y = self.rect.centery
            self.vel.y = 0 # 地面
        # 上端はクリア条件に関わるので一旦制限なし（マイナスに行ける）



class Obstacle(pygame.sprite.Sprite):
    def __init__(self, pos, size=(30, 30), color=RED, image_name=None):
        super().__init__()
        self.assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        if image_name:
            self.image_raw = pygame.image.load(os.path.join(self.assets_dir, image_name)).convert_alpha()
            self.image = pygame.transform.scale(self.image_raw, size)
            self.image = make_transparent(self.image)
            self.mask = pygame.mask.from_surface(self.image)
        else:
            self.image = pygame.Surface(size)
            self.image.fill(color)
            self.mask = pygame.mask.from_surface(self.image)
        
        self.rect = self.image.get_rect(topleft=pos)
        self.pos = pygame.math.Vector2(pos)

    def update(self):
        # 基本は何もしない
        pass

class Seaweed(Obstacle):
    def __init__(self, pos):
        super().__init__(pos, size=(30, 120), color=GREEN, image_name="seaweed.png")  # 縦長に変更
        # ゆらゆら動くためのパラメータ
        self.start_x = pos[0]
        self.sway_speed = 0.005
        self.sway_amount = 20

    def update(self):
        # サイン波で左右に揺れる
        offset = math.sin(pygame.time.get_ticks() * self.sway_speed) * self.sway_amount
        self.rect.x = self.start_x + offset

class Sunfish(Obstacle):
    def __init__(self, pos, player=None):
        super().__init__(pos, size=(70, 70), color=RED, image_name="sunfish.png")
        self.speed = 1.5
        self.player = player  # プレイヤーへの参照

    def update(self):
        if self.player:
            # プレイヤーに向かって移動
            direction = pygame.math.Vector2(
                self.player.rect.centerx - self.rect.centerx,
                self.player.rect.centery - self.rect.centery
            )
            if direction.length() > 0:
                direction = direction.normalize()
            self.pos += direction * self.speed
            self.rect.topleft = self.pos
        
        # 画面外に出たら消える
        if self.rect.right < -50 or self.rect.left > SCREEN_WIDTH + 50:
            self.kill()
        if self.rect.bottom < -50 or self.rect.top > SCREEN_HEIGHT + 50:
            self.kill()

class Turtle(Obstacle):
    def __init__(self, pos):
        # フィードバック反映：亀は大きく！
        super().__init__(pos, size=(120, 100), color=(0, 100, 0), image_name="turtle.png") # 深緑
        self.speed = 0.5  # 修正: 1 -> 0.5
        self.vel = pygame.math.Vector2(self.speed, 0)
        # ランダムな方向に動く
        import random
        self.vel.rotate_ip(random.randint(0, 360))

    def update(self):
        self.pos += self.vel
        self.rect.topleft = self.pos
        
        # 画面端で跳ね返る
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.vel.x *= -1
        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.vel.y *= -1

class PlasticWaste(Obstacle):
    def __init__(self, pos):
        super().__init__(pos, size=(60, 60), color=(100, 100, 100), image_name="plastic_waste.png")  # サイズ大きく
        self.fall_speed = 0.5  # 修正: 1 -> 0.5
        self.drift_speed = 0.3  # 横に流れる速度

    def update(self):
        self.rect.y += self.fall_speed
        self.rect.x += self.drift_speed  # 横に流れる
        if self.rect.top > SCREEN_HEIGHT or self.rect.left > SCREEN_WIDTH:
            self.kill()


class Bubble(pygame.sprite.Sprite):
    def __init__(self, pos, speed_y=2, size=None):
        super().__init__()
        if size:
            self.radius = size
        else:
            self.radius = random.randint(2, 6)
            
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        # 半透明の白い円
        pygame.draw.circle(self.image, (255, 255, 255, 150), (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=pos)
        
        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(random.uniform(-0.5, 0.5), -speed_y)
        self.timer = 0
        self.life_time = random.randint(60, 120) # フレーム数

    def update(self):
        self.pos += self.vel
        self.pos.x += math.sin(self.timer * 0.1) * 0.5 # ゆらゆら
        self.rect.center = self.pos
        
        self.timer += 1
        if self.timer > self.life_time:
            self.kill()
        
        # 画面外に出たら消える
        if self.rect.bottom < 0:
            self.kill()


