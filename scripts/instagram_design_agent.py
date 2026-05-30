#!/usr/bin/env python3
"""
Instagram Design Agent
Cria carrosséis para Instagram seguindo diretrizes de marca usando Claude + Canva.

Uso:
    python instagram_design_agent.py <guidelines.txt> "<tema>" [--model <model>]

Exemplos:
    python instagram_design_agent.py brand_guidelines.txt "Marketing Digital"
    python instagram_design_agent.py brand_guidelines.txt "Como usar IA" --model claude-opus-4-8

Variáveis de ambiente:
    CANVA_API_KEY  — chave da API do Canva (opcional; sem ela roda em modo simulação)
    ANTHROPIC_API_KEY — obrigatória
"""

import json
import os
import sys
import argparse
from pathlib import Path

import anthropic

sys.path.insert(0, str(Path(__file__).parent))
from parse_brand_guidelines import parse_instructions


DEFAULT_MODEL = "claude-opus-4-8"

SYSTEM_PROMPT = """\
Você é um especialista em design de carrosséis para Instagram.
Seu objetivo: criar carrosséis de 6 a 8 slides que seguem RIGOROSAMENTE as diretrizes de marca.

Fluxo obrigatório:
1. Analise o tema e as diretrizes de marca.
2. Planeje os slides (capa → problema → desenvolvimento → CTA).
3. Para cada slide, chame `generate_instagram_slide` com todos os parâmetros de design.
4. Após gerar todos os slides, chame `export_carousel` para finalizar.

Regras de copy:
- Headline do slide de capa: máx. 8 palavras, deve parar o scroll
- Corpo de cada slide: máx. 30 palavras (mobile-first)
- Último slide: sempre com CTA explícito (salvar / comentar / seguir)
- Tom de voz: siga exatamente o definido nas diretrizes

Nunca invente cores, fontes ou elementos fora das diretrizes fornecidas.\
"""

TOOLS = [
    {
        "name": "generate_instagram_slide",
        "description": (
            "Gera um slide 1080×1080px para carrossel de Instagram no Canva. "
            "Chame uma vez para cada slide, em ordem (1 = capa, último = CTA)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "slide_number": {
                    "type": "integer",
                    "description": "Posição do slide no carrossel (começa em 1)"
                },
                "slide_function": {
                    "type": "string",
                    "description": "Papel deste slide: Capa | Problema | Contexto | Solução | Dado | CTA"
                },
                "headline": {
                    "type": "string",
                    "description": "Texto principal (máx. 8 palavras)"
                },
                "body_text": {
                    "type": "string",
                    "description": "Texto de suporte, bullets ou chamada secundária (opcional)"
                },
                "background_color": {
                    "type": "string",
                    "description": "Cor de fundo em hex (ex: #1A1A2E), da paleta da marca"
                },
                "text_color": {
                    "type": "string",
                    "description": "Cor do texto principal em hex, da paleta da marca"
                },
                "font_headline": {
                    "type": "string",
                    "description": "Fonte do headline (conforme tipografia da marca)"
                },
                "font_body": {
                    "type": "string",
                    "description": "Fonte do corpo (conforme tipografia da marca)"
                },
                "visual_elements": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Elementos visuais recorrentes da marca a incluir"
                },
                "design_prompt": {
                    "type": "string",
                    "description": "Prompt completo descrevendo o design para o Canva"
                }
            },
            "required": [
                "slide_number", "slide_function", "headline",
                "background_color", "font_headline", "design_prompt"
            ]
        }
    },
    {
        "name": "export_carousel",
        "description": "Exporta todos os slides gerados como PNG 1080×1080px prontos para Instagram.",
        "input_schema": {
            "type": "object",
            "properties": {
                "design_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "IDs dos designs gerados, em ordem"
                },
                "output_format": {
                    "type": "string",
                    "enum": ["png", "jpg"],
                    "description": "Formato de exportação (padrão: png)"
                }
            },
            "required": ["design_ids"]
        }
    }
]


