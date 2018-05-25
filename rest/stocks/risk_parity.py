import numpy as np
from scipy.optimize import minimize

def Quadratic(weight_vec, *args):
    weight_vec = np.matrix(weight_vec)
    cov = args[0]
    #calculate risk
    sigma = weight_vec * cov * weight_vec.T
    sigma = np.sqrt(sigma[0,0])
    #create equal risk contribution [0.25 0.25 0.25 0.25]
    risk = [1/weight_vec.shape[1] for i in range(weight_vec.shape[1])]
    risk = np.matrix(risk).T
    #asset risk contribution w*cov*w.T/sigma
    asset_risk_contribution = np.multiply(weight_vec.T, cov*weight_vec.T)/sigma
    #minimize squared sum of error
    SSE = sum(np.square(asset_risk_contribution-sigma*risk))*1000
    return SSE[0,0]

def construct_ERC(returns):
    #construct covariance matrix
    returns = np.vstack((returns))
    cov = np.cov(returns)
    cov = np.matrix(cov)
    #construc equal weight vector
    weight_vec = (np.ones(cov.shape[0]))
    weight_vec = weight_vec/weight_vec.shape[0]
    #construct bounds and constraints for optimize minimize
    bounds = [(0,1) for i in range(cov.shape[0])]
    cons = ({'type': 'eq', 'fun': lambda x:  np.sum(x)-1})

    weights = minimize(Quadratic,
                       weight_vec,
                       cov,
                       bounds = bounds,
                       constraints = cons,
                       method='SLSQP')

    return weights.x
