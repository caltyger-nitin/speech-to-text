from __future__ import absolute_import, division, print_function

import argparse
import numpy as np
import shlex
import subprocess
import sys
import wave
import json

from deepspeech import Model, printVersions
from timeit import default_timer as timer
import time

try:
    from shhlex import quote
except ImportError:
    from pipes import quote

def convert_samplerate(audio_path, desired_sample_rate):
    sox_cmd = 'sox {} --type raw --bits 16 --channels 1 --rate {} --encoding signed-integer --endian little --compression 0.0 --no-dither - '.format(quote(audio_path), desired_sample_rate)
    try:
        output = subprocess.check_output(shlex.split(sox_cmd), stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError('SoX returned non-zero status: {}'.format(e.stderr))
    except OSError as e:
        raise OSError(e.errno, 'SoX not found, use {}hz files or install it: {}'.format(desired_sample_rate, e.strerror))

    return desired_sample_rate, np.frombuffer(output, np.int16)


def metadata_to_string(metadata):
    return ''.join(item.character for item in metadata.items)


ds = Model('models/output_graph.pbmm', 500)    ### ds = Model(args.model, args.beam_width)

desired_sample_rate = ds.sampleRate()

lm = './models/lm.binary'
trie = './models/trie'
lm_alpha = 0.75
lm_beta = 1.85


ds.enableDecoderWithLM(lm, trie, lm_alpha, lm_beta)



def stt(audio):
	fin = wave.open(audio, 'rb')
	fs = fin.getframerate()

	if fs != desired_sample_rate:
		print('Warning: original sample rate ({}) is different than {}hz. Resampling might produce erratic speech recognition.'.format(fs, desired_sample_rate), file=sys.stderr)
		fs, audio = convert_samplerate(audio, desired_sample_rate)
	else:
		audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)


	audio_length = fin.getnframes() * (1/fs)
	fin.close()

	print('Running inference.', file=sys.stderr)


	t0=time.time()
	text = ds.stt(audio)
	print('total stt time = ',time.time()-t0)
	return text

# specifying the path for audio file
audio = '/home/caltyger/Downloads/DeepSpeech-master/ewm.wav'

text = stt(audio)

# print('the output is')
print(text)



from g2p_en import G2p

g2p = G2p()
out = g2p(text)

print(out)

list = []

for phoneme in out:
    # print(phoneme[-1])
    if phoneme[-1] == '0' or phoneme[-1] == '1' or phoneme[-1] == '2':
        phoneme = phoneme[:-1]
        list.append(phoneme.lower())
    elif phoneme == ' ':
        print('kuch nahi bs yun hi')
    else:
        list.append(phoneme.lower())
print(list)


list2 = []
list3 = []
list2.append('sil')
list3.append('sil')
for word in list:
        word = word.lower()
        text3 = '<'+word+'>'
        list3.append(text3)
        list2.append(word)
list2.append('[ sil ] ')
list3.append('[ sil ] ;')
phoneme = " ".join(word for word in list2)
# print(phoneme)
text = "why should one halt on the way"
from jsgf import PublicRule, Literal, Grammar


rule = PublicRule("why", Literal(phoneme))
grammar = Grammar("forcing")
grammar.add_rule(rule)
align_file = 'why-align.jsgf'
grammar.compile_to_file(align_file)

text2 = 'sil '+text+' [ sil ] '
rule2 = PublicRule("wholeutt", Literal(text2))
grammar2 = Grammar("word")
grammar2.add_rule(rule2)
words_file = "why-words.jsgf"
grammar2.compile_to_file(words_file)

phoneme_final = " ".join(word for word in list3)

phoneme_final = phoneme_final + "\n\n<aa> = aa | ah | er | ao;\n<ae> = ae | eh | er | ah;\n<ah> = ah | ae | er | aa;\n<ao> = ao | aa | er | uh;\n<aw> = aw | aa | uh | ow;\n<ay> = ay | aa | iy | oy | ey;\n<b> = b | p | d;\n<ch> = ch | sh | jh | t;\n<dh> = dh | th | z | v;\n<d> = d | t | jh | g | b;\n<eh> = eh | ih | er | ae;\n<er> = er | eh | ah | ao;\n<ey> = ey | eh | iy | ay;\n<f> = f | hh | th | v;\n<g> = g | k | d;\n<hh> = hh | th | f | p | t | k;\n<ih> = ih | iy | eh;\n<iy> = iy | ih;\n<jh> = jh | ch | zh | d;\n<k> = k | g | t | hh;\n<l> = l | r | w;\n<m> = m | n;\n<ng> = ng | n;\n<n> = n | m | ng;\n<ow> = ow | ao | uh | aw;\n<oy> = oy | ao | iy | ay;\n<p> = p | t | b | hh;\n<r> = r | y | l;\n<ss> = sh | s | z | th;\n<sh> = sh | s | zh | ch;\n<t> = t | ch | k | d | p | hh;\n<th> = th | s | dh | f | hh;\n<uh> = uh | ao | uw | uw;\n<uw> = uw | uh | uw;\n<v> = v | f | dh;\n<w> = w | l | y;\n<y> = y | w | r;\n<z> = z | s | dh | z;\n<zh> = zh | sh | z | jh"
rule3 = PublicRule("why", Literal(phoneme_final))
grammar3 = Grammar("neighbors")
grammar3.add_rule(rule3)

neighbor_file = "why-neighbors.jsgf"
grammar3.compile_to_file(neighbor_file)

# Executing PocketSphinx Commands
import subprocess
import shlex
# How to execute commandline command from python files
audio = 'ewm.wav'

pocket_command = "pocketsphinx_continuous -infile {} -jsgf {} -dict phonemes.dict -backtrace yes -fsgusefiller no -bestpath no 2>&1 | tee {}-align.txt".format(audio, align_file, audio)
subprocess.run(pocket_command, shell = True)

pocket_command2 = "pocketsphinx_continuous -infile {} -jsgf {} -dict phonemes.dict -backtrace yes -fsgusefiller no -bestpath yes 2>&1 | tee {}-neighbors.txt".format(audio, neighbor_file, audio)
subprocess.run(pocket_command2, shell = True)

pocket_command3 = "pocketsphinx_continuous -infile {} -jsgf {} -dict words.dict -backtrace yes -fsgusefiller no -bestpath no 2>&1 | tee {}-words.txt".format(audio, words_file, audio)
subprocess.run(pocket_command3, shell = True)

allign_sentence = "|".join(word for word in list2[1:-1])
final_allign_command = "for f in *-align.txt ; do awk '/^({})  / ' $f >> alignments.txt ; done".format(allign_sentence)
subprocess.run(final_allign_command, shell = True)
