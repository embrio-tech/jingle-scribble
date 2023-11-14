from globals import config
from pathlib import Path
from unidecode import unidecode
import openai
import textwrap
import re
from typing import List

from handwriting.main import hand
from xml.etree import ElementTree
from svg_to_gcode.svg_parser import parse_root, Transformation
from gcode import gcode_compiler

TMP_DIR = config['TMP']['DIR']
TMP_FILENAME = config['TMP']['FILENAME']
HANDWRITING_STYLE = int(config['HANDWRITING']['STYLE'])
HANDWRITING_BIAS = float(config['HANDWRITING']['BIAS'])

openai.api_key = config['OPENAI']['API_TOKEN']


def generate_content(recipient: str, context: str, language: str, style: str) -> str:
    prompt = f"""
    Think like a business developer of a small swiss software development agency specialized in cloud-native web applications named embrio.
    Write a max 400 characters Christmas card. Use a friendly, simple and positive writing style.

    Recipient: {recipient}

    Context information about the recipient:
    {context}

    Content of the card:
    - All the best ideas always start on paper.
    - The Christmas present is a high quality Swiss pen.
    - With it you can write up to eight km of ideas.
    - Whenever these are fit to be turned into digital products remember about us!
    - We are always happy to help.

    Language of the card: {language}
    Style of the card: {style}

    Add a P.S stating: 
    - This card was generated bi AI and written by a robot. Ain't that crazy? 
    - Visit xmas.embrio.tech to learn how we pulled this off.
    
    Don't justify your answers. Don't include or invent information not mentioned in the CONTEXT or CONTENT INFORMATION."""

    prompt = textwrap.dedent(prompt)
    print(prompt)

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "system", "content": prompt}])

    return response['choices'][0]['message']['content']

def format_content(text: str):
    text = unidecode(text).replace("Q", 'q').replace('Z', 'z')
    text = re.sub("\[(.*?)\]", "\n", text)
    text = re.sub("(\u00a9|\u00ae|[\u2000-\u3300]|\ud83c[\ud000-\udfff]|\ud83d[\ud000-\udfff]|\ud83e[\ud000-\udfff])", '', text)
    return text

def draw_svg(lines: List[str]):
    biases = [HANDWRITING_BIAS for i in lines]
    styles = [HANDWRITING_STYLE for i in lines]  # 1
    stroke_colors = ['black' for i in lines]
    stroke_widths = [0.2 for i in lines]
    line_spacings = [0.70 for i in lines]

    return hand.write(
        write_file=True,
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
    gcode = gcode_compiler.compile()
    with open(Path(TMP_DIR, f'{TMP_FILENAME}.gcode'), 'w') as file:
            file.write(gcode)
    return gcode

def new_card(recipient: str, context: str, language: str, chars_per_line) -> str:
    text = generate_content(recipient, context, language)
    text = format_content(text)
    lines = compute_lines(text, chars_per_line).split('\n')
    svg = draw_svg(lines)
    return compile_gcode(svg)
