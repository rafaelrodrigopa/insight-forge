import os
import re
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont


class BannerGenerator:
    """
    Gerador dinâmico de banners visuais de alta resolução (1200x630) para posts no LinkedIn/redes sociais.
    """

    def __init__(self, output_dir: str = "posts/images"):
        self.output_dir = output_dir

    def generate_banner(
        self,
        title: str,
        topics: Optional[List[str]] = None,
        slug: Optional[str] = None,
        date_str: Optional[str] = None,
        aspect_ratio: str = "1:1",
    ) -> str:
        """
        Gera uma imagem de capa elegante e dinamicamente tematizada (1200x1200 px para 1:1 quadrado sem barras pretas no LinkedIn, ou 1200x630 para 16:9).
        """
        os.makedirs(self.output_dir, exist_ok=True)

        if aspect_ratio == "16:9":
            width, height = 1200, 630
        else:
            width, height = 1200, 1200

        # Seleciona paleta de cores dinâmica baseada no primeiro tópico relevante ou hash do título
        palette = self._select_palette(topics, title)
        bg_start, bg_end = palette["bg_start"], palette["bg_end"]
        accent_color = palette["accent"]
        pill_fill = palette["pill_fill"]
        pill_outline = palette["pill_outline"]

        # 0. Carrega fontes escaláveis com fallback
        is_square = (height == 1200)
        title_size = 46 if is_square else 38
        title_font = self._get_font(title_size, bold=True)
        badge_font = self._get_font(18 if is_square else 16, bold=True)
        pill_font = self._get_font(20 if is_square else 18, bold=True)
        footer_font = self._get_font(18 if is_square else 16)

        image = Image.new("RGB", (width, height), color=bg_start)
        draw = ImageDraw.Draw(image)

        # 1. Desenha gradiente sutil de fundo
        for y in range(height):
            r = int(bg_start[0] + (bg_end[0] - bg_start[0]) * (y / height))
            g = int(bg_start[1] + (bg_end[1] - bg_start[1]) * (y / height))
            b = int(bg_start[2] + (bg_end[2] - bg_start[2]) * (y / height))
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # 2. Desenha elementos decorativos neon (linhas, cantos e formas geométricas)
        draw.line([(0, 0), (width, 0)], fill=accent_color, width=10 if is_square else 8)
        draw.rectangle([50, 50, width - 50, height - 50], outline=pill_outline, width=2)

        # Círculo sutil brilhante no canto superior direito para profundidade visual
        draw.ellipse([width - 320, -80, width + 80, 320], outline=accent_color, width=1)

        # 3. Badge "INSIGHT FORGE | TECH INSIGHTS"
        badge_y = 100 if is_square else 70
        draw.rectangle([80, badge_y, 450, badge_y + 46], fill=pill_fill, outline=accent_color, width=1)
        draw.text((95, badge_y + 11), "INSIGHT FORGE  |  TECH INSIGHTS", fill=accent_color, font=badge_font)

        # 4. Renderiza o Título com quebra automática de linhas
        lines = self._wrap_text(title, max_chars_per_line=24 if is_square else 28)
        y_text = 240 if is_square else 160
        line_height = 70 if is_square else 60
        for line in lines[:5]:  # até 5 linhas no formato quadrado
            draw.text((80, y_text), line, fill=(255, 255, 255), font=title_font)
            y_text += line_height

        # Linha acento decorativo abaixo do título
        y_text += 20
        draw.line([(80, y_text), (280, y_text)], fill=accent_color, width=3)

        # 5. Renderiza pills de tópicos na parte inferior
        if topics:
            x_pill = 80
            y_pill = 900 if is_square else 470
            pill_h = 44 if is_square else 40
            for topic in topics[:4]:
                topic_label = f"# {topic.upper()}"
                try:
                    bbox = pill_font.getbbox(topic_label)
                    pill_w = (bbox[2] - bbox[0]) + 32
                except Exception:
                    pill_w = len(topic_label) * 13 + 32

                if x_pill + pill_w > width - 80:
                    x_pill = 80
                    y_pill += pill_h + 15

                draw.rectangle(
                    [x_pill, y_pill, x_pill + pill_w, y_pill + pill_h],
                    fill=pill_fill,
                    outline=accent_color,
                    width=1,
                )
                draw.text((x_pill + 16, y_pill + (10 if is_square else 9)), topic_label, fill=(240, 245, 255), font=pill_font)
                x_pill += pill_w + 16

        # 6. Rodapé do autor / projeto
        footer_y = 1090 if is_square else 545
        draw.text((80, footer_y), "Gerações Inteligentes de Conteúdo Técnico | rafaelrodrigopa.com.br", fill=(140, 160, 190), font=footer_font)

        # Salva o arquivo
        filename_slug = slug or self._slugify(title)
        filename = f"{date_str + '-' if date_str else ''}{filename_slug}.png"
        file_path = os.path.join(self.output_dir, filename)

        image.save(file_path, "PNG")
        return file_path

    @staticmethod
    def _get_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
        """
        Carrega fonte TrueType escalável compatível entre sistemas operacionais (Windows/Linux/Mac).
        """
        font_candidates = [
            "segoeuib.ttf" if bold else "segoeui.ttf",
            "arialbd.ttf" if bold else "arial.ttf",
            "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
            "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "C:\\Windows\\Fonts\\segoeui.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",
        ]
        for font_name in font_candidates:
            try:
                return ImageFont.truetype(font_name, size)
            except Exception:
                continue
        try:
            return ImageFont.load_default(size=size)
        except Exception:
            return ImageFont.load_default()

    @staticmethod
    def _select_palette(topics: Optional[List[str]], title: str) -> dict:
        """
        Determina paleta temática com base nos tópicos ou hash do título.
        """
        topics_str = " ".join(topics or []).lower()
        title_lower = title.lower()

        if any(k in topics_str or k in title_lower for k in ["numpy", "data science", "pandas", "scipy", "math"]):
            # Magenta / Purple Theme (Data Science)
            return {
                "bg_start": (15, 10, 30),
                "bg_end": (35, 15, 60),
                "accent": (255, 64, 129),
                "pill_fill": (45, 20, 70),
                "pill_outline": (180, 80, 200),
            }
        elif any(k in topics_str or k in title_lower for k in ["python", "django", "fastapi", "code"]):
            # Cyan / Deep Ocean Theme (Python)
            return {
                "bg_start": (8, 20, 35),
                "bg_end": (15, 40, 70),
                "accent": (0, 210, 255),
                "pill_fill": (20, 45, 80),
                "pill_outline": (60, 140, 220),
            }
        elif any(k in topics_str or k in title_lower for k in ["ai", "machine learning", "llm", "gpt", "model"]):
            # Emerald / Teal Theme (AI & Machine Learning)
            return {
                "bg_start": (6, 25, 20),
                "bg_end": (12, 50, 40),
                "accent": (0, 230, 153),
                "pill_fill": (15, 55, 45),
                "pill_outline": (50, 180, 130),
            }
        elif any(k in topics_str or k in title_lower for k in ["analytics", "sql", "bigquery", "database", "bi"]):
            # Amber / Gold Theme (Analytics & Engineering)
            return {
                "bg_start": (25, 18, 10),
                "bg_end": (55, 35, 15),
                "accent": (255, 180, 0),
                "pill_fill": (60, 40, 15),
                "pill_outline": (200, 140, 40),
            }

        # Paleta padrão moderna (Indigo/Violet)
        return {
            "bg_start": (11, 15, 30),
            "bg_end": (25, 30, 65),
            "accent": (100, 130, 255),
            "pill_fill": (30, 40, 75),
            "pill_outline": (90, 120, 210),
        }

    @staticmethod
    def _wrap_text(text: str, max_chars_per_line: int = 30) -> List[str]:
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            if sum(len(w) for w in current_line) + len(current_line) + len(word) <= max_chars_per_line:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))

        return lines

    @staticmethod
    def _slugify(text: str) -> str:
        import unicodedata

        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        text = text.lower().strip()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[\s_-]+", "-", text)
        return text.strip("-") or "banner"

