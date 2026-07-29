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
        Gera uma imagem de capa elegante de 1200x630 px e retorna o caminho do arquivo salvo.
        """
        os.makedirs(self.output_dir, exist_ok=True)

        width, height = 1200, 630
        image = Image.new("RGB", (width, height), color=(11, 15, 25))
        draw = ImageDraw.Draw(image)

        # 1. Desenha gradiente sutil de fundo
        for y in range(height):
            r = int(11 + (25 - 11) * (y / height))
            g = int(15 + (27 - 15) * (y / height))
            b = int(25 + (53 - 25) * (y / height))
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # 2. Desenha elementos decorativos neon (linhas & cantos)
        draw.line([(0, 0), (width, 0)], fill=(0, 210, 255), width=6)  # Borda superior neon cyan
        draw.rectangle([40, 40, width - 40, height - 40], outline=(40, 50, 80), width=2)

        # 3. Badge "INSIGHT FORGE | AI CURATED CONTENT"
        draw.rectangle([70, 70, 360, 105], fill=(30, 41, 69), outline=(0, 210, 255), width=1)
        draw.text((85, 80), "INSIGHT FORGE  |  TECH INSIGHTS", fill=(0, 210, 255))

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
                    fill=(20, 30, 50),
                    outline=(100, 130, 200),
                    width=1,
                )
                draw.text((x_pill + 12, y_pill + 8), topic_label, fill=(180, 210, 255))
                x_pill += pill_w + 15

        # 6. Rodapé do autor / projeto
        draw.text((70, 550), "Gerações Inteligentes de Conteúdo Técnico", fill=(120, 140, 170))

        # Salva o arquivo
        filename_slug = slug or self._slugify(title)
        filename = f"{date_str + '-' if date_str else ''}{filename_slug}.png"
        file_path = os.path.join(self.output_dir, filename)

        image.save(file_path, "PNG")
        return file_path

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
