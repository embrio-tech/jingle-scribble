from handwriting.main import hand

lines = ['The quick brown fox jumps over the lazy dog', 'and breaks a leg.', '', 'Oh, poor fox.']
biases = [0.6 for i in lines]
styles = [5 for i in lines] #[i for i, j in enumerate(lines)]  # 1
stroke_colors = ['black' for i in lines]
stroke_widths = [0.2 for i in lines]

hand.write(
        write_file=True,
        lines=lines,
        biases=biases,
        styles=styles,
        stroke_colors=stroke_colors,
        stroke_widths=stroke_widths,
    )