import openai
import os
import textwrap
import re
from typing import List

from handwriting.main import hand
from xml.etree import ElementTree
from svg_to_gcode.svg_parser import parse_root, Transformation
from gcode import gcode_compiler

openai.api_key = os.getenv("OPENAI_API_TOKEN")

def generate_content(recipient: str, context: str, language: str) -> str:
    prompt = f"""
    Think like a business developer of a small swiss software development agency specialized in cloud-native web applications.
    Write a max 400 characters Christmas card. Use a friendly, simple and positive writing style.

    Recipient: {recipient}

    Context information about the recipient:
    {context}

    Content of the card:
    - The Christmas present is a pen.
    - All the best ideas always start on paper.
    - With this high quality Swiss pen you can write up to eight km of ideas on paper.
    - Whenever these are fit to become a product remember about us!
    - We are always here to help you transform them in amazing digital products.

    Language of the card: {language}

    Add a P.S stating that the card is written by artificial intelligence.
    Don't justify your answers. Don't include information not mentioned in the CONTEXT or CONTENT INFORMATION."""

    prompt = textwrap.dedent(prompt)
    print(prompt)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "system", "content": prompt}])

    return response['choices'][0]['message']['content']

def format_content(text: str):
    text = text.replace("ä", "a").replace("ü", "u").replace("ö", "o").replace('ß', 'ss').replace(
        "Q", 'q').replace('Z', 'z').replace('Ü', 'Ue').replace('à', 'a').replace('è', 'e')
    text = re.sub("\[(.*?)\]", "\n", text)
    text = re.sub(
        "(\u00a9|\u00ae|[\u2000-\u3300]|\ud83c[\ud000-\udfff]|\ud83d[\ud000-\udfff]|\ud83e[\ud000-\udfff])", '', text)
    return text

def draw_svg(lines: List[str]):
    biases = [0.8 for i in lines]
    styles = [3 for i in lines]  # 1
    stroke_colors = ['black' for i in lines]
    stroke_widths = [0.2 for i in lines]
    line_spacings = [0.70 for i in lines]

    return hand.write(
        filename='test.svg',
        lines=lines,
        biases=biases,
        styles=styles,
        stroke_colors=stroke_colors,
        stroke_widths=stroke_widths,
        line_spacings=line_spacings
    )

def compute_lines(text: str, chars: int = 70) -> str:
    l = 0
    lines = text.split('\n')
    while l < len(lines):
        line = lines[l]
        if len(line) > chars:
            i = chars - 1
            while line[i] != ' ':
                i -= 1
            next_line = line[i+1:]
            lines[l] = line[:i]
            lines.insert(l+1, next_line)
        l += 1
    return '\n'.join(lines)

def compile_gcode(svg: str) -> str:
    root = ElementTree.fromstring(svg)
    transform = Transformation()
    transform.add_scale(1, -1)
    curves = parse_root(root, False, None, False, True, transform)

    gcode_compiler.append_curves(curves)
    return gcode_compiler.compile()

def new_card(recipient: str, context: str, language: str, chars_per_line) -> str:
    text = generate_content(recipient, context, language)
    text = format_content(text)
    lines = compute_lines(text, chars_per_line).split('\n')
    svg = draw_svg(lines)
    return compile_gcode(svg)
