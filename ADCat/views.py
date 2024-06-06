from django.shortcuts import render
from django.http import HttpResponse
# from .forms import UploadFileForm


def home(request):
    return render(request, 'index.html')


def adbench(request):
    return render(request, 'adbench.html')


def contact(request):
    return render(request, 'contact.html')


def result(request):
    return render(request, 'result.html')


def register(request):
    return render(request, 'register.html')


def login(request):
    return render(request, 'login.html')


def PCA(request):
    return render(request, 'unsupervised_PCA.html')
def OCSVM(request):
    return render(request, 'unsupervised_OCSVM.html')
def LOF(request):
    return render(request, 'unsupervised_LOF.html')
def CBLOF(request):
    return render(request, 'unsupervised_CBLOF.html')
def COF(request):
    return render(request, 'unsupervised_COF.html')
def HBOS(request):
    return render(request, 'unsupervised_HBOS.html')
def KNN(request):
    return render(request, 'unsupervised_KNN.html')
def SOD(request):
    return render(request, 'unsupervised_SOD.html')
def COPOD(request):
    return render(request, 'unsupervised_COPOD.html')
def ECOD(request):
    return render(request, 'unsupervised_ECOD.html')
def DeepSVDD(request):
    return render(request, 'unsupervised_DeepSVDD.html')
def DAGMM(request):
    return render(request, 'unsupervised_DAGMM.html')
def LODA(request):
    return render(request, 'unsupervised_LODA.html')
def IForest(request):
    return render(request, 'unsupervised_IForest.html')


def GANomaly(request):
    return render(request, 'semi-supervised_GANomaly.html')
def DeepSAD(request):
    return render(request, 'semi-supervised_DeepSAD.html')
def REPEN(request):
    return render(request, 'semi-supervised_REPEN.html')
def DevNet(request):
    return render(request, 'semi-supervised_DevNet.html')
def PReNet(request):
    return render(request, 'semi-supervised_PReNet.html')
def FEAWAD(request):
    return render(request, 'semi-supervised_FEAWAD.html')
def XGBOD(request):
    return render(request, 'semi-supervised_XGBOD.html')


def NB(request):
    return render(request, 'supervised_NB.html')
def SVM(request):
    return render(request, 'supervised_SVM.html')
def MLP(request):
    return render(request, 'supervised_MLP.html')
def RF(request):
    return render(request, 'supervised_RF.html')
def XGBoost(request):
    return render(request, 'supervised_XGBoost.html')
def LightGBM(request):
    return render(request, 'supervised_LightGBM.html')
def CatBoost(request):
    return render(request, 'supervised_CatBoost.html')
def ResNet(request):
    return render(request, 'supervised_ResNet.html')
def FTTransformer(request):
    return render(request, 'supervised_FTTransformer.html')


def service1(request):
    return render(request, 'service1.html')


def adgym(request):
    return render(request, 'adgym.html')
