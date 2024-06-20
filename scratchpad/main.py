import random

songs = ['a.mp3', 'b.mp3', 'c.mp3', 'd.mp3']
ranks = {}
matrix = {}

def score(i, j):
    update = [j]
    for k, v in matrix[i].items():
        if k == j: continue
        if v == 0: continue
        update.append(k)
    scr = 1 / len(update)
    for u in update:
        matrix[i][u] = scr
    return scr

# -- update weight matrix
for song in songs:
    # -- update ranks
    ranks[song] = 1/ len(songs)
    # --
    matrix[song] = dict()
    for inner in songs:
        matrix[song][inner] = 0

# -- sample play-queue flow
flow = [
    'a>b',
    'b>d',
    'd>a',
    'a>c',
    'd>b'
]
prev = None
for f in flow:
    if f[1] == '>':
        ref, cand = ['{}.mp3'.format(i) for i in f.split('>')]
        score(ref, cand)
        prev = (ref, cand)
    elif (f[1] == '<') and prev:
        ref, cand = prev
        matrix[ref][cand] = 0
        cand = '{}.mp3'.format(f[2])
        score(ref, cand)

# --
print(matrix)
updated = dict()
for song in ranks:
    updated[song] = 0
for song in ranks:
    for i in matrix:
        # print(song,matrix[i][song], i)
        updated[song] += ranks[i] * matrix[i][song]
    # --
ranks = updated
print(ranks)
