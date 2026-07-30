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
    ) -> str:
        """
        Gera uma imagem de capa elegante e dinamicamente tematizada de 1200x630 px.
        """
        os.makedirs(self.output_dir, exist_ok=True)

        width, height = 1200, 630
        
        # Seleciona paleta de cores dinâmica baseada no primeiro tópico relevante ou hash do título
        palette = self._select_palette(topics, title)
        bg_start, bg_end = palette["bg_start"], palette["bg_end"]
        accent_color = palette["accent"]
        pill_fill = palette["pill_fill"]
        pill_outline = palette["pill_outline"]

        image = Image.new("RGB", (width, height), color=bg_start)
        draw = ImageDraw.Draw(image)

        # 1. Desenha gradiente sutil de fundo
        for y in range(height):
            r = int(bg_start[0] + (bg_end[0] - bg_start[0]) * (y / height))
            g = int(bg_start[1] + (bg_end[1] - bg_start[1]) * (y / height))
            b = int(bg_start[2] + (bg_end[2] - bg_start[2]) * (y / height))
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # 2. Desenha elementos decorativos neon (linhas, cantos e formas geométricas)
        draw.line([(0, 0), (width, 0)], fill=accent_color, width=8)  # Borda superior neon
        draw.rectangle([40, 40, width - 40, height - 40], outline=pill_outline, width=2)
        
        # Círculo sutil brilhante no canto superior direito para profundidade visual
        draw.ellipse([width - 250, -50, width + 50, 250], outline=accent_color, width=1)

        # 3. Badge "INSIGHT FORGE | TECH INSIGHTS"
        draw.rectangle([70, 70, 370, 108], fill=pill_fill, outline=accent_color, width=1)
        draw.text((85, 81), "INSIGHT FORGE  |  TECH INSIGHTS", fill=accent_color)

        # 4. Renderiza o Título com quebra automática de linhas
        lines = self._wrap_text(title, max_chars_per_line=32)
        y_text = 160
        for line in lines[:4]:  # no máximo 4 linhas
            draw.text((70, y_text), line, fill=(255, 255, 255))
            y_text += 55

        # 5. Renderiza pills de tópicos na parte inferior
        if topics:
            x_pill = 70
            y_pill = 480
            for topic in topics[:4]:
                topic_label = f"# {topic.upper()}"
                pill_w = len(topic_label) * 11 + 24
                draw.rectangle(
                    [x_pill, y_pill, x_pill + pill_w, y_pill + 36],
                    fill=pill_fill,
                    outline=accent_color,
                    width=1,
                )
                draw.text((x_pill + 12, y_pill + 8), topic_label, fill=(240, 245, 255))
                x_pill += pill_w + 15

        # 6. Rodapé do autor / projeto
        draw.text((70, 550), "Gerações Inteligentes de Conteúdo Técnico", fill=(140, 160, 190))

        # Salva o arquivo
        filename_slug = slug or self._slugify(title)
        filename = f"{date_str + '-' if date_str else ''}{filename_slug}.png"
        file_path = os.path.join(self.output_dir, filename)

        image.save(file_path, "PNG")
        return file_path

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

