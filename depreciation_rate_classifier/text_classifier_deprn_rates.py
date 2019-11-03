# 6 December 2017 - Robert Li <robertwli@gmail.com>


import pandas as pd
import os
from sklearn import preprocessing
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import cross_val_predict
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import wordpunct_tokenize
from nltk.corpus import wordnet as wn
from functools import lru_cache
from nltk.tag.perceptron import PerceptronTagger


class DeprnPredictor:
    def __init__(self):
        # Load data
        self.dir = os.path.join('depreciation_rate_classifier', 'data_training')
        self.account_meanings = pd.read_csv(os.path.join('depreciation_rate_classifier', 'account_meanings.csv'),
                                            index_col='account')

        all_files = os.listdir(self.dir)
        for file in all_files:
            if file == ".DS_Store":
                all_files.remove(file)
            if '$' in file:
                all_files.remove(file)

        dfs = []
        for file in all_files:
            if '.csv' in file:
                dfs.append(pd.read_csv(os.path.join(self.dir, file)).dropna())
            if '.xls' in file:
                dfs.append(pd.read_excel(os.path.join(self.dir, file)).dropna())
        self.data_training = pd.concat(dfs, ignore_index=True)  # Ensures one long index in DF object.

        # Preprocess classifier labels (i.e. turn accounts into ints)
        # See http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.LabelEncoder.html
        self.le = preprocessing.LabelEncoder()
        self.le.fit(self.data_training.account)
        self.data_training = self.data_training.assign(target=pd.Series(self.le.transform(self.data_training.account)))
        # lower case everything to reduce errors
        self.data_training['description'] = self.data_training['description'].str.lower()

        # Initiate lemmatizer - idea from:
        # https://joaorafaelm.github.io/blog/text-classification-with-python
        self.wnl = WordNetLemmatizer()

        # Load tagger pickle
        self.tagger = PerceptronTagger()

        # Lookup if tag is noun, verb, adverb or an adjective
        self.tags = {'N': wn.NOUN, 'V': wn.VERB, 'R': wn.ADV, 'J': wn.ADJ}

        # Memoization of POS tagging and Lemmatizer
        self.lemmatize_mem = lru_cache(maxsize=10000)(self.wnl.lemmatize)
        self.tagger_mem = lru_cache(maxsize=10000)(self.tagger.tag)

        self.pipeline = self._create_trained_model()

    # POS tag sentences and lemmatize each word
    def tokenizer(self, text):
        for token in wordpunct_tokenize(text):
            if token not in ENGLISH_STOP_WORDS:
                tag = self.tagger_mem(frozenset({token}))
                yield self.lemmatize_mem(token, self.tags.get(tag[0][1],  wn.NOUN))

    def _create_trained_model(self):
        # Pipeline definition
        pipeline = Pipeline([
            ('vectorizer', TfidfVectorizer(
                tokenizer=self.tokenizer,
                ngram_range=(1, 2),
                stop_words=ENGLISH_STOP_WORDS,
                sublinear_tf=True,
                min_df=0.00009
            )),
            ('classifier', SGDClassifier(loss='hinge',
                                         penalty='l2',
                                         alpha=1e-4,
                                         random_state=42,
                                         max_iter=5,
                                         tol=None)),
        ])

        pipeline.fit(self.data_training.description, self.data_training.target)
        # issues with pickle de-serialisation this given the lemmatize is in memory
        # joblib.dump(self.pipeline, os.path.join(self.save_dir, self.trained_model))
        return pipeline

    def predict_description(self, user_description):
        # self.pipeline = joblib.load(self.save_dir + self.trained_model)
        predicted = self.pipeline.predict([user_description])
        predicted_account = self.le.inverse_transform(predicted)[0]
        return self.account_meanings.loc[predicted_account], predicted_account

    def report_results(self):
        # Cross validate using k-fold
        y_pred = cross_val_predict(
            self.pipeline, self.data_training['description'],
            y=self.data_training['target'],
            cv=10, n_jobs=1, verbose=20
        )

        # Compute precison, recall and f1 score.
        cr = classification_report(
            self.data_training['target'], y_pred, target_names=list(self.le.classes_),
            digits=3
        )

        print('-------------------------------------------------------------\n')
        print('Cross validate using k-fold results\n')
        print(cr)
        print('=============================================================\n')

        # Evaluate using all data for training and testing
        self.pipeline.fit(self.data_training.description, self.data_training.target)
        predicted = self.pipeline.predict(self.data_training.description)

        # Compute precison, recall and f1 score.
        cr = classification_report(
            self.data_training.target, predicted, target_names=list(self.le.classes_),
            digits=3
        )
        print('-------------------------------------------------------------\n')
        print('Evaluate using all data for training and testing.\n')
        print(cr)
        print('Accuracy: \n')
        print(accuracy_score(self.data_training.target, predicted))
        print('=============================================================\n')
