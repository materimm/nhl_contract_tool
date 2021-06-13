from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.model_selection import train_test_split, RepeatedStratifiedKFold, GridSearchCV
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from pathlib import Path
import os
import pandas as pd
import pickle

import contract_feature_eng as cfe


def get_data():
    base_dir = str(Path(os.getcwd()).parents[0])
    df = pd.read_csv(base_dir + '\\NHLData\\features_bins.csv')
    labels = df.cap_hit_percentage_at_signing
    features = df.drop(['cap_hit_percentage_at_signing'], axis=1)
    return features, labels


#Best: 0.606644 using {'learning_rate': 0.01, 'max_depth': 3, 'n_estimators': 500, 'subsample': 0.5}
def gbr_grid_search():
    x, y = get_data()
    model = GradientBoostingRegressor()
    grid = dict()
    grid['n_estimators'] = [10, 50, 100, 500]
    grid['learning_rate'] = [0.0001, 0.001, 0.01, 0.1, 1.0]
    grid['subsample'] = [0.3, 0.5, 0.7, 1.0]
    grid['max_depth'] = [2, 3, 4, 5]
    #cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
    grid_search = GridSearchCV(estimator=model, param_grid=grid, cv=10)
    grid_result = grid_search.fit(x, y)
    print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
    # means = grid_result.cv_results_['mean_test_score']
    # stds = grid_result.cv_results_['std_test_score']
    # params = grid_result.cv_results_['params']
    # for mean, stdev, param in zip(means, stds, params):
    #     print("%f (%f) with: %r" % (mean, stdev, param))


def gbr_model():
    features, labels = get_data()
    xtrain, xtest, ytrain, ytest=train_test_split(features, labels, random_state=12, test_size=0.15)
    # with new parameters
    gbr = GradientBoostingRegressor(n_estimators=500,
        max_depth=3,
        learning_rate=0.01,
        subsample=0.5)

    gbr.fit(xtrain, ytrain)
    save_model(gbr, 'contract_gbr.sav')

    counter = 0
    for x, y in zip(features.columns.values.tolist(), gbr.feature_importances_):
        print(str(counter) + '- ' + x + ': ' + str(y))
        counter = counter + 1
    # plot
    plt.bar(range(len(gbr.feature_importances_)), gbr.feature_importances_)
    plt.show()

    ypred = gbr.predict(xtest)
    mse = mean_squared_error(ytest, ypred)
    print("MSE: %.5f" % mse)

    ## for sorted graph
    Z = [x for _,x in sorted(zip(ytest,ypred))]
    V = ytest.tolist()
    V.sort()
    x_ax = range(len(V))
    plt.scatter(x_ax, V, s=5, color="blue", label="original")
    plt.plot(x_ax, Z, lw=0.8, color="red", label="predicted")

    # x_ax = range(len(ytest))
    # plt.scatter(x_ax, ytest, s=5, color="blue", label="original")
    # plt.plot(x_ax, ypred, lw=0.8, color="red", label="predicted")

    plt.legend()
    plt.show()


#Best: 0.626503 using {'min_samples_leaf': 50, 'n_estimators': 100}
def rf_grid_search():
    x, y = get_data()
    model = RandomForestRegressor()
    grid = {
        'min_samples_leaf': [50, 100, 250, 500],
        'n_estimators': [10, 50, 100, 500]
    }
    grid_search = GridSearchCV(estimator=model, param_grid=grid, cv=10)
    grid_result = grid_search.fit(x, y)
    print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))


def rf_model():
    x, y = get_data()
    xtrain, xtest, ytrain, ytest=train_test_split(x, y, random_state=12, test_size=0.15)
    # with new parameters
    rfr = RandomForestRegressor(n_estimators=100, min_samples_leaf=50)

    rfr.fit(xtrain, ytrain)

    ypred = rfr.predict(xtest)
    mse = mean_squared_error(ytest, ypred)
    print("MSE: %.5f" % mse)

    ## for sorted graph
    Z = [x for _,x in sorted(zip(ytest,ypred))]
    V = ytest.tolist()
    V.sort()
    x_ax = range(len(V))
    plt.scatter(x_ax, V, s=5, color="blue", label="original")
    plt.plot(x_ax, Z, lw=0.8, color="red", label="predicted")

    plt.legend()
    plt.show()


def save_model(model, filename):
    # save the model to disk
    pickle.dump(model, open(filename, 'wb'))


def load_model(filename):
    # load the model from disk
    return pickle.load(open(filename, 'rb'))


def get_predicted_contract(names):
    salary_cap = 81500000
    gbr = load_model('contract_gbr.sav')
    contracts = []
    for n in names:
        data = cfe.get_player_features(n)
        pred = gbr.predict(data)
        contract = round(salary_cap * pred[0], 2)
        contracts.append(contract)
        contract = "$" + f"{contract:,}"
        print(n + ': ' + contract)
    return contracts

#####################
###  Method Calls ###
#####################
#gbr_model()
get_predicted_contract(['Michael Mcleod', 'Janne Kuokkanen', 'Yegor Sharangovich'])
