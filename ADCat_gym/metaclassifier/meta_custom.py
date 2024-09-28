# work pipline:
# 1. fit a meta predictor with catboost, save the model
# 2. generate meta-feature of uploaded datasets
# 3. test all components with the meta feature, la, return the best components
# 4. train with the best components, return the anomaly score

import time
import os
import sys; sys.path.append('..')

import catboost
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ast
from sklearn import preprocessing
from torch import nn
import torch
from torch.utils.data import Subset, DataLoader, TensorDataset
from tqdm import tqdm
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from joblib import dump, load


from ADCat_gym.data_generator import DataGenerator
from ADCat_gym.gen_meta_features import generate_meta_features
from ADCat_gym.utils import Utils
import xgboost as xgb
from ADCat_gym.components import Components

class meta_custom():
    def __init__(self,
                 seed:int = 1,
                 metric: str='AUCPR',
                 suffix: str='',
                 grid_mode: int='large',
                 grid_size: int=1000,
                 test_dataset_path: str=None,
                 model_name: str=None,
                 meta_predictor_save_path: str=None):

        # base
        self.seed = seed
        self.metric = metric
        self.grid_mode = grid_mode
        self.grid_size = grid_size
        self.suffix = suffix

        self.test_dataset_path = test_dataset_path # uploaded by the user , test dataset path

        self.utils = Utils()
        self.data_generator = DataGenerator()
        self.model_name = model_name # [xgboost,catboost]

        self.utils.set_seed(self.seed)
        self.device = self.utils.get_device()

        self.meta_predictor_save_path = meta_predictor_save_path # save the meta predictor

    def components_process(self, result):
        assert isinstance(result, pd.DataFrame)

        # we only compare the differences in diverse components
        components_list = [ast.literal_eval(_) for _ in result['Components']] # list of dict
        keys = list(ast.literal_eval(result['Components'][0]).keys())
        keys_diff = []

        for k in keys:
            options = [str(_[k]) for _ in components_list if _[k] is not None]
            # delete components that only have unique or None value
            if len(set(options)) == 1 or len(options) == 0:
                continue
            else:
                keys_diff.append(k)

        # save components as dataframe
        components_list_diff = []
        for c in components_list:
            components_list_diff.append({k: c[k] for k in keys_diff})

        components_df = pd.DataFrame(components_list_diff)
        components_df = components_df.replace([None], 'None')
        # 2022.03.14
        components_df = components_df.fillna('None')
        components_df = components_df.astype('str')

        # encode components to int index for preparation
        components_df_index = components_df.copy()
        for col in components_df_index.columns:
            components_df_index[col] = preprocessing.LabelEncoder().fit_transform(components_df_index[col])

        return components_list, components_df_index

    def meta_fit(self):
        # generate training data for meta predictor
        meta_features, las, components, performances = [], [], [], []

        for la in [5, 10, 20]:
            result = pd.read_csv('ADCat_gym/result/result-' + self.metric + '-test-' + '-'.join(
                [self.suffix, str(la), self.grid_mode, str(self.grid_size), str(self.seed)]) + '.csv')
            result.rename(columns={'Unnamed: 0': 'Components'}, inplace=True)

            # using the rank ratio as target
            for i in range(1, result.shape[1]):
                r = np.argsort(np.argsort(-result.iloc[:, i].fillna(0).values))
                result.iloc[:, i] = r / result.shape[0]

            # transform result dataframe for preparation
            self.components_list, self.components_df_index = self.components_process(result)

            for i in range(result.shape[0]):
                for j in range(1, result.shape[1]):
                    if not pd.isnull(result.iloc[i, j]):  # set nan to 0?
                        meta_feature = np.load(
                            'ADCat_gym/datasets/meta-features/' + 'meta-features-' + result.columns[j] + '-' + str(
                                la) + '-' + str(self.seed) + '.npz', allow_pickle=True)

                        # preparing training data for meta classifier
                        # note that we only extract meta features in training set of both training & testing tasks
                        meta_features.append(meta_feature['data'])
                        las.append(la)
                        components.append(self.components_df_index.iloc[i, :].values)
                        performances.append(result.iloc[i, j])

        del la

        meta_features = np.stack(meta_features)
        components = np.stack(components)

        # fillna in extracted meta-features
        meta_features = pd.DataFrame(meta_features).fillna(0).values
        # min-max scaling for meta-features
        self.scaler_meta_features = MinMaxScaler(clip=True).fit(meta_features)
        dump(self.scaler_meta_features, f'{self.meta_predictor_save_path}/scaler_meta_features.joblib')
        meta_features = self.scaler_meta_features.transform(meta_features)
        # min-max scaling for la
        las = np.array(las).reshape(-1, 1)

        X = np.concatenate((meta_features, las, components), axis=1)

        if self.model_name == 'XGBoost':
            self.model = xgb.XGBRegressor(random_state=self.seed).fit(X, performances)
            self.model.save_model(f'{self.meta_predictor_save_path}/meta-predictor_xgb.bin')
        elif self.model_name == 'CatBoost':
            self.model = catboost.CatBoostRegressor(random_state=self.seed,verbose=False).fit(X, performances)
            self.model.save_model(f'{self.meta_predictor_save_path}/meta-predictor_catb.cbm', format='cbm')
        else:
            raise NotImplementedError

    def get_meta_predictor(self):
        if self.model_name == 'XGBoost':
            self.model = xgb.XGBRegressor()
            self.model.load_model(f'{self.meta_predictor_save_path}/meta-predictor_xgb.bin')
        elif self.model_name == 'CatBoost':
            self.model = catboost.CatBoostRegressor(verbose=False)
            self.model.load_model(f'{self.meta_predictor_save_path}/meta-predictor_catb.cbm')
        else:
            raise NotImplementedError

    def meta_predict(self): # return the best components
        # test-dataset_df:      ....,label
        if self.test_dataset_path.endswith(".xlsx"):
            self.test_dataset_df = pd.read_excel(self.test_dataset_path, sheet_name='Sheet1')
        elif self.test_dataset_path.endswith(".csv"):
            try:
                self.test_dataset_df = pd.read_csv(self.test_dataset_path,encoding='gbk')
            except:
                self.test_dataset_df = pd.read_csv(self.test_dataset_path)
        y = self.test_dataset_df['label'].values
        X = self.test_dataset_df.drop('label', axis=1).values
        self.test_la = sum(y)

        # get components_list
        result = pd.read_csv('ADCat_gym/result/result-' + self.metric + '-test-' + '-'.join(
                [self.suffix, '5', self.grid_mode, str(self.grid_size), str(self.seed)]) + '.csv')
        result.rename(columns={'Unnamed: 0': 'Components'}, inplace=True)
        self.components_list, self.components_df_index = self.components_process(result)

        # 1. meta-feature for testing dataset
        meta_feature_test, _ = generate_meta_features(X)
        # meta_feature_test = meta_feature_test['data']
        meta_feature_test = np.stack([meta_feature_test for i in range(self.components_df_index.shape[0])])
        meta_feature_test = pd.DataFrame(meta_feature_test).fillna(0).values
        self.scaler_meta_features = load(f'{self.meta_predictor_save_path}/scaler_meta_features.joblib')
        meta_feature_test = self.scaler_meta_features.transform(meta_feature_test)

        # 2. number of labeled anomalies in testing dataset
        la_test = np.repeat(self.test_la, self.components_df_index.shape[0]).reshape(-1, 1)

        # 3. components (predefined)
        components_test = self.components_df_index.values

        X_test = np.concatenate((meta_feature_test, la_test, components_test), axis=1)

        # predicting
        pred = self.model.predict(X_test)
        gym = self.components_list[np.argmin(pred)]

        return gym
    
    def predict_gym(self,gym):
        y = self.test_dataset_df['label'].values
        X = self.test_dataset_df.drop('label', axis=1).values
        data = {'X_train':X,'y_train':y,'X_test':X,'y_test':y} # the native model, without split training and test dataset
        

        com = Components(seed=self.seed,
                            data=data.copy(),
                            augmentation=gym['augmentation'],
                            preprocess=gym['preprocess'],
                            network_architecture=gym['network_architecture'],
                            hidden_size_list=gym['hidden_size_list'],
                            act_fun=gym['act_fun'],
                            dropout=gym['dropout'],
                            network_initialization=gym['network_initialization'],
                            training_strategy=gym['training_strategy'],
                            loss_name=gym['loss_name'],
                            optimizer_name=gym['optimizer_name'],
                            batch_resample=gym['batch_resample'],
                            epochs=gym['epochs'],
                            batch_size=gym['batch_size'],
                            lr=gym['lr'],
                            weight_decay=gym['weight_decay'])

        # training
        start_time = time.time()
        com.f_train()
        end_time = time.time()
        fit_time = end_time - start_time

        # predicting
        (score_train, score_test), (metrics_train, metrics_test) = com.f_predict_score()

        return fit_time,score_test



