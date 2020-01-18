# -*- coding: utf-8 -*-
#
# Tuxemon
# Copyright (C) 2014, William Edwards <shadowapex@gmail.com>,
#                     Benjamin Bean <superman2k5@gmail.com>
#
# This file is part of Tuxemon.
#
# Tuxemon is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Tuxemon is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Tuxemon.  If not, see <http://www.gnu.org/licenses/>.
#
# Contributor(s):
#
# William Edwards <shadowapex@gmail.com>
# Leif Theden <leif.theden@gmail.com>
#
#
# core.prepare Prepares the game environment.
#
"""This module initializes the display and creates dictionaries of resources.
It contains all the static and dynamic variables used throughout the game such
as display resolution, scale, etc.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os.path
import re

from tuxemon.constants import paths
from tuxemon.core import config

logger = logging.getLogger(__name__)

# TODO: refact this out when other platforms supported (such as headless)
PLATFORM = "pygame"


# list of regular expressions to blacklist devices
joystick_blacklist = [
    re.compile(r"Microsoft.*Transceiver.*"),
]

# Create game dir if missing
if not os.path.isdir(paths.USER_GAME_DIR):
    os.makedirs(paths.USER_GAME_DIR)

# Create game data dir if missing
if not os.path.isdir(paths.USER_GAME_DATA_DIR):
    os.makedirs(paths.USER_GAME_DATA_DIR)

# Create game savegame dir if missing
if not os.path.isdir(paths.USER_GAME_SAVE_DIR):
    os.makedirs(paths.USER_GAME_SAVE_DIR)

# Generate default config
config.generate_default_config()

# Read "tuxemon.cfg" config from disk, update and write back
CONFIG = config.TuxemonConfig(paths.USER_CONFIG_PATH)

with open(paths.USER_CONFIG_PATH, "w") as fp:
    CONFIG.cfg.write(fp)

# Set up the screen size and caption
SCREEN_SIZE = CONFIG.resolution
ORIGINAL_CAPTION = CONFIG.window_caption

# Set the native tile size so we know how much to scale our maps
TILE_SIZE = [16, 16]  # 1 tile = 16 pixels

# Set the status icon size so we know how much to scale our menu icons
ICON_SIZE = [7, 7]

# Set the healthbar _color
HP_COLOR = (112, 248, 168)

# Set the XP bar _color
XP_COLOR = (248, 245, 71)

# Native resolution is similar to the old gameboy resolution. This is
# used for scaling.
NATIVE_RESOLUTION = [240, 160]

# If scaling is enabled, scale the tiles based on the resolution
if CONFIG.large_gui:
    SCALE = 2
    TILE_SIZE[0] *= SCALE
    TILE_SIZE[1] *= SCALE
elif CONFIG.scaling:
    SCALE = int((SCREEN_SIZE[0] / NATIVE_RESOLUTION[0]))
    TILE_SIZE[0] *= SCALE
    TILE_SIZE[1] *= SCALE
else:
    SCALE = 1

# Reference user save dir
SAVE_PATH = os.path.join(paths.USER_GAME_SAVE_DIR, "slot")
SAVE_METHOD = "JSON"
# SAVE_METHOD = "CBOR"

DEV_TOOLS = CONFIG.dev_tools


def pygame_init():
    """ Eventually refactor out of prepare
    """
    global JOYSTICKS
    global FONTS
    global MUSIC
    global SFX
    global GFX
    global SCREEN
    global SCREEN_RECT

    import pygame as pg

    logger.debug("pygame init")
    pg.init()
    pg.display.set_caption(ORIGINAL_CAPTION)

    fullscreen = pg.FULLSCREEN if CONFIG.fullscreen else 0
    flags = pg.HWSURFACE | pg.DOUBLEBUF | fullscreen

    SCREEN = pg.display.set_mode(SCREEN_SIZE, flags)
    SCREEN_RECT = SCREEN.get_rect()

    # Disable the mouse cursor visibility
    pg.mouse.set_visible(not CONFIG.hide_mouse)

    # Set up any gamepads that we detect
    # The following event types will be generated by the joysticks:
    # JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
    JOYSTICKS = list()
    pg.joystick.init()
    devices = [pg.joystick.Joystick(x) for x in range(pg.joystick.get_count())]

    # Initialize the individual joysticks themselves.
    for joystick in devices:
        name = joystick.get_name()
        print("Found joystick: \"{}\"".format(name))
        blacklisted = any(i.match(name) for i in joystick_blacklist)
        if blacklisted:
            print("Ignoring joystick: \"{}\"".format(name))
        else:
            print("Configuring joystick: \"{}\"".format(name))
            joystick.init()
            JOYSTICKS.append(joystick)

    from .platform import android
    # Map the appropriate android keys if we're on android
    if android:
        android.init()
        android.map_key(android.KEYCODE_MENU, pg.K_ESCAPE)


# Initialize the game framework
def init():

    # initialize any platform-specific workarounds before pygame
    from tuxemon.core import platform
    platform.init()

    # Initialize PyGame and our screen surface.
    if PLATFORM == 'pygame':
        pygame_init()

# Fetches a resource file
def fetch(*args):
    path = os.path.join(*args)
    resource_default = os.path.join(paths.BASEDIR, "..", "resources", path)
    resource_mod = os.path.join(paths.BASEDIR, "..", "mod", CONFIG.data, path)

    # Always try the mod directory first, fallback to resources
    if os.path.exists(resource_mod):
        return resource_mod
    if os.path.exists(resource_default):
        return resource_default
    return None
