#!/usr/local/bin/python
import sys
import re

import theano
from theano import tensor
from theano.sandbox.rng_mrg import MRG_RandomStreams as RandomStreams

from nltk.tokenize import wordpunct_tokenize


import argparse

import numpy
import cPickle as pkl

from defgen_rev import build_fprop, \
                       load_params, \
                       init_params, \
                       init_tparams, \
                       zipp

def main(argv,
         model, 
         dictionary,
         embeddings,
         max_n=1000):

    # load model model_options
    with open('%s.pkl'%model, 'rb') as f:
        model_options = pkl.load(f)

    with open(dictionary, 'rb') as f:
        worddict = pkl.load(f)
    worddict_r = dict()
    for k, v in worddict.iteritems():
        worddict_r[v] = k
    worddict_r[0] = '<eos>'

    print >>sys.stderr, 'Loading skipgram vectors...',
    with open(embeddings, 'rb') as f:
        wv = pkl.load(f)
    wv_vectors = numpy.zeros((len(wv.keys()), wv.values()[0].shape[0]))
    wv_words = [None] * len(wv.keys())
    for ii, (kk, vv) in enumerate(wv.iteritems()):
        wv_vectors[ii,:] = vv
        wv_words[ii] = kk
    wv_vectors = wv_vectors / (numpy.sqrt((wv_vectors ** 2).sum(axis=1))[:,None])
    print >>sys.stderr, 'Done'

    trng = RandomStreams(1234)
    use_noise = theano.shared(numpy.float32(0.), name='use_noise')

    params = init_params(model_options)

    params = load_params(model, params)
    tparams = init_tparams(params)

    # word index
    f_prop = build_fprop(tparams, model_options, trng, use_noise)

    def process_line(line):
        if line != "":
            clueid,clue,length = '','',''
            try:
                clueid,clue,length = line.split('\t')
            except Exception as e:
                print line
            
            clue = clue.lower()
            words = wordpunct_tokenize(clue.strip())
            length = int(length)

            seq = [worddict[w] if w in worddict else 1 for w in words] + [0]

            vec = f_prop(numpy.array(seq).reshape([len(seq),1]).astype('int64'),
                         numpy.ones((len(seq),1)).astype('float32'))
            vec = vec / numpy.sqrt((vec ** 2).sum(axis=1))[:,None]
            sims = (wv_vectors * vec).sum(1)
            sorted_idx = sims.argsort()[::-1]

            answer_dict = {}
            i = 1
            for ii, s in enumerate(sorted_idx):
                if len(wv_words[s]) == length:
                    answer_dict[wv_words[s]] = sims[s]
                    if i >= max_n:
                        break
                    i += 1

            if len(answer_dict.keys()) > 0:
                for word in answer_dict:
                    print "\t".join([clueid,word,str(answer_dict[word])])

    if len(argv) == 2:
        for line in open(argv[1]).readlines():
            process_line(line)
    elif len(argv) == 1:
        for line in sys.stdin:
            process_line(line)
    

if __name__ == "__main__":
    model = '../models/reverse_merged_T4.npz'
    embeddings = '../models/D_cbow_pdw_8B.pkl'
    dictionary = '../models/Merged_dict_T4_train.pkl'

    main(sys.argv, model, dictionary=dictionary,embeddings=embeddings)








