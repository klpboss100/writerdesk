"""
로고 생성 스크립트 - 작가의 책상 / Writer's Desk
흰 바탕 + 심플 노트북 + 네이비 (#0f3460)
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_logo(output_path="logo.png", width=400, height=200):
    # 배경: 흰색
    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    navy = (15, 52, 96)       # #0f3460
    light_navy = (30, 80, 150)
    accent = (200, 215, 240)

    # ── 노트북 아이콘 (왼쪽) ──────────────────────────────
    bx, by = 30, 40          # 책 왼쪽 상단
    bw, bh = 90, 115          # 책 너비·높이

    # 책 본체
    draw.rounded_rectangle([bx, by, bx+bw, by+bh], radius=6,
                            fill=(255, 255, 255), outline=navy, width=3)

    # 책등 (왼쪽 세로 띠)
    draw.rounded_rectangle([bx, by, bx+14, by+bh], radius=6,
                            fill=navy)

    # 가로 줄 (lined paper)
    line_y = by + 22
    while line_y < by + bh - 12:
        draw.line([(bx+22, line_y), (bx+bw-10, line_y)],
                  fill=accent, width=2)
        line_y += 13

    # 펜 (노트북 위에 비스듬히)
    px1, py1 = bx + bw - 12, by - 20
    px2, py2 = bx + bw + 18, by + 18
    draw.line([(px1, py1), (px2, py2)], fill=navy, width=4)
    # 펜촉
    draw.polygon([(px2-4, py2-4), (px2+6, py2+6), (px2+8, py2)],
                 fill=navy)
    # 펜 클립
    draw.line([(px1+4, py1+6), (px1+10, py1+2)], fill=light_navy, width=2)

    # ── 텍스트 ────────────────────────────────────────────
    tx = bx + bw + 24

    # 앱명 한글
    try:
        font_title_ko = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
        font_title_en = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_tag     = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    except Exception:
        font_title_ko = ImageFont.load_default()
        font_title_en = font_title_ko
        font_tag      = font_title_ko

    draw.text((tx, by + 18), "작가의 책상", font=font_title_ko, fill=navy)
    draw.text((tx, by + 52), "Writer's Desk", font=font_title_en, fill=light_navy)

    # 구분선
    draw.line([(tx, by + 82), (tx + 230, by + 82)], fill=accent, width=2)

    # 태그라인
    draw.text((tx, by + 90), "당신의 원고를 완성시켜 드립니다",
              font=font_tag, fill=(80, 100, 140))

    img.save(output_path, "PNG")
    print(f"✅ 로고 저장: {output_path}")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    create_logo("logo.png")
