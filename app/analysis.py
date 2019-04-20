
#MOOD (v_be): List of variables to check
#same day and previous day of all recorded variables
#v_u; v_l :not sure how useful this would be
#v_be, v_u, v_l previous days
#v_be, v_u, v_l previous average
#v_be, v_u, v_l intra-day variability
#same for a values
#kcal intake of previous days; averages

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import numpy as np
import pandas as pd

# Import function to create training and test set splits
from sklearn.model_selection import train_test_split
# Import function to automatically create polynomial features! 
from sklearn.preprocessing import PolynomialFeatures
# Import Linear Regression and a regularized regression function
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LassoCV
# Finally, import function to make a machine learning pipeline
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report
from sklearn import metrics

import sys, datetime
sys.path.insert(0, './app')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/u_delta/projects/PDV3/app.db'
db = SQLAlchemy(app)

from app.models import Mood, QS_Params, Lifts

db.create_all()

test = db.session.query(Mood).all()
#[print(_.squat_str, _.squat_max, _.squat_max_vol_per_set, _.squat_total_vol) for _ in test] #if _.date > datetime.date(2017,4,10)]
culled = [(_.date, _.v_be, _.qsp.bpm, _.qsp.sleep_overall_q, _.v_u, _.v_l, _.qsp.kcal_intake) for _ in test if _.v_be != None and _.qsp.bpm != None and _.qsp.sleep_overall_q != None and _.qsp.kcal_intake != None]
date, v_be, bpm, sq, v_u, v_l, kcal = [list(_) for _ in zip(*culled)]

arr = np.column_stack((bpm,sq,v_u, v_l, kcal))

df = pd.DataFrame(data=arr)

#print(df)

# Alpha (regularization strength) of LASSO regression
lasso_eps = 0.0001
lasso_nalpha=5
lasso_iter=5000
# Min and max degree of polynomials features to consider
degree_min = 0
degree_max = 6
# Test/train split
X_train, X_test, y_train, y_test = train_test_split(df, v_be,test_size=.33)
print(len(X_train))
scores,r2_score = [],[]
rmse_error, mae_error = [],[]

print("Polynomial Regression w/ LASSO")
# Make a pipeline model with polynomial transformation and LASSO regression with cross-validation, run it for increasing degree of polynomial (complexity of the model)
for degree in range(degree_min,degree_max+1):
    model = make_pipeline(PolynomialFeatures(degree, interaction_only=False), LassoCV(eps=lasso_eps,n_alphas=lasso_nalpha,max_iter=lasso_iter, normalize=True,cv=5))
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

for degree in range(degree_min,degree_max+1):
	print("Poly (order %d): " %degree)
	print("     RMSE: ", rmse_error[degree])
	print("     MAE: ", mae_error[degree])
	print("     R^2 Score: ", scores[degree])
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
