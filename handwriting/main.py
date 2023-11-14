import os
from globals import config
from pathlib import Path
import logging

import numpy as np
import svgwrite


from . import drawing
from .rnn import rnn

TMP_DIR = config['TMP']['DIR']
TMP_FILENAME = config['TMP']['FILENAME']
MARGIN = int(config['PAPER']['MARGIN'])
PAPER_WIDTH = int(config['PAPER']['WIDTH'])
PAPER_HEIGHT = int(config['PAPER']['HEIGHT'])


class Hand(object):

    def __init__(self):
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        self.nn = rnn(
            log_dir='handwriting/logs',
            checkpoint_dir='handwriting/checkpoints',
            prediction_dir='handwriting/predictions',
            learning_rates=[.0001, .00005, .00002],
            batch_sizes=[32, 64, 64],
            patiences=[1500, 1000, 500],
            beta1_decays=[.9, .9, .9],
            validation_batch_size=32,
            optimizer='rms',
            num_training_steps=100000,
            warm_start_init_step=17900,
            regularization_constant=0.0,
            keep_prob=1.0,
            enable_parameter_averaging=False,
            min_steps_to_checkpoint=2000,
            log_interval=20,
            logging_level=logging.CRITICAL,
            grad_clip=10,
            lstm_size=400,
            output_mixture_components=20,
            attention_mixture_components=10
        )
        self.nn.restore()

    def write(self, write_file: bool, lines, biases=None, styles=None, stroke_colors=None, stroke_widths=None, line_spacings=None):
        valid_char_set = set(drawing.alphabet)
        for line_num, line in enumerate(lines):
            if len(line) > 75:
                raise ValueError(
                    (
                        "Each line must be at most 75 characters. "
                        "Line {} contains {}"
                    ).format(line_num, len(line))
                )

            for char in line:
                if char not in valid_char_set:
                    raise ValueError(
                        (
                            "Invalid character {} detected in line {}. "
                            "Valid character set is {}"
                        ).format(char, line_num, valid_char_set)
                    )

        strokes = self._sample(lines, biases=biases, styles=styles)
        return self._draw(strokes, lines, write_file, stroke_colors=stroke_colors, stroke_widths=stroke_widths, line_spacings=line_spacings)

    def _sample(self, lines, biases=None, styles=None):
        num_samples = len(lines)
        max_tsteps = 40*max([len(i) for i in lines])
        biases = biases if biases is not None else [0.5]*num_samples

        x_prime = np.zeros([num_samples, 1200, 3])
        x_prime_len = np.zeros([num_samples])
        chars = np.zeros([num_samples, 120])
        chars_len = np.zeros([num_samples])

        if styles is not None:
            for i, (cs, style) in enumerate(zip(lines, styles)):
                x_p = np.load(
                    'handwriting/styles/style-{}-strokes.npy'.format(style))
                c_p = np.load(
                    'handwriting/styles/style-{}-chars.npy'.format(style)).tostring().decode('utf-8')

                c_p = str(c_p) + " " + cs
                c_p = drawing.encode_ascii(c_p)
                c_p = np.array(c_p)

                x_prime[i, :len(x_p), :] = x_p
                x_prime_len[i] = len(x_p)
                chars[i, :len(c_p)] = c_p
                chars_len[i] = len(c_p)

        else:
            for i in range(num_samples):
                encoded = drawing.encode_ascii(lines[i])
                chars[i, :len(encoded)] = encoded
                chars_len[i] = len(encoded)

        [samples] = self.nn.session.run(
            [self.nn.sampled_sequence],
            feed_dict={
                self.nn.prime: styles is not None,
                self.nn.x_prime: x_prime,
                self.nn.x_prime_len: x_prime_len,
                self.nn.num_samples: num_samples,
                self.nn.sample_tsteps: max_tsteps,
                self.nn.c: chars,
                self.nn.c_len: chars_len,
                self.nn.bias: biases
            }
        )
        samples = [sample[~np.all(sample == 0.0, axis=1)]
                   for sample in samples]
        return samples

    def _draw(self, strokes, lines, write_file: bool, stroke_colors=None, stroke_widths=None, line_spacings=None):
        stroke_colors = stroke_colors or ['black']*len(lines)
        stroke_widths = stroke_widths or [2]*len(lines)
        line_spacings = line_spacings or [1]*len(lines)

        x_min, x_max = [0,0]
        h_max = 0
        for i, offsets in enumerate(strokes):
            # offsets[:, :2] *= scale_factor
            strokes[i] = drawing.offsets_to_coords(offsets)
            strokes[i] = drawing.denoise(strokes[i])
            strokes[i][:, :2] = drawing.align(strokes[i][:, :2])
            strokes[i][:, 1] *= -1

            x_max = max(x_max, np.max(strokes[i][:,0]))
            x_min = min(x_min, np.min(strokes[i][:,0]))
            h_max = max(h_max, 8*strokes[i][:,1].std())
            
        text_width = x_max - x_min
        scale_factor = (PAPER_WIDTH - MARGIN) / text_width
        line_height = h_max * scale_factor
        view_height = line_height * (len(strokes)) * np.mean(line_spacings)+ MARGIN

        if view_height > PAPER_HEIGHT:
           raise ValueError('Message too long, overflowing paper length')

        dwg = svgwrite.Drawing(filename=Path(TMP_DIR, f'{TMP_FILENAME}.svg').absolute().as_posix())
        dwg.viewbox(width=PAPER_WIDTH, height=view_height)
        dwg.add(dwg.rect(insert=(0, 0), size=(PAPER_WIDTH, view_height), fill='white'))

        last_final_coord = np.array([0, 0, 1.0])
        initial_coord = np.array([0, -MARGIN/2])
        for line_strokes, line, color, width, spacing in zip(strokes, lines, stroke_colors, stroke_widths, line_spacings):
            # if line is empty, add empty space and go to next
            if not line:
                initial_coord[1] -= line_height * spacing
                continue

            line_strokes[:,:2] *= scale_factor
            line_strokes[:, :2] -= line_strokes[:, :2].min() + initial_coord
            line_strokes[:, 0] += MARGIN / 2 - 2
            #line_strokes[:, 0] += (view_width - line_strokes[:, 0].max()) / 2

            prev_eos = 1.0
            p = "M{},{} ".format(*last_final_coord[:2])
            for x, y, eos in zip(*line_strokes.T):
                p += '{}{},{} '.format('M' if prev_eos == 1.0 else 'L', x, y)
                prev_eos = eos
            path = svgwrite.path.Path(p)
            path = path.stroke(color=color, width=width,
                               linecap='round').fill("none")
            dwg.add(path)
            initial_coord[1] -= line_height * spacing
            last_final_coord = line_strokes[-1, :]
        if write_file: dwg.save()
        return dwg.tostring()


hand = Hand()
