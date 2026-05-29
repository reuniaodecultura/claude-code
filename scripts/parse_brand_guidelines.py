import re
import json


def parse_instructions(file_content):
    instructions = {}

    # Brand Context
    brand_context_block_match = re.search(r'## 1\\. CONTEXTO DA MARCA\s*\n\n(.*?)\n-----\n', file_content, re.DOTALL)
    if brand_context_block_match:
        brand_context_content = brand_context_block_match.group(1)

        name_match = re.search(r'\*\*Nome:\*\* (.+?)\s*\n', brand_context_content, re.DOTALL)
        tagline_match = re.search(r'\*\*Tagline:\*\* \*[""](.+?)[""]\*\s*\n', brand_context_content, re.DOTALL)
        positioning_match = re.search(r'\*\*Posicionamento:\*\* (.+?)\s*\n', brand_context_content, re.DOTALL)
        tone_match = re.search(r'\*\*Tom de voz:\*\* (.+?)\s*\n', brand_context_content, re.DOTALL)
        audience_match = re.search(r'\*\*Público:\*\* (.+?)(?:\s*\n\s*\n|$)', brand_context_content, re.DOTALL)

        instructions["brand_context"] = {
            "name": name_match.group(1).strip() if name_match else None,
            "tagline": tagline_match.group(1).strip() if tagline_match else None,
            "positioning": positioning_match.group(1).strip() if positioning_match else None,
            "tone_of_voice": tone_match.group(1).strip() if tone_match else None,
            "audience": audience_match.group(1).strip() if audience_match else None,
        }

    # Visual Identity - Color Palette
    color_palette_match = re.search(
        r'### Paleta de cores\n\n\|Elemento\s+\|Cor\s+\|\n\|-----------------\|---------------------------------------------------------------------------\|\n((?:\|.+\|.+\|\n)+)',
        file_content,
    )
    if color_palette_match:
        colors_raw = color_palette_match.group(1).strip().split('\n')
        instructions["color_palette"] = {}
        for line in colors_raw:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) == 2:
                instructions["color_palette"][parts[0]] = parts[1]

    # Visual Identity - Typography
    typography_match = re.search(
        r'### Tipografia\n\n\|Uso\s+\|Fonte\s+\|\n\|-----------------------\|------------------------------------\|\n((?:\|.+\|.+\|\n)+)',
        file_content,
    )
    if typography_match:
        typography_raw = typography_match.group(1).strip().split('\n')
        instructions["typography"] = {}
        for line in typography_raw:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) == 2:
                instructions["typography"][parts[0]] = parts[1]

    # Visual Identity - Recurring Visual Elements
    visual_elements_match = re.search(r'### Elementos visuais recorrentes\n\n((?:- .+\n)+)', file_content)
    if visual_elements_match:
        instructions["visual_elements"] = [
            line.strip('- ').strip() for line in visual_elements_match.group(1).strip().split('\n')
        ]

    # Carousel Structure
    carousel_structure_match = re.search(
        r'## 3\\. ESTRUTURA PADRÃO DE UM CAROUSEL\n\nCada carousel deve ter entre \*\*6 e 8 slides\*\*, seguindo esta estrutura:\n\n\|Slide\s+\|Função\s+\|O que conter\s+\|\n\|-----------------------------------------\|--------------------------\|----------------------------------------------------------\|\n((?:\|.+\|.+\|.+\|\n)+)',
        file_content,
    )
    if carousel_structure_match:
        structure_raw = carousel_structure_match.group(1).strip().split('\n')
        instructions["carousel_structure"] = []
        for line in structure_raw:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) == 3:
                instructions["carousel_structure"].append({
                    "slide": parts[0],
                    "function": parts[1],
                    "content": parts[2],
                })

    # Copy Rules
    copy_rules_match = re.search(r'## 4\\. REGRAS DE COPY\n\n((?:\d+\. .+\n)+)', file_content)
    if copy_rules_match:
        instructions["copy_rules"] = [line.strip() for line in copy_rules_match.group(1).strip().split('\n')]

    # Editorial Calendar
    editorial_calendar_section_match = re.search(
        r'## 5\\. CALENDÁRIO EDITORIAL — 2 SEMANAS\n\n### \(6 posts no total — 3 por semana\)\n\n-----\n\n(.*?)(?:## 6\\. REGRAS DE GERAÇÃO DO MANUS|$)',
        file_content,
        re.DOTALL,
    )
    if editorial_calendar_section_match:
        editorial_calendar_content = editorial_calendar_section_match.group(1)
        instructions["editorial_calendar"] = []

        weeks_raw = re.split(r'### SEMANA \d\s*\n\n', editorial_calendar_content)
        weeks_raw = [week for week in weeks_raw if week.strip()]

        for week_content in weeks_raw:
            posts_raw = re.findall(
                r'\*\*Post \d — (.+?)\*\*\s*\n- \*\*Tema:\*\* \*(.+?)\*\s*\n- \*\*Ângulo:\*\* (.+?)\s*\n- \*\*Referências:\*\* (.+?)\s*\n- \*\*Hook da capa:\*\* \*[""](.+?)[""]\*\*\s*\n- \*\*Tom:\*\* (.+?)\s*\n',
                week_content,
                re.DOTALL,
            )
            for post_data in posts_raw:
                instructions["editorial_calendar"].append({
                    "day": post_data[0].strip(),
                    "theme": post_data[1].strip(),
                    "angle": post_data[2].strip(),
                    "references": post_data[3].strip(),
                    "hook": post_data[4].strip(),
                    "tone": post_data[5].strip(),
                })

    # Manus Generation Rules
    manus_rules_match = re.search(r'## 6\\. REGRAS DE GERAÇÃO DO MANUS\n\n((?:\d+\. .+\n)+)', file_content)
    if manus_rules_match:
        instructions["manus_generation_rules"] = [
            line.strip() for line in manus_rules_match.group(1).strip().split('\n')
        ]

    # What Never To Do
    never_do_match = re.search(r'## 7\\. O QUE NUNCA FAZER\n\n((?:- .+\n)+)', file_content)
    if never_do_match:
        instructions["what_never_to_do"] = [
            line.strip('- ').strip() for line in never_do_match.group(1).strip().split('\n')
        ]

    return instructions


if __name__ == '__main__':
    import sys

    input_path = sys.argv[1] if len(sys.argv) > 1 else '/home/ubuntu/upload/Pasted_content.txt'
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'parsed_instructions.json'

    with open(input_path, 'r') as f:
        content = f.read()

    parsed_data = parse_instructions(content)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(parsed_data, f, ensure_ascii=False, indent=4)

    print(f"Instructions parsed and saved to {output_path}")
