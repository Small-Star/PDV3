from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import numpy as np
import pandas as pd

# Import function to create training and test set splits
from sklearn.model_selection import train_test_split
# Import function to automatically create polynomial features! 
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
# Import Linear Regression and a regularized regression function
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LassoCV
# Finally, import function to make a machine learning pipeline
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report
from sklearn import metrics
from sklearn.pipeline import Pipeline

import sys, datetime
sys.path.insert(0, './app')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/u_delta/projects/PDV3/app.db'
db = SQLAlchemy(app)

from app.models import Mood, QS_Params, Lifts

##db.create_all()
##print("Current table:")
##
##ms = Mood.query.all()
##print(ms)
##
##print("Adding some test users")
##
###db.session.add(Mood(datetime.date(2001,5,20),1,3,'M',4,6,'N'))
###db.session.add(Mood(datetime.date(2005,6,21),2,4,'N',5,7,'U'))


#Pull data from DB
db_dump = db.session.query(QS_Params).all()

# def get_variable(var_name, shift=1):
# 	culled = [(_.date, _.var_name) for _ in db_dump if _.var_name != None]
# 	return v

# b = get_variable(var_name=_.bpm)

# print(b)

#PREPROCESSING
#Cull NaN
#Shift data
#Filter only for all values present

test = db.session.query(Mood).all()
culled = [(_.date, _.v_be, _.qsp.bpm, _.qsp.sleep_overall_q, _.v_u, _.v_l, _.qsp.kcal_intake, _.qsp.tdee, _.qsp.sleep_duration, _.qsp.meditation_time, _.qsp.net_carb_intake) for _ in test if _.v_be != None and _.qsp.bpm != None and _.qsp.sleep_overall_q != None and _.qsp.kcal_intake != None and _.qsp.tdee != None and _.qsp.sleep_duration != None and _.qsp.meditation_time != None and _.qsp.net_carb_intake != None]
date, v_be, bpm, sq, v_u, v_l, kcal, tdee, sd, mt, nc = [list(_) for _ in zip(*culled)]

arr = np.column_stack((bpm,sq,v_u, v_l, kcal, tdee, sd, mt, nc))

df = pd.DataFrame(data=arr)

print("Dataframe shape: ", df.shape)

# Alpha (regularization strength) of LASSO regression
lasso_eps = 0.0001
lasso_nalpha=5
lasso_iter=50000
# Min and max degree of polynomials features to consider
degree_min = 0
degree_max = 3
# Test/train split
X_train, X_test, y_train, y_test = train_test_split(df, v_be,test_size=.33)
print("Number of traning elements: ", len(X_train))

scores,r2_score = [],[]
rmse_error, mae_error = [],[]
poly = []

pr = True
if pr == True:
    print("Polynomial Regression (up to degree %d) w/ LASSO" %degree_max)
    # Make a pipeline model with polynomial transformation and LASSO regression with cross-validation, run it for increasing degree of polynomial (complexity of the model)
    for degree in range(degree_min,degree_max+1):
        #poly.append(PolynomialFeatures(degree, interaction_only=False))
        model = Pipeline(steps=[('pf',PolynomialFeatures(degree, interaction_only=False)), ('sc',StandardScaler()), ('lasso',LassoCV(eps=lasso_eps,n_alphas=lasso_nalpha,max_iter=lasso_iter, normalize=True,cv=5))])
        model.fit(X_train,y_train)

        test_pred = np.array(model.predict(X_test))
        RMSE=np.sqrt(np.sum(np.square(test_pred-y_test)))
        MAE=np.sqrt(metrics.mean_squared_error(y_test, test_pred))
        test_score = model.score(X_test,y_test)
        #r2 = metrics.r2_score(y_test, test_pred)
        rmse_error.append(RMSE)
        mae_error.append(MAE)
        scores.append(test_score)
        #r2_score.append(r2)
        #model.named_steps.pf.fit(X_train,y_train)
        #print(model.named_steps.pf.coef_)

    for degree in range(degree_min,degree_max+1):
        print("Poly (order %d): " %degree)
        print("     RMSE: ", rmse_error[degree])
        print("     MAE: ", mae_error[degree])
        print("     R^2 Score: ", scores[degree])
        #print("Coefficients: ", poly[degree].get_feature_names(df.columns))
        #print("     R^2: ", r2_score[degree])

# print("Linear Regression")
# lm2 = LinearRegression()

# # Fit Model
# lm2.fit(X_train, y_train)

# # Predict
# y_pred = lm2.predict(X_test)

# # RMSE
# print("     MAE: ", np.sqrt(metrics.mean_squared_error(y_test, y_pred)))
db.session.commit()