def _canva_generate(slide_input: dict, api_key: str) -> dict:
    """Call Canva API to generate a design. Returns design metadata."""
    import urllib.request

    payload = json.dumps({
        "design_type": "instagram-post",
        "title": f"Slide {slide_input['slide_number']} - {slide_input['slide_function']}",
        "query": slide_input["design_prompt"],
    }).encode()

    req = urllib.request.Request(
        "https://api.canva.com/rest/v1/designs",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def _canva_export(design_id: str, fmt: str, api_key: str) -> dict:
    """Export a Canva design and return download URL."""
    import urllib.request

    payload = json.dumps({"format": fmt}).encode()
    req = urllib.request.Request(
        f"https://api.canva.com/rest/v1/designs/{design_id}/exports",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def handle_tool_call(name: str, inputs: dict, canva_api_key: str | None) -> str:
    if name == "generate_instagram_slide":
        num = inputs["slide_number"]
        headline = inputs["headline"]
        fn = inputs["slide_function"]
        print(f"  [Slide {num}] {fn}: {headline}")

        if canva_api_key:
            try:
                result = _canva_generate(inputs, canva_api_key)
                design_id = result.get("design", {}).get("id", f"canva_{num}")
                return json.dumps({"design_id": design_id, "slide": num, "status": "created"})
            except Exception as e:
                return json.dumps({"error": str(e), "slide": num, "status": "failed"})

        # Simulation mode
        mock_id = f"sim_slide_{num}_{fn.lower()}"
        return json.dumps({
            "design_id": mock_id,
            "slide": num,
            "headline": headline,
            "background_color": inputs.get("background_color"),
            "font": inputs.get("font_headline"),
            "status": "simulated",
        })

    if name == "export_carousel":
        ids = inputs["design_ids"]
        fmt = inputs.get("output_format", "png")
        print(f"\n  [Export] {len(ids)} slides → {fmt.upper()}")

        if canva_api_key:
            urls = []
            for did in ids:
                try:
                    result = _canva_export(did, fmt, canva_api_key)
                    urls.append(result.get("job", {}).get("urls", [did])[0])
                except Exception:
                    urls.append(did)
            return json.dumps({"urls": urls, "format": fmt, "count": len(ids)})

        return json.dumps({
            "design_ids": ids,
            "format": fmt,
            "count": len(ids),
            "status": "simulated",
            "note": "Defina CANVA_API_KEY para exportação real",
        })

    return json.dumps({"error": f"Ferramenta desconhecida: {name}"})


def _brand_context_block(guidelines: dict) -> str:
    """Convert parsed guidelines dict to a readable context string."""
    parts = []

    if bc := guidelines.get("brand_context"):
        parts.append("## MARCA")
        for key, label in [
            ("name", "Nome"), ("tagline", "Tagline"), ("positioning", "Posicionamento"),
            ("tone_of_voice", "Tom de voz"), ("audience", "Público"),
        ]:
            if bc.get(key):
                parts.append(f"**{label}:** {bc[key]}")

    if cp := guidelines.get("color_palette"):
        parts.append("\n## PALETA DE CORES")
        for elem, color in cp.items():
            parts.append(f"- {elem}: {color}")

    if typo := guidelines.get("typography"):
        parts.append("\n## TIPOGRAFIA")
        for use, font in typo.items():
            parts.append(f"- {use}: {font}")

    if ve := guidelines.get("visual_elements"):
        parts.append("\n## ELEMENTOS VISUAIS")
        parts.extend(f"- {e}" for e in ve)

    if cs := guidelines.get("carousel_structure"):
        parts.append("\n## ESTRUTURA DO CARROSSEL")
        for s in cs:
            parts.append(f"- Slide {s['slide']}: {s['function']} → {s['content']}")

    if cr := guidelines.get("copy_rules"):
        parts.append("\n## REGRAS DE COPY")
        parts.extend(f"- {r}" for r in cr)

    if nd := guidelines.get("what_never_to_do"):
        parts.append("\n## NUNCA FAZER")
        parts.extend(f"- {i}" for i in nd)

    return "\n".join(parts)


def run_agent(topic: str, guidelines: dict, model: str = DEFAULT_MODEL) -> dict:
    canva_api_key = os.getenv("CANVA_API_KEY")
    client = anthropic.Anthropic()
    brand_context = _brand_context_block(guidelines)

    print(f"\nTema: {topic}")
    print(f"Modelo: {model}")
    print(f"Canva: {'API real' if canva_api_key else 'modo simulação'}\n")

    messages = [
        {
            "role": "user",
            "content": f"Crie um carrossel completo para Instagram sobre: **{topic}**\n\n{brand_context}",
        }
    ]

    designs = []

    while True:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            tools=TOOLS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            summary = next(
                (b.text for b in response.content if hasattr(b, "text")), ""
            )
            print(f"\nCarrossel criado: {len(designs)} slides")
            return {"topic": topic, "model": model, "designs": designs, "summary": summary}

        if response.stop_reason != "tool_use":
            break

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            result_str = handle_tool_call(block.name, block.input, canva_api_key)
            result_data = json.loads(result_str)
            if block.name == "generate_instagram_slide":
                designs.append(result_data)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result_str,
            })

        messages.append({"role": "user", "content": tool_results})

    return {"topic": topic, "designs": designs, "error": "Loop encerrado inesperadamente"}


def main():
    parser = argparse.ArgumentParser(description="Agente de design para Instagram")
    parser.add_argument("guidelines", help="Caminho para o arquivo de diretrizes da marca")
    parser.add_argument("topic", nargs="+", help="Tema do carrossel")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Modelo Claude (padrão: {DEFAULT_MODEL})")
    parser.add_argument("--output", default="carousel_output.json", help="Arquivo de saída JSON")
    args = parser.parse_args()

    guidelines_path = Path(args.guidelines)
    if not guidelines_path.exists():
        print(f"Erro: arquivo de diretrizes não encontrado: {guidelines_path}", file=sys.stderr)
        sys.exit(1)

    with open(guidelines_path, encoding="utf-8") as f:
        guidelines = parse_instructions(f.read())

    topic = " ".join(args.topic)
    result = run_agent(topic, guidelines, model=args.model)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nResultado salvo em: {args.output}")

    if result.get("summary"):
        print(f"\nResumo do agente:\n{result['summary']}")


if __name__ == "__main__":
    main()
