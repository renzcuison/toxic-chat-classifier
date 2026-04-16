import pandas as pd
import re
import math
from collections import Counter
from itertools import chain

class ToxicChatClassifier:
    def __init__(self, alpha=1.0, threshold=2.0):
        self.alpha = alpha
        self.threshold = threshold
        self.toxic_log_probs = {}
        self.clean_log_probs = {}
        self.default_toxic_log_prob = 0
        self.default_clean_log_prob = 0
        self.priors = {'toxic': 0, 'clean': 0}

    def normalize_slang(self, text):
        text = str(text).lower()
        replacements = {
            r'\bur\b': 'you are', r'\bu\b': 'you', r'\br\b': 'are',
            r'\bpls\b': 'please', r'\bgg\b': 'good game', r'\bafk\b': 'away',
            r'\bmy bad\b': 'my mistake'
        }
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text)
        return text

    def get_features(self, text):
        """Generates both Unigrams and Bigrams for contextual awareness."""
        text = self.normalize_slang(text)
        tokens = re.sub(r'[^a-z0-9\s]', '', text).split()

        bigrams = [" ".join(tokens[i:i+2]) for i in range(len(tokens)-1)]

        return tokens + bigrams

    def train(self, df):
        train_toxic = df[df['toxic'] == 1]['comment_text'].dropna().apply(self.get_features)
        train_clean = df[df['toxic'] == 0]['comment_text'].dropna().apply(self.get_features)

        toxic_feature_list = list(chain.from_iterable(train_toxic))
        clean_feature_list = list(chain.from_iterable(train_clean))

        toxic_freq = Counter(toxic_feature_list)
        clean_freq = Counter(clean_feature_list)

        total_toxic_features = sum(toxic_freq.values())
        total_clean_features = sum(clean_freq.values())
        vocab = set(toxic_freq.keys()).union(set(clean_freq.keys()))
        vocab_size = len(vocab)

        self.priors['toxic'] = math.log(len(train_toxic) / len(df))
        self.priors['clean'] = math.log(len(train_clean) / len(df))

        self.toxic_log_probs = {w: math.log((toxic_freq.get(w, 0) + self.alpha) / (total_toxic_features + self.alpha * vocab_size)) for w in vocab}
        self.clean_log_probs = {w: math.log((clean_freq.get(w, 0) + self.alpha) / (total_clean_features + self.alpha * vocab_size)) for w in vocab}

        self.default_toxic_log_prob = math.log(self.alpha / (total_toxic_features + self.alpha * vocab_size))
        self.default_clean_log_prob = math.log(self.alpha / (total_clean_features + self.alpha * vocab_size))

    def predict(self, text):
        features = self.get_features(text)
        log_prob_toxic = self.priors['toxic']
        log_prob_clean = self.priors['clean']

        for f in features:
            log_prob_toxic += self.toxic_log_probs.get(f, self.default_toxic_log_prob)
            log_prob_clean += self.clean_log_probs.get(f, self.default_clean_log_prob)

        is_toxic = log_prob_toxic > (log_prob_clean + self.threshold)
        return ('TOXIC' if is_toxic else 'CLEAN'), {'toxic': log_prob_toxic, 'clean': log_prob_clean}

    def get_word_contributions(self, text):
        text = self.normalize_slang(text)
        tokens = re.sub(r'[^a-z0-9\s]', '', text).split()
        return [(t, self.toxic_log_probs.get(t, self.default_toxic_log_prob) -
                self.clean_log_probs.get(t, self.default_clean_log_prob)) for t in tokens]