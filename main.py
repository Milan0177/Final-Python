import pygame
import sys
from singleton import Singleton
from camera import Camera
from player import Player
from level import Level
import settings as config

class Game(Singleton):

    def __init__(self) -> None:
        # ============= Initialization =============  
        self.__alive = True
        # Window / Render
        self.window = pygame.display.set_mode(config.DISPLAY, config.FLAGS)
        self.clock = pygame.time.Clock()

        # Instances
        self.camera = Camera()
        self.lvl = Level()
        self.player = Player(
            config.HALF_XWIN - config.PLAYER_SIZE[0] / 2,  # X POS
            config.HALF_YWIN + config.HALF_YWIN / 2,  # Y POS
            *config.PLAYER_SIZE,  # SIZE
            config.PLAYER_COLOR  # COLOR
        )

        # User Interface
        self.score = 0
        self.current_level = 1
        self.LEVEL_THRESHOLDS = [100, 300, 500]  # Level thresholds in meters
        self.score_txt = config.SMALL_FONT.render("0 m", 1, config.GRAY)
        self.level_txt = config.SMALL_FONT.render("Level 1", 1, config.GRAY)
        self.next_level_txt = config.SMALL_FONT.render("Next: 100 m", 1, config.GRAY)

        self.score_pos = pygame.math.Vector2(10, 10)
        self.level_pos = pygame.math.Vector2(10, 40)
        self.next_level_pos = pygame.math.Vector2(10, 70)

        self.gameover_txt = config.LARGE_FONT.render("Game Over", 1, config.GRAY)
        self.gameover_rect = self.gameover_txt.get_rect(
            center=(config.HALF_XWIN, config.HALF_YWIN))

        # Restart button
        self.restart_button = pygame.Rect(config.HALF_XWIN - 100, config.HALF_YWIN + 50, 200, 50)
        self.restart_button_txt = config.SMALL_FONT.render("Restart", 1, config.WHITE)
        self.restart_button_txt_rect = self.restart_button_txt.get_rect(center=self.restart_button.center)

        # Congratulations screen
        self.congratulations_txt = config.LARGE_FONT.render("Congratulations!", 1, config.GREEN)
        self.congratulations_rect = self.congratulations_txt.get_rect(center=(config.HALF_XWIN, config.HALF_YWIN - 100))

    def close(self):
        self.__alive = False

    def reset(self):
        """Resets the game to its initial state."""
        self.camera.reset()
        self.lvl.reset()
        self.player.reset()
        self.score = 0
        self.current_level = 1  # Reset to level 1
        self.update_ui_texts()

    def update_ui_texts(self):
        """Updates score, level, and next level text."""
        self.score_txt = config.SMALL_FONT.render(f"{self.score} m", 1, config.GRAY)
        self.level_txt = config.SMALL_FONT.render(f"Level {self.current_level}", 1, config.GRAY)
        
        if self.current_level == 1:
            remaining = self.LEVEL_THRESHOLDS[0] - self.score
            self.next_level_txt = config.SMALL_FONT.render(f"Next: {remaining} m", 1, config.GRAY)
        elif self.current_level == 2:
            remaining = self.LEVEL_THRESHOLDS[1] - self.score
            self.next_level_txt = config.SMALL_FONT.render(f"Next: {remaining} m", 1, config.GRAY)
        elif self.current_level == 3:
            remaining = self.LEVEL_THRESHOLDS[2] - self.score
            self.next_level_txt = config.SMALL_FONT.render(f"Next: {remaining} m", 1, config.GRAY)   
        elif self.current_level == 4:
            if self.score >= self.LEVEL_THRESHOLDS[3]:
                self.next_level_txt = config.SMALL_FONT.render("Congratulations!", 1, config.GRAY)
              # Show the "Congratulations" screen if the player has completed the final level
        if self.current_level == 4 and self.score >= self.LEVEL_THRESHOLDS[2]:
            self.window.fill(config.LIGHT_GREEN)  # New background color for the "Congratulations" screen
            self.window.blit(self.congratulations_txt, self.congratulations_rect)
            pygame.display.update()
            pygame.time.wait(2000)  # Wait for 2 seconds before allowing the player to continue
            self.reset()  # Restart the game after showing the Congratulations screen


    def _event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.close()
                if event.key == pygame.K_RETURN and self.player.dead:
                    self.reset()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.player.dead and self.restart_button.collidepoint(event.pos):
                    self.reset()
            self.player.handle_event(event)

    def _update_level(self):
        """Checks if the player has reached the score threshold for the next level."""
        if self.current_level < len(self.LEVEL_THRESHOLDS) and self.score >= self.LEVEL_THRESHOLDS[self.current_level - 1]:
            self.current_level += 1
            self.camera.reset()  # Reset camera for the new level
            self.player.reset()  # Reset player position
            self.lvl.reset()  # Reset level elements
            self.update_ui_texts()

    def _update_loop(self):
        self.player.update()
        self.lvl.update()

        if not self.player.dead:
            self.camera.update(self.player.rect)
            self.score = -self.camera.state.y // 50  # Calculate score
            self.update_ui_texts()
            self._update_level()

    def _render_loop(self):
        # Set background color based on the current level
        if self.current_level == 1:
            background_color = config.LIGHT_BROWN
        elif self.current_level == 2:
            background_color = config.YELLOW
        elif self.current_level == 3:
            background_color = config.LIGHT_BLUE
        else:
            background_color = config.WHITE

        self.window.fill(background_color)
        self.lvl.draw(self.window)
        self.player.draw(self.window)

        # User Interface
        if self.player.dead:
            self.window.blit(self.gameover_txt, self.gameover_rect)
            pygame.draw.rect(self.window, config.GRAY, self.restart_button)
            self.window.blit(self.restart_button_txt, self.restart_button_txt_rect)

        # Render score, level, and next level information
        self.window.blit(self.score_txt, self.score_pos)
        self.window.blit(self.level_txt, self.level_pos)
        self.window.blit(self.next_level_txt, self.next_level_pos)

      
        pygame.display.update()
        self.clock.tick(config.FPS)

    def run(self):
        while self.__alive:
            self._event_loop()
            self._update_loop()
            self._render_loop()
        pygame.quit()

if __name__ == "__main__":
    # ============= PROGRAM STARTS HERE =============  
    game = Game()
    game.run()
