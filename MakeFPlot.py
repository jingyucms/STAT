import matplotlib.pyplot as plt
import numpy as np

import pickle
AllData = {}
with open('input/default.p', 'rb') as handle:
    AllData = pickle.load(handle)

import src
src.Initialize()
from src import mcmc
chain = mcmc.Chain()
MCMCSamples = chain.load()



# These taken from Raymond code
# https://github.com/raymondEhlers/STAT/blob/1b0df83a9fd479f8110fd326ae26c0ce002a1109/run_analysis_base.py

def raw_f(Q: float, C1: float, C2: float, C3: float, EM: float) -> float:
    lambda_qcd = 0.2
    LogQQLL = np.log((Q * Q) / (lambda_qcd * lambda_qcd))
    XB = Q * Q / (2 * EM)
    if C3 > 0:
        ans = (np.exp(C3 * (1 - XB)) - 1) / (1 + C1 * LogQQLL + C2 * LogQQLL * LogQQLL)
    elif C3 == 0:
        ans = (1 - XB) / (1 + C1 * LogQQLL + C2 * LogQQLL * LogQQLL)
    else:
        ans = 0
    return ans

def f(Q: float, C1: float, C2: float, C3: float, Q0: float, EM: float) -> float:
    if Q < Q0:
        return 1
    F1 = raw_f(Q = Q, C1 = C1, C2 = C2, C3 = C3, EM = EM)
    F0 = raw_f(Q = Q0, C1 = C1, C2 = C2, C3 = C3, EM = EM)

    if F0 == 0:
        ans = 0
    else:
        ans = F1 / F0

    return ans

# def virtuality_qhat_function:
#     xB = mu_square / (2.0 * ener_loc)
#     xB0 = Q0*Q0 / (2.0 * ener_loc)
#     if xB <= xB0:
#        return 1.0
#     if C3 > 0.0 and xB < 0.99:
#       ans = (np.exp(C3 * (1.0-xB) ) - 1.0 )/(1.0 + C1*np.log(mu_square / 0.04) + C2*np.log(mu_square/0.04)*np.log(mu_square/0.04) )
#       ans = ans*(1.0 + C1*np.log(Q0 * Q0 / 0.04) + C2*np.log(Q0 * Q0 / 0.04)*np.log(Q0*Q0/0.04) )/( np.exp(C3 * (1.0-xB0)) - 1.0 )
#     elif C3 == 0.0 and xB < 0.99:
#       ans = (1.0-xB)/(1.0 + C1 * np.log(mu_square / 0.04) + C2 * np.log(mu_square / 0.04) * np.log(mu_square / 0.04) )
#       ans = ans * (1.0 + C1 * np.log(Q0 * Q0 / 0.04) + C2 * np.log(Q0 * Q0 / 0.04) * np.log(Q0 * Q0 / 0.04) )/(1 - xB0)
#     else:
#       return 0.0

def PlotF(EM = 1, P = [[1, 1, 1, 1, 1, 1]], Type = "", Suffix = "", DoJet = False):

    if Suffix != "":
        Suffix = "_" + Suffix

    X = np.exp(np.arange(np.log(1), np.log(2 * EM), 0.01))
    Y = []
    XLabel = r'$Q^2$'
    ExtraText = f'$E\cdot M = {EM}$ GeV$^2$'
    # ExtraText = f"E = {E} GeV"

    figure, axes = plt.subplots(figsize = (5, 5))

    AllY = []

    NSample = P.shape[0]
    for i in range(NSample):
        Y = [f(Q = np.sqrt(x), C1 = np.exp(P[i][2]), C2 = np.exp(P[i][3]), C3 = np.exp(P[i][5]), Q0 = P[i][1], EM = EM) for x in X]
        XLabel = r'$Q^2$ (GeV$^2$)'

        AllY.append(Y)

        axes.plot(X, Y, 'b', alpha = 50 / NSample)

    axes.text(0.95, 0.95, ExtraText, transform = axes.transAxes, ha = 'right', va = 'top')
    axes.text(0.95, 0.90, Type, transform = axes.transAxes, ha = 'right', va = 'top')

    axes.set_xlabel(XLabel)
    axes.set_ylabel(r'$f(Q^2)$')

    axes.set_xscale('log')
    axes.set_ylim([0, 1.1])

    plt.tight_layout()
    tag = AllData['tag']
    figure.savefig(f'result/{tag}/plots/FQ{Suffix}.pdf', dpi = 192)
    figure.savefig(f'result/{tag}/plots/FQ{Suffix}.png', dpi = 192)

    axes.set_yscale('log')
    axes.set_ylim([1e-5, 100])

    figure.savefig(f'result/{tag}/plots/FQLog{Suffix}.pdf', dpi = 192)
    figure.savefig(f'result/{tag}/plots/FQLog{Suffix}.png', dpi = 192)

    axes.set_xscale('linear')
    axes.set_xlim([0, 50])
    axes.set_ylim([1e-3, 10])

    figure.savefig(f'result/{tag}/plots/FQX{Suffix}.pdf', dpi = 192)
    figure.savefig(f'result/{tag}/plots/FQX{Suffix}.png', dpi = 192)

    AllY = np.array(AllY)

    Y05 = []
    Y50 = []
    Y95 = []

    for i in range(0, AllY.shape[1]):
        Y = np.sort(AllY[:,i])
        Y05.append(Y[int(Y.shape[0]*0.05)])
        Y50.append(Y[int(Y.shape[0]*0.50)])
        Y95.append(Y[int(Y.shape[0]*0.95)])

    figure, axes = plt.subplots(figsize = (5, 5))

    axes.plot(X, Y05, 'b-')
    axes.plot(X, Y50, 'b.')
    axes.plot(X, Y95, 'b-')

    axes.text(0.95, 0.95, ExtraText, transform = axes.transAxes, ha = 'right', va = 'top')
    axes.text(0.95, 0.90, Type, transform = axes.transAxes, ha = 'right', va = 'top')
    axes.text(0.95, 0.85, 'Median and 90% range', transform = axes.transAxes, ha = 'right', va = 'top')

    axes.set_xlabel(XLabel)
    axes.set_ylabel(r'$f(Q^2)$')

    plt.tight_layout()
    tag = AllData['tag']
    figure.savefig(f'result/{tag}/plots/FQRange{Suffix}.pdf', dpi = 192)
    figure.savefig(f'result/{tag}/plots/FQRange{Suffix}.png', dpi = 192)



Posterior = MCMCSamples[ np.random.choice(range(len(MCMCSamples)), 5000), :]

PlotF(EM = 100, P = Posterior, Type = "Posterior", Suffix = "Posterior_E100")
PlotF(EM = 20,  P = Posterior, Type = "Posterior", Suffix = "Posterior_E20")
PlotF(EM = 10,  P = Posterior, Type = "Posterior", Suffix = "Posterior_E10")

Design = AllData["design"]

PlotF(EM = 100, P = Design, Type = "Design", Suffix = "Design_E100")



