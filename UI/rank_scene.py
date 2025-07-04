import pygame
from UI.components.character_animator import CharacterAnimator
from UI.components.base_scene import BaseScene
from UI.components.audio_manager import AudioManager
from simulation import Simulation
import setting

class RankScene(BaseScene):
    def __init__(self, screen, player):
        super().__init__(screen)
        self.audio = AudioManager.get_instance()
        self.player = player
        # 背景
        self.background = pygame.image.load(setting.ImagePath.BACKGROUND_PATH).convert_alpha()
        self.background = pygame.transform.scale(self.background, self.screen.get_size())
        self.background.set_alpha(100)
        self.transition_direction = 1 

        self.simulation = Simulation()
        self.simulation.run_and_plot_all_with_player(player)
        self.overlay_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        self.overlay_alpha = 0 

        # 字型
        self.font_desc = pygame.font.Font(setting.JFONT_PATH_REGULAR, 36)

        # 動畫角色
        self.animator = CharacterAnimator(self.player.ending, (900, 30), (240, 220))
        self.animator.frame_delay = 5



        # 圖片載入與縮放
        self.image_paths = [
            setting.GPA_HIGHLIGHT_PATH,
            setting.TOTAL_SCORE_HIGHLIGHT_PATH,
            setting.MIDTERM_FINAL_HIGHLIGHT_PATH,
        ]
        self.images = []
        for path in self.image_paths:
            img = pygame.image.load(path).convert_alpha()
            orig_w, orig_h = img.get_size()
            scale_ratio = min(850 / orig_w, 600 / orig_h)
            new_size = (int(orig_w * scale_ratio), int(orig_h * scale_ratio))
            scaled = pygame.transform.smoothscale(img, new_size)
            self.images.append(scaled)

        self.current_page = 0
        self.next_page = None

        # 滑動動畫參數
        self.transitioning = False
        self.slide_offset = 0
        self.slide_speed = 40  # 每 frame 移動速度

        # 自動換頁計時器
        self.page_timer = 0
        self.auto_page_delay = 5000  # 毫秒

    def update(self):
        if self.overlay_alpha < 140:
            self.overlay_alpha += 5
        self.overlay_surface.fill((0, 0, 0, self.overlay_alpha))

        self.animator.update()
        self.page_timer += self.clock.get_time()

        if self.page_timer >= self.auto_page_delay and not self.transitioning:
            self.start_transition()

        if self.transitioning:
            self.slide_offset += self.slide_speed
            if self.slide_offset >= self.images[0].get_height():
                self.current_page = self.next_page
                self.transitioning = False
                self.slide_offset = 0
                self.page_timer = 0  # 重設計時器
    
    def start_transition(self, direction=1):
        self.transition_direction = direction
        self.next_page = (self.current_page + direction) % len(self.images)
        self.transitioning = True
        self.slide_offset = 0
        self.page_timer = 0
        self.audio.play_sound(setting.SoundEffect.NEXT_PAGE_PATH)

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        screen.blit(self.overlay_surface, (0, 0))

        img_current = self.images[self.current_page]
        rect_current = img_current.get_rect(center=(self.SCREEN_WIDTH // 2 - 150, self.SCREEN_HEIGHT // 2 - self.slide_offset))
        screen.blit(img_current, rect_current)

        if self.transitioning:
            img_next = self.images[self.next_page]
            if self.transition_direction == 1:
                # 向下滑
                rect_next = img_next.get_rect(center=(self.SCREEN_WIDTH // 2 - 150, self.SCREEN_HEIGHT // 2 + img_next.get_height() - self.slide_offset))
                rect_current = img_current.get_rect(center=(self.SCREEN_WIDTH // 2 - 150, self.SCREEN_HEIGHT // 2 - self.slide_offset))
            else:
                # 向上滑
                rect_next = img_next.get_rect(center=(self.SCREEN_WIDTH // 2 - 150, self.SCREEN_HEIGHT // 2 - img_next.get_height() + self.slide_offset))
                rect_current = img_current.get_rect(center=(self.SCREEN_WIDTH // 2 - 150, self.SCREEN_HEIGHT // 2 + self.slide_offset))
            screen.blit(img_current, rect_current)
            screen.blit(img_next, rect_next)
        else:
            rect_current = img_current.get_rect(center=(self.SCREEN_WIDTH // 2 - 150, self.SCREEN_HEIGHT // 2))
            screen.blit(img_current, rect_current)

        hint = self.font_desc.render("按 ↓ 顯示下一頁, Esc 退出", True, (230, 230, 230))
        screen.blit(hint, (self.SCREEN_WIDTH - 500, self.SCREEN_HEIGHT - 60))

        self.animator.draw(screen)

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key == pygame.K_DOWN and not self.transitioning:
                self.start_transition(direction=1)
            elif event.key == pygame.K_UP and not self.transitioning:
                self.start_transition(direction=-1)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)

            self.update()
            self.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(self.FPS)

        self.running = False