def run(test_dataset_path: str=None,):
    seed=1
    metric = 'AUCPR' #['AUCROC','AUCPR']
    grid_mode = 'large' #['large','small']
    grid_size = 1000
    model_name = 'XGBoost' #['XGBoost','CatBoost']
    meta_predictor_save_path = './meta-predictor_modelFile'
    suffix = 'formal'

    if os.path.exists(meta_predictor_save_path) is False:
        os.mkdir(meta_predictor_save_path)

    meta = meta_custom(seed=seed, metric=metric, grid_mode=grid_mode, suffix=suffix,
    grid_size=grid_size, test_dataset_path=test_dataset_path, model_name=model_name, meta_predictor_save_path=meta_predictor_save_path)

    isexists_meta_predictor = False
    if model_name == 'XGBoost' and os.path.exists(f'{meta_predictor_save_path}/meta-predictor_xgb.bin'):
        isexists_meta_predictor = True
    if model_name == 'CatBoost' and os.path.exists(f'{meta_predictor_save_path}/meta-predictor_catb.cbm'):
        isexists_meta_predictor = True
    if isexists_meta_predictor:
        meta.get_meta_predictor() # load the meta-predictor
    else:
        meta.meta_fit() # fit meta-predictor

    best_pipeline = meta.meta_predict()
    
    num_normal_train = len(meta.test_dataset_df['label'].values) - sum(meta.test_dataset_df['label'].values)
    
    if best_pipeline['batch_resample'] is True and best_pipeline['batch_size'] > num_normal_train:
        best_pipeline['batch_size'] = int(num_normal_train)

    fit_time, score_test = meta.predict_gym(best_pipeline)
    # scaler = MinMaxScaler()
    # score_test = score_test.reshape(-1,1)
    # score_test = scaler.fit_transform(score_test).flatten()
    score_test = [round(num, 3) for num in score_test]

    best_pipeline_list = list(best_pipeline.values())

    return best_pipeline_list, fit_time, score_test
    
# best_pipeline,fit_time,score_train = run('ADCat_gym/data_test.csv')
#
# print(best_pipeline,fit_time,score_train)
