#! /usr/bin/env python3
import sys
import django
import os
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix, accuracy_score
from unidecode import unidecode
# from controle_precos import REGEX_LIST
from django.conf import settings

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'controle_precos.settings')
django.setup()
#print(settings)


class CategoryGuesser:
    def __init__(self):
        self.classifier = GaussianNB()
        self.cv = CountVectorizer(max_features=3000)
        self.ps = PorterStemmer()
        nltk.download('stopwords')
        self.all_stopwords = stopwords.words("portuguese")

    def predict_cat(self, product: str):

        df4corpus = []

        words = product.split()
        words = [
            unidecode(self.ps.stem(word)) for word in words if word not in self.all_stopwords
        ]
        words = ' '.join(words)

        df4corpus.append(words)

        new_X = self.cv.transform(df4corpus).toarray()

        new_Y_pred = self.classifier.predict(new_X)

        return settings.CATEGORY_DICT[new_Y_pred.tolist()[0]]

    def train_model(self, path2data):

        df = pd.read_csv(
            path2data,
            header=0,
            on_bad_lines="skip",
            names=["item", "categoria"]
        )

        print(df.shape)

        df = df[df["item"].str.split().str.len() < 13]

        # print(settings.REGEX_LIST)

        for expression in settings.REGEX_LIST:
            #df["item"] = df["item"].replace(regex=expression, value="")
            df["item"] = df["item"].apply(lambda x: re.sub(expression, "", x))
        
        # regexst = "[0-9]+ml"
        #print(df.groupby(["item"], as_index=False).first())

        # for i in df.loc[df["item"].str.contains("embalagem")]["item"]:
        #     print(i)
        # items_len = []
        # for i in df["item"]:
        #     print(i)
        #     items_len.append(len(i.split(" ")))

        # print(items_len)

        # print(df)

        # return None

        df4corpus = []

        for i in df['item']:
            words = i.split()
            words = [
                unidecode(self.ps.stem(word)) for word in words if word not in self.all_stopwords
            ]
            words = ' '.join(words)
            df4corpus.append(words)

        X = self.cv.fit_transform(df4corpus).toarray()
        y = df.iloc[:, -1].values
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=0
        )

        self.classifier.fit(X_train, y_train)
        

        # Built a custom X_test, Y_test
        corpus = []
        with open("/home/gustavo/Documentos/ML/real_testset.txt", "r") as input:
            for i in input.readlines()[:-1]:
                name = i.strip()
                # print(name)
                corr_nam = []
                if name not in corpus:
                    for expression in settings.REGEX_LIST:
                        if len(corr_nam) < 1:
                            corr = re.sub(expression, "", name)
                            corr_nam.append(corr)
                        else:
                            corr = re.sub(expression, "", corr_nam[-1])
                            corr_nam.append(corr)
                        # ...
                print(name)
                print(corr_nam)
                if len(corr_nam) > 1:
                    corpus.append(self.ps.stem(corr_nam[-1].strip()))

        print(corpus)

        # for expression in settings.REGEX_LIST:                    
        #     corpus_new = [re.sub(expression, "", name) for name in corpus]
        # print(corpus_new)

        realXtest = self.cv.transform(corpus).toarray()

        y_pred = self.classifier.predict(realXtest)
        # print(X_test)
        # #print(np.concatenate((y_pred.reshape(len(y_pred),1), y_test.reshape(len(y_test),1)),1))

        print(y_pred)
        # print(type(y_test))

        # cm = confusion_matrix(y_test, y_pred)
        # print(cm)
        # acc = accuracy_score(y_test, y_pred)

        # print(acc)
        # print(len(X))

        return 'Model Trained'


def main():
    """
    In [1]: lista_de_produtos = []
       ...: with open("/home/gustavo/Documentos/lista_items.txt", 'w') as fh:
       ...:     for item in db.execute_sql('select * from notas_fiscais_itemnotafiscal').fetchall():
       ...:         _, _, _, produto, _, _, _ = item
       ...:         if produto not in lista_de_produtos:
       ...:             lista_de_produtos.append(produto)
       ...:             fh.write(f'{produto.lower()}\n')
    """
    # categorias destes dados foram colocadas manualmente para treinar o modelo

    """
    sed -E 's/[0-9]?kg|[0-9],[0-9]kg|[0-9]{2,}g|[0-9]{1,}ml|[0-9]+l|[0-9]*un//gim' items_cat.csv | 
    sed 's/ ,/,/g' | 
    awk '{print tolower($0)}' | 
    sort -k1 | 
    uniq > items_cat_uniq.csv
    """

    guesser = CategoryGuesser()

    guesser.train_model(
        path2data='/home/gustavo/Documentos/ML/raw_muffato_data/all_items_muffato.csv'
    )

    # pred = guesser.predict_cat(product=str(sys.argv[1]))

    # print(pred)


if __name__ == '__main__':
    main()
