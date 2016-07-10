from __future__ import print_function
#from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from time import time
import numpy as np
import readPDF as readPDF
import RSOM as SOM
 
class DSOM(object):
    
    def __init__(self, inputFile=None, fileType=None, widthOfMap=2, useGPU=True):
        self.inputFile = inputFile
        self.fileType = fileType
        self.widthOfMap = widthOfMap
        self.useGPU = useGPU
        self.arrayTrain = []
        self.Y = None
        self.vectorizer = None
        self.nodeHolder = dict()
        self.text = ""
        self.dataset = ""
        
        
        
    def readDocument(self):
        if(self.fileType == 'pdf'):
            self.text = readPDF.pdfparser(self.inputFile)
        else:   
            self.text = open(self.inputFile, "r").read()    
        self.dataset = self.text.split("\n\n")         
        
    def train(self, inputFile=None):
        ###############################################################################
        #clean_file = open("data/paragraph_vector_output (copy).txt")
        #dataset = clean_file.read().split("\n\n")
    #     print(dataset)
    #     print("%d Paragraphs " % len(dataset))
    #     print()
    #     print("Extracting features from the dataset using a sparse vectorizer")
        #t0 = time()
        self.vectorizer = TfidfVectorizer(max_df=0.5, max_features=1000,
                                         min_df=2, stop_words='english',
                                         use_idf=True, sublinear_tf=True)
        self.Y = self.vectorizer.fit_transform(self.dataset)
        
        #arrayTrain = X.toarray()
        svd = TruncatedSVD(n_components=100, random_state=42)
        X = svd.fit_transform(self.Y)
        self.arrayTrain = X
        #print("done in %fs" % (time() - t0))
        #print("n_samples: %d, n_features: %d" % X.shape)
        #print()
        ###############################################################################
        ## SOM
        #For plotting the images
        
        #Train a 20x30 SOM with 400 iterations
        #print("<-- Starting SOM -- >")
        mapSide = self.widthOfMap
        som = SOM.SOM(DATA=self.arrayTrain, num_units=mapSide*mapSide, width=mapSide, height=mapSide)
        #print("<-- Training SOM -- >")
        #t0 = time()
        if(self.useGPU == True):
            try:
                import theano.sandbox.cuda
                theano.sandbox.cuda.use('gpu')
            except: 
                print("Switching to GPU didn't work, will fallback to CPU.")
            som.train_batch_theano(verbose=False)
        else:
            som.train_batch(verbose=False)
        #print("<-- Done Training SOM %fs -- >" %(time()-t0))
        #Get output grid
        #print("<-- Testing SOM -- >")
        #print("<-- Begin Output -- >")
        #np.set_printoptions(threshold='nan')
        clusters = som.ins_unit_assign
        #print(clusters)
        
        
        for i in range(mapSide*mapSide):
                self.nodeHolder[i] = []
                
        for i, m in enumerate(clusters):
            if (m) in self.nodeHolder:
                self.nodeHolder[m].append(i)
            else:
                self.nodeHolder[m] = [i]
    
    def getClusters(self):
        return self.nodeHolder
    
    def getDataset(self):
        return self.dataset
    
    def tfIDFArray(self):
        inverse = self.vectorizer.inverse_transform(self.Y)
        outList = []
        for x in inverse:
            outList.append([y.encode('UTF8') for y in x])
        return outList