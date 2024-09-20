import warnings

import torch

warnings.filterwarnings('ignore')
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'  # 解决第二个错误
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
import pandas as pd
import numpy as np
from sklearn.utils import check_array
# 无监督的14种算法
from pyod.models.pca import PCA
from pyod.models.ocsvm import OCSVM
from pyod.models.lof import LOF
# from pyod.models.cblof import CBLOF
from pyod.models.cof import COF
from pyod.models.hbos import HBOS
from pyod.models.knn import KNN
from pyod.models.sod import SOD
from pyod.models.copod import COPOD
from pyod.models.ecod import ECOD
from pyod.models.deep_svdd import DeepSVDD
from adbench.baseline.DAGMM.run import DAGMM
from pyod.models.loda import LODA
from pyod.models.iforest import IForest

# 半监督的7种算法
from adbench.baseline.GANomaly.run import GANomaly
from adbench.baseline.DeepSAD.src.run import DeepSAD
from adbench.baseline.REPEN.run import REPEN
from adbench.baseline.DevNet.run import DevNet
from adbench.baseline.PReNet.run import PReNet
from adbench.baseline.FEAWAD.run import FEAWAD
from pyod.models.xgbod import XGBOD
# 有监督的9种算法
from adbench.baseline import Supervised
from adbench.baseline.Supervised import supervised
# from adbench.baseline.FTTransformer.run import FTTransformer(model_name = 'ResNet')
# from adbench.baseline.FTTransformer.run import FTTransformer


