
class Player:
    def __init__(self):
        self.x = 100
        self.y = 300
        self.vy = 0
        self.speed = 4
        self.on_ground = True

        self.hp = 5
        self.ammo = 10
        self.max_ammo = 10

        self.rect = pg.Rect(self.x, self.y, 32, 32)

    def update(self, keys):
        if keys[pg.K_LEFT]:
            self.x -= self.speed
        if keys[pg.K_RIGHT]:
            self.x += self.speed

        # ジャンプ
        if keys[pg.K_SPACE] and self.on_ground:
            self.vy = -10
            self.on_ground = False

        # 重力
        self.vy += 0.5
        self.y += self.vy

        # 地面
        if self.y >= 300:
            self.y = 300
            self.vy = 0
            self.on_ground = True

        self.rect.topleft = (self.x, self.y)

    def shoot(self):
        if self.ammo > 0:
            self.ammo -= 1
            return Bullet(self.x + 16, self.y + 8, 4, 0)
        return None

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 2
        self.alive = True

        self.attack_cool = 0
        self.rect = pg.Rect(self.x, self.y, 32, 32)

    def update(self, player):
        if not self.alive:
            return

        # 少しずつ近づく
        if player.x > self.x:
            self.x += 1
        else:
            self.x -= 1

        # 攻撃クール
        if self.attack_cool > 0:
            self.attack_cool -= 1

        distance = abs(player.x - self.x)
        if distance < 40 and self.attack_cool == 0:
            player.hp -= 1
            self.attack_cool = 60

        self.rect.topleft = (self.x, self.y)

    def damage(self, value, player):
        self.hp -= value
        if self.hp <= 0:
            self.alive = False
            player.ammo = min(player.ammo + 3, player.max_ammo)

class Bullet:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

        self.bounce = 0
        self.max_bounce = 2
        self.alive = True

        self.rect = pg.Rect(self.x, self.y, 8, 8)

    def update(self, walls):
        self.x += self.vx
        self.y += self.vy
        self.rect.topleft = (self.x, self.y)

        for wall in walls:
            if self.rect.colliderect(wall):
                if abs(self.rect.right - wall.left) < 10 or abs(self.rect.left - wall.right) < 10:
                    self.vx *= -1
                if abs(self.rect.bottom - wall.top) < 10 or abs(self.rect.top - wall.bottom) < 10:
                    self.vy *= -1

                self.bounce += 1
                if self.bounce > self.max_bounce:
                    self.alive = False

        for bullet in bullets:
            for enemy in enemies:
                if enemy.alive and bullet.rect.colliderect(enemy.rect):
                    enemy.damage(1, player)
                    bullet.alive = False
        bullets = [b for b in bullets if b.alive]
        enemies = [e for e in enemies if e.alive]

camera_x = player.x - SCREEN_W // 2
camera_x = max(0, camera_x)
screen.blit(player_image, (player.x - camera_x, player.y))
screen.blit(enemy_image, (enemy.x - camera_x, enemy.y))

