# -*- coding: utf-8 -*-

from math import copysign
from pygame.math import Vector2
from pygame.locals import KEYDOWN, KEYUP, K_LEFT, K_RIGHT
from pygame.sprite import collide_rect
from pygame.event import Event

from singleton import Singleton
from sprite import Sprite
from level import Level
import settings as config


# Return the sign of a number: getsign(-5)-> -1
getsign = lambda x: copysign(1, x)


class Player(Sprite, Singleton):
    def __init__(self, *args):
        # Calling default Sprite constructor
        Sprite.__init__(self, *args)
        self.__startrect = self.rect.copy()
        self.__maxvelocity = Vector2(config.PLAYER_MAX_SPEED, 100)
        self.__startspeed = .5

        self._velocity = Vector2()
        self._input = 0
        self._jumpforce = config.PLAYER_JUMPFORCE
        self._bonus_jumpforce = config.PLAYER_BONUS_JUMPFORCE

        self.gravity = config.GRAVITY
        self.accel = .5
        self.deccel = .6
        self.dead = False

    def _fix_velocity(self) -> None:
        """ Set player's velocity between max/min. Should be called in Player.update(). """
        self._velocity.y = min(self._velocity.y, self.__maxvelocity.y)
        self._velocity.y = round(max(self._velocity.y, -self.__maxvelocity.y), 2)
        self._velocity.x = min(self._velocity.x, self.__maxvelocity.x)
        self._velocity.x = round(max(self._velocity.x, -self.__maxvelocity.x), 2)

    def reset(self) -> None:
        """ Called only when game restarts (after player death). """
        self._velocity = Vector2()
        self.rect = self.__startrect.copy()
        self.camera_rect = self.__startrect.copy()
        self.dead = False

    def handle_event(self, event: Event) -> None:
        """ Handles key events for movement and jumping. """
        # Check if the player starts moving
        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                self._velocity.x = -self.__startspeed
                self._input = -1
            elif event.key == K_RIGHT:
                self._velocity.x = self.__startspeed
                self._input = 1

        # Check if the player stops moving
        elif event.type == KEYUP:
            if (event.key == K_LEFT and self._input == -1) or (
                    event.key == K_RIGHT and self._input == 1):
                self._input = 0

    def jump(self, force: float = None) -> None:
        """ Handles player jumping. """
        if not force:
            force = self._jumpforce
        self._velocity.y = -force

    def onCollide(self, obj: Sprite) -> None:
        """ Handles the player's collision with platforms. """
        self.rect.bottom = obj.rect.top
        self.jump()

    def collisions(self) -> None:
        """ Checks for collisions with level platforms. Should be called in Player.update(). """
        lvl = Level.instance
        if not lvl:
            return
        for platform in lvl.platforms:
            # Check if the player is falling and colliding with a platform
            if self._velocity.y > .5:
                # Check collisions with platform's spring bonus
                if platform.bonus and collide_rect(self, platform.bonus):
                    self.onCollide(platform.bonus)
                    self.jump(platform.bonus.force)

                # Check collisions with platform
                if collide_rect(self, platform):
                    self.onCollide(platform)
                    platform.onCollide()

    def update(self) -> None:
        """ Updates the player's position and velocity. Should be called each frame. """
        # Check if player is out of screen, marking death
        if self.camera_rect.y > config.YWIN * 2:
            self.dead = True
            return

        # Apply gravity and handle input acceleration/deceleration
        self._velocity.y += self.gravity
        if self._input:  # Accelerate left/right
            self._velocity.x += self._input * self.accel
        elif self._velocity.x:  # Decelerate
            self._velocity.x -= getsign(self._velocity.x) * self.deccel
            self._velocity.x = round(self._velocity.x)
        self._fix_velocity()

        # Update position (prevent player from going off-screen horizontally)
        self.rect.x = (self.rect.x + self._velocity.x) % (config.XWIN - self.rect.width)
        self.rect.y += self._velocity.y

        # Check for collisions
        self.collisions()

