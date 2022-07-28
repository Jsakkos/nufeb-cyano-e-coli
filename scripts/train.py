from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import pandas as pd
#from sklearn.svm import SVC
#from sklearn.datasets import load_digits
#from sklearn.feature_selection import RFE
import tensorflow as tf
import tensorflow_addons as tfa
#import matplotlib.pyplot as plt
import autokeras as ak
from tensorflow.keras import backend as K
#import keras_tuner as kt
from tensorflow.keras.callbacks import TensorBoard
from tensorflow.keras.utils import CustomObjectScope
from tensorflow.keras.models import load_model
def coeff_determination(y_true, y_pred):
    SS_res =  K.sum(K.square( y_true-y_pred ))
    SS_tot = K.sum(K.square( y_true - K.mean(y_true) ) )
    return ( 1 - SS_res/(SS_tot + K.epsilon()) )
# Define Tensorboard as a Keras callback
tb_callback = TensorBoard(
  log_dir='../logs',
  histogram_freq=1,
)


#data = pd.read_pickle('~/nufeb-cyano-e-coli/simulation-data/saved-metrics4.pkl')
df = pd.read_csv('~/nufeb-cyano-e-coli/simulation-data/dataset.csv')
data = df.iloc[:,1:]
predictors = list(data.columns.drop(['total biomass','Colony Area','mother_cell'])) 


dataset = data.dropna()
features = dataset[predictors]
labels = dataset.pop('total biomass')
train_features, test_features, train_labels, test_labels = train_test_split(features, labels, train_size = 0.9, random_state = 42)
#train, test = train_test_split(features,train_size = 0.9, random_state = 42)
#names=pd.DataFrame(features.columns)
#from sklearn.linear_model import LogisticRegression,BayesianRidge,LinearRegression
#use linear regression as the model
#lin_reg = LinearRegression()

#lin_reg = LinearRegression()

#This is to select 5 variables: can be changed and checked in model for accuracy
#rfe_mod = RFE(lin_reg) #RFECV(lin_reg, step=1, cv=5) 
#myvalues=rfe_mod.fit(features,labels) #to fit
#myvalues.support_#The mask of selected features.
#myvalues.ranking_ #The feature ranking, such that ranking_[i] corresponds to the ranking position of the i-th feature. Selected (i.e., estimated best) features are assigned rank 1.

#rankings=pd.DataFrame(myvalues.ranking_) #Make it into data frame
#Concat and name columns
#ranked=pd.concat([names,rankings], axis=1)
#ranked.columns = ["Feature", "Rank"]
#ranked

#Select most important (Only 1's)
#most_important = ranked.loc[ranked['Rank'] ==1] 
#print(most_important)

#most_important['Rank'].count()
#features = features[most_important.Feature]
#train_features, test_features, train_labels, test_labels = train_test_split(features, labels, train_size = 0.8, random_state = 42)

reg = ak.StructuredDataRegressor(max_trials=10,metrics=['mse','mae',coeff_determination], distribution_strategy=tf.distribute.MirroredStrategy(),overwrite=True)#
reg.fit(train_features, train_labels)
with CustomObjectScope({'coeff_determination': coeff_determination}):
  model = reg.export_model()
model.summary()
try:
    model.save("model_autokeras")
except Exception:
    model.save("model_autokeras.h5")
loaded_model = load_model("model_autokeras", custom_objects=ak.CUSTOM_OBJECTS)
test_predictions  = loaded_model.predict(test_features).flatten()
print('r2: ' + str(r2_score(test_labels, test_predictions)))
