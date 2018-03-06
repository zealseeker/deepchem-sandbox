import os, gc, time
import numpy as np
import pandas as pd
import deepchem as dc
from deepchem.models.tensorgraph.models.graph_models import GraphConvTensorGraph

def load_toxcast(filename,tasks):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    featurizer = 'GraphConv'
    if featurizer == 'ECFP':
        featurizer = dc.feat.CircularFingerprint(size=1024)
    elif featurizer == 'GraphConv':
        featurizer = dc.feat.ConvMolFeaturizer()
    # Load TOXCAST dataset
    loader = dc.data.CSVLoader(tasks=tasks, smiles_field='smiles',featurizer=featurizer)
    dataset = loader.featurize(filename,shard_size=8192)
    transformers = [
        dc.trans.BalancingTransformer(transform_w=True, dataset = dataset)
    ]
    for transformer in transformers:
        dataset = transformer.transform(dataset)
    return dataset, transformers

def main():
    tasks = np.load('tasks.npy').tolist()
    dataset, transformers = load_toxcast('toxcast_available.csv',tasks)
    valid_indice = np.load('index400.npy')
    y_preds = []
    y_trues = []
    i = 0
    n = len(valid_indice)
    for (train, test) in leave_one_out(len(dataset), valid_indice):
        start = time.clock()
        train_dataset = dataset.select(train, 'train_data')
        model = tf_graph_model(train_dataset, len(tasks), transformers)
        test_dataset = dataset.select(test,'test_data')
        y_preds.append(model.predict(test_dataset)[0][0])
        y_trues.append(list(next(test_dataset.itersamples()))[1])
        i += 1
        del model
        gc.collect()
        print('%d/%d' % (i,n))
        print "time consumption:",time.clock()-start,"The end!"	
        
    np.savetxt('y_true.csv',y_trues,fmt='%d',delimiter=',')
    np.savetxt('y_pred.csv',y_preds,fmt='%d',delimiter=',')
        



def leave_one_out(indice, valid_indice = None):
    if type(indice) == int:
        indice = range(indice)
    if valid_indice == None:
        valid_indice = indice
    for i,index in enumerate(valid_indice):
        train = set(valid_indice) | set(indice)
        train.remove(index)
        yield (train, [index]) 
    
def tf_graph_model(dataset, task_length, transformers=None, testset=None):
    # Batch size of models
    batch_size = 50
    model = GraphConvTensorGraph(task_length, batch_size=batch_size, mode='classification')
    model.fit(dataset, nb_epoch=10)
    return model

if __name__ == '__main__':
    main()