# 为测试而写
# def adbench_cal(filename, algo):
def adbench_cal(filename, algo, islabel):
    '''
    :param filename: 文件名，需要通过media索引访问读取文件；
    :param algo: 算法名，字符串；
    :param islabel: 标签列的名。取值为"无标签"或列索引；
    :return: score分数
    '''

    default_road = 'media/adbench/'  # 文件存储的相对路径
    load_path = default_road + str(filename)  # 加上文件名就是打开文件的路径
    if load_path.endswith(".xlsx"):
        X = pd.read_excel(load_path, sheet_name='Sheet1')
    elif load_path.endswith(".csv"):
        X = pd.read_csv(load_path)
    # X_train = pd.read_excel(load_path, sheet_name='Sheet1')
    # islabel = int(islabel)-1  # 由于"无标签"占位，计数取value从1开始，要减1
    if islabel == "无标签":  # 若选的是无标签
        y_train = X.iloc[:, 0]  # 取X_train最后一列
        y_train = y_train.tolist()
        for i in range(len(y_train)):
            y_train[i] = 0  # 把y_train置为0，即y_train是一列全0的list
            # 对于无监督原本并不需要y_train(pyod也不需要);
            # 但adbench.baseline.PyOD.PYOD中需要，暂且写下这个逻辑
    else:
        # y_train = X_train.iloc[:, islabel]  # 根据列号索引获得y_train
        y_train = X[[islabel]]  # 根据列名索引获得y_train
        # y_train = y_train.values.tolist()
        # y_train = [int(x) for x in y_train]
        X = X.drop(islabel, axis=1)  # 同时删除X_train中的标签列

    X_train = X.values
    y_train = np.array(y_train)
    # 无监督的14个
    if algo == '主成分分析(PCA)':
        clf = PCA()
        clf.fit(X_train)
        score = clf.decision_function(X_train)
        # score = clf.decision_scores_
    elif algo == 'One-class SVM (OCSVM)':
        clf = OCSVM()
        clf.fit(X_train)
        score = clf.decision_function(X_train)
    elif algo == 'Local Outlier Factor (LOF)':
        clf = LOF()
        clf.fit(X_train)
        score = clf.decision_function(X_train)
    elif algo == 'Clustering Based Local Outlier Factor (CBLOF)':                                    
        clf = CBLOF()
        clf.fit(X_train)
        score = clf.decision_function(X_train)
    elif algo == 'Connectivity-Based Outlier Factor (COF)':
        clf = COF()
        clf.fit(X_train)
        score = clf.decision_function(X_train)
    elif algo == 'Histogram-based outlier detection (HBOS)':
        clf = HBOS()
        clf.fit(X_train)
        score = clf.decision_function(X_train)
    elif algo == 'K-Nearest Neighbors (KNN)':
        clf = KNN()
        clf.fit(X_train)
        score = clf.decision_function(X_train)
    elif algo == 'Subspace Outlier Detection (SOD)':
        X_train = check_array(X_train)
        clf = SOD()
        clf.fit(X_train)
        score = clf.decision_function(X_train)
    elif algo == 'Copula Based Outlier Detector (COPOD)':
        clf = COPOD()
        clf.fit(X_train)
        score = clf.decision_function(X_train)
    elif algo == 'Empirical-Cumulative-distribution-based Outlier Detection (ECOD)':
        clf = ECOD()
        clf.fit(X_train)
        score = clf.decision_function(X_train)
    elif algo == 'Deep Support Vector Data Description (DeepSVDD)':
        clf = DeepSVDD()
        clf.fit(X_train)
        score = clf.decision_function(X_train)
    elif algo == 'Deep Autoencoding Gaussian Mixture Model (DAGMM)':
        X_train = check_array(X_train)
        # clf = DAGMM(seed=1)
        # clf.fit(X_train, y_train)
        # score = clf.decision_function(X_train)
        model = DAGMM(seed=42)
        model.fit(X_train=X_train, y_train=np.repeat(0, X_train.shape[0]))
        # score = model.predict_score(X_train, X_test)
        score = model.decision_function(X_train)
    elif algo == 'Lightweight on-line detector of anomalies (LODA)':
        clf = LODA()
        clf.fit(X_train)
        score = clf.decision_function(X_train)
    elif algo == 'Isolation Forest (IForest)':
        clf = IForest()
        clf.fit(X_train)
        score = clf.decision_function(X_train)
    # 半监督的7个
    elif algo == 'Semi-Supervised Anomaly Detection via Adversarial Training (GANomaly)':
        clf = GANomaly(seed=1)
        # X_train = torch.from_numpy(X_train)
        # y_train = torch.from_numpy(y_train)
        clf.fit(X_train, y_train)
        score = clf.decision_function(X_train)
    elif algo == 'Deep Semi-supervised Anomaly Detection (DeepSAD)':
        clf = DeepSAD(seed=1)
        # X_train = np.arrary(X_train)
        clf.fit(X_train, y_train)
        score = clf.decision_function(X_train)
    elif algo == 'REPresentations for a random nEarest Neighbor distance-based method (REPEN)':
        clf = REPEN(seed=1)
        clf.fit(X_train, y_train)
        score = clf.decision_function(X_train)
    elif algo == 'Deviation Networks (DevNet)':
        clf = DevNet(seed=1)
        clf.fit(X_train, y_train)
        score = clf.decision_function(X_train)
    elif algo == 'Pairwise Relation prediction-based ordinal regression Network (PReNet)':
        X_train = check_array(X_train)
        clf = PReNet(seed=1)
        clf.fit(X_train, y_train)
        score = clf.decision_function(X_train)
    elif algo == 'Feature Encoding With Autoencoders for Weakly Supervised Anomaly Detection (FEAWAD)':
        clf = FEAWAD(seed=1)
        clf.fit(X_train, y_train)
        score = clf.decision_function(X_train)
    elif algo == 'Extreme Gradient Boosting Outlier Detection (XGBOD)':
        clf = XGBOD()
        clf.fit(X_train, y_train)
        score = clf.decision_function(X_train)
    # 有监督的9个
    elif algo == 'Naive Bayes (NB)':
        algo = 'NB'
        a = supervised(1, algo)
        b = a.fit(X_train, y_train)
        score = b.predict_score(X_train)
    elif algo == 'Support Vector Machine (SVM)':
        algo = 'SVM'
        a = supervised(1, algo)
        b = a.fit(X_train, y_train)
        score = b.predict_score(X_train)
    elif algo == 'Multi-layer Perceptron (MLP)':
        algo = 'MLP'
        a = supervised(1, algo)
        b = a.fit(X_train, y_train)
        score = b.predict_score(X_train)
    elif algo == 'Random Forest (RF)':
        algo = 'RF'
        a = supervised(1, algo)
        b = a.fit(X_train, y_train)
        score = b.predict_score(X_train)
    elif algo == 'Xtreme Gradient Boosting (XGBoost)':
        algo = 'XGB'
        a = supervised(1, algo)
        b = a.fit(X_train, y_train)
        score = b.predict_score(X_train)
    elif algo == 'Highly Efficient Gradient Boosting Decision Tree (LightGBM)':
        algo = 'LGB'
        a = supervised(1, algo)
        b = a.fit(X_train, y_train)
        score = b.predict_score(X_train)
    elif algo == 'Categorical Boosting (CatBoost)':
        algo = 'CatB'
        a = supervised(1, algo)
        b = a.fit(X_train, y_train)
        score = b.predict_score(X_train)
    elif algo == 'Residual Nets (ResNet)':
        X_train = check_array(X_train)
        clf = FTTransformer(model_name='ResNet', seed=1)
        clf.fit(X_train, y_train)
        score = clf.predict_score(X_train)
    elif algo == 'Feature Tokenizer + Transformer (FTTransformer)':
        X_train = check_array(X_train)
        clf = FTTransformer(model_name='FTTransformer', seed=1)
        clf.fit(X_train, y_train)
        score = clf.predict_score(X_train)
    else:
        return False

    features_num = X_train.shape[1]
    nums = X_train.shape[0]
    return score, features_num, nums


from sklearn.ensemble import IsolationForest

def service1_cal(filename):
    '''
    :param filename: 文件名，需要通过media索引访问读取文件；
    :return: score分数
    '''

    default_road = 'media/service1/'  # 文件存储的相对路径
    load_path = default_road + str(filename)  # 加上文件名就是打开文件的路径
    if load_path.endswith(".xlsx"):
        X_train = pd.read_excel(load_path, sheet_name='Sheet1')
    elif load_path.endswith(".csv"):
        X_train = pd.read_csv(load_path)
    X = X_train.values
    # 不管数据什么类型，直接上KNN
    clf = IsolationForest(n_estimators=80,
                          max_samples=256,
                          contamination=0.02,
                          max_features=6,
                          random_state=1
                          )
    clf.fit(X)
    score = clf.decision_function(X)
    y_pred = clf.predict(X)
    anomaly_num = np.count_nonzero(y_pred == -1)
    features_num = X_train.shape[1]
    nums = X_train.shape[0]

    return score, anomaly_num, features_num, nums


from ADCat_gym.metaclassifier.meta_custom import run as adgym


def run_adgym(filename):
    '''
    :param filename: 文件名，需要通过media索引访问读取文件；
    :return: best_pipeline,fit_time,score_train；
    :best_pipeline: 选择得到的一系列参数（字符串）；
    :fit_time: 训练模型的时长（字符串）；
    :score_train: 经训练得到的异常检测的分数（列表）；
    '''

    default_road = 'media/adgym/'  # 文件存储的相对路径
    load_path = default_road + str(filename)  # 加上文件名就是打开文件的路径
    # if load_path.endswith(".xlsx"):
    #     X_train = pd.read_excel(load_path, sheet_name='Sheet1')
    # elif load_path.endswith(".csv"):
    #     X_train = pd.read_csv(load_path)
    # X = X_train.values
    best_pipeline_list, fit_time, anomaly_score = adgym(load_path)
    return best_pipeline_list, fit_time, anomaly_score

