# -*- coding: utf-8 -*-
import sys, os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

OUTPUT_PPTX = r'C:\Users\DevLab\Desktop\Soutenance\Soutenance_NetScan_Officielle.pptx'
OUTPUT_BAS = r'C:\Users\DevLab\Desktop\Soutenance\Generer_Soutenance_NetScan.bas'

# Color Palette (Modern Cybersecurity)
C_NAVY_DARK = RGBColor(15, 23, 42)      # #0F172A Deep Navy Slate
C_NAVY_HEADER = RGBColor(10, 25, 47)    # #0A192F Dark Banner
C_CYAN_ACCENT = RGBColor(14, 116, 144)  # #0E7490 Modern Teal/Cyan
C_BLUE_LIGHT  = RGBColor(2, 132, 199)   # #0284C7 Cyber Blue
C_BG_PAGE     = RGBColor(248, 250, 252) # #F8FAFC Clean Light Gray/White
C_CARD_BG     = RGBColor(255, 255, 255) # Pure White
C_BORDER      = RGBColor(226, 232, 240) # Slate border
C_TEXT_MAIN   = RGBColor(15, 23, 42)    # Dark Charcoal
C_TEXT_MUTED  = RGBColor(100, 116, 139) # Slate Muted
C_SUCCESS     = RGBColor(16, 185, 129)  # Emerald Green
C_DANGER      = RGBColor(220, 38, 38)   # Crimson Red
C_WHITE       = RGBColor(255, 255, 255)

print('Starting presentation generator...')
