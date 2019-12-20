# There should be no empty string in the list
list = ['W', 'AY',  'SH', 'UH', 'D',  'W', 'AH', 'N', 'HH', 'AO', 'L', 'T', 'AA', 'N', 'DH', 'AH',  'W', 'EY']
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
