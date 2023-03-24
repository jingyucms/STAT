import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from pathlib import Path

import pickle
AllData = {}
with open('input/default.p', 'rb') as handle:
    AllData = pickle.load(handle)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--Plot", help = "What tags to plot", nargs = '+', type = str, default = [])
parser.add_argument("--Label", help = "What labels to plot", nargs = '+', type = str, default = [])
parser.add_argument("--Min", help = "x min", default = 3, type = float)
parser.add_argument("--Max", help = "x max", default = 9, type = float)
parser.add_argument("--Bin", help = "Number of bins", default = 40, type = float)
parser.add_argument("--Suffix", help = "suffix", default = '', type = str)
parser.add_argument("--DoKSTest", help = "do KS test or not", default = False, type = bool)
parser.add_argument("--T", help = "temperature", default = 0.2, type = float)
parser.add_argument("--E", help = "energy", default = 200, type = float)
args = parser.parse_args()

import src
src.Initialize()
from src import mcmc

if args.DoKSTest == True:
    if len(args.Plot) < 2:
        args.DoKSTest = False

print(f'Do KS test? {args.DoKSTest}')

# These taken from Raymond code
# https://github.com/raymondEhlers/STAT/blob/1b0df83a9fd479f8110fd326ae26c0ce002a1109/run_analysis_base.py

def running_alpha_s(mu_square: float, alphas: float) -> float:
    active_flavor = 3
    square_lambda_QCD_HTL = np.exp( -12.0 * np.pi/( (33 - 2 * active_flavor) * alphas) );
    ans = 12.0 * np.pi/( (33.0 - 2.0 * active_flavor) * np.log(mu_square/square_lambda_QCD_HTL) );
    if mu_square < 1.0:
        ans = alphas
    # print(f"Fixed-alphaS={alphas}, Lambda_QCD_HTL={np.sqrt(square_lambda_QCD_HTL)}, mu2={mu_square}, Running alpha_s={ans}")
    return ans;

def qhat(T=0, E=0, Q=0, parameters=None) -> float:
    model = "exponential"
    if model == "exponential":
        # Parameters
        # alpha_s_fix, Q0, C1, C2, tau_0, C3 = parameters
        alpha_s_fix = parameters[0]
        active_flavor = 3

        # Extracted from JetScapeConstants
        C_a = 3.0

        # From GeneralQhatFunction
        debye_mass_square = alpha_s_fix * 4 * np.pi * np.power(T, 2.0) * (6.0 + active_flavor) / 6.0
        scale_net = 2 * E * T
        if scale_net < 1.0:
            scale_net = 1.0

        # alpha_s should be taken as 2*E*T, per Abhijit
        # See: https://jetscapeworkspace.slack.com/archives/C025X5NE9SN/p1648404101376299
        # answer = (C_a * 50.4864 / np.pi) * running_alpha_s(mu_square=scale_net, alphas=scale_net) * alpha_s_fix * np.power(T, 3) * np.abs(np.log(scale_net / debye_mass_square))
        answer = (C_a * 50.4864 / np.pi) * running_alpha_s(mu_square=scale_net, alphas=scale_net) * alpha_s_fix * np.abs(np.log(scale_net / debye_mass_square))   # nb in this one I removed T^3

        # This is not to be evaluated when evaluating qhat(T, E), per Abhijit. See: https://jetscapeworkspace.slack.com/archives/C025X5NE9SN/p1648404101376299
        # qhat = qhat * _virtuality_qhat_function(
        #  qhat_parametrization_type=ParametrizationType.exponential, ener_loc=E,
        #  # mu_square is the virtuality.
        #  # see: https://github.com/JETSCAPE/JETSCAPE-COMP/blob/e83b8ac71f8d71b9ad8ed71935f85d8951a16cb9/src/jet/Matter.cc#L805
        #  mu_square=Q,
        #  Q0=Q0, C1=C1, C2=C2, C3=C3,
        #  # C4 is unused for this parametrization, so just set to 0
        #  C4=0,
        #)

        return answer * 0.19732698   # 1/GeV to fm

def GetQHatSlice(T = 0.15, E = 100, Q = 100, P = [[1, 1, 1, 1, 1, 1]]):

    AllY = []

    NSample = np.array(P).shape[0]
    for i in range(NSample):
        Value = qhat(T = T, E = E, Q = Q, parameters = P[i])
        AllY.append(Value)

    return AllY



chain = mcmc.Chain()
MCMCSamples = chain.load()
Posterior = MCMCSamples[ np.random.choice(range(len(MCMCSamples)), 5000), :]
Y = GetQHatSlice(T = args.T, E = args.E, Q = args.E, P = Posterior)

figure, axes = plt.subplots(figsize = (5, 5))

axes.hist(Y, bins = 50, range = (0, 10))

bottom, top = axes.get_ylim()
axes.set_ylim(bottom, (top - bottom) * 1.5 + bottom)

axes.text(0.95, 0.95, f"T = {args.T*1000:.0f} MeV, E = {args.E:.0f} GeV", transform = axes.transAxes, ha = 'right', va = 'top', fontsize = 15)
axes.text(0.95, 0.90, "Posterior", transform = axes.transAxes, ha = 'right', va = 'top', fontsize = 15)
axes.text(0.95, 0.85, '', transform = axes.transAxes, ha = 'right', va = 'top', fontsize = 15)
axes.tick_params(axis = 'x', labelsize = 15)
axes.tick_params(axis = 'y', labelsize = 15)

plt.tight_layout()
tag = AllData['tag']
figure.savefig(f'result/{tag}/plots/QHatSlice.pdf', dpi = 192)


if len(args.Plot) > 0:
    figure, axes = plt.subplots(figsize = (5, 5))

    if args.DoKSTest == True:
        Y1 = np.array([])
        Y2 = np.array([])

    for i, item in enumerate(args.Plot):
        chain = mcmc.Chain(path = Path(f'result/{item}/mcmc_chain.hdf'))
        MCMCSamples = chain.load()
        # Posterior = MCMCSamples[ np.random.choice(range(len(MCMCSamples)), 5000), :]
        Y = GetQHatSlice(T = args.T, E = args.E, Q = args.E, P = MCMCSamples)

        if args.DoKSTest == True and i == 0:
            Y1 = np.array(Y)
        if args.DoKSTest == True and i == 1:
            Y2 = np.array(Y)

        # if len(args.Plot) <= 1:
        #     axes.hist(Y, bins = args.Bin, density = True, alpha = 0.5, range = (args.Min, args.Max), label = args.Label[i] if i < len(args.Label) else '')
        # else:
        #     axes.hist(Y, bins = args.Bin, density = True, histtype = 'step', fill = None, linewidth = 2, range = (args.Min, args.Max), label = args.Label[i] if i < len(args.Label) else '')

        axes.hist(Y, bins = args.Bin, density = True, histtype = 'step', fill = None, linewidth = 2, range = (args.Min, args.Max), label = args.Label[i] if i < len(args.Label) else '')



    bottom, top = axes.get_ylim()
    axes.set_ylim(bottom, (top - bottom) * 1.5 + bottom)
    axes.tick_params(axis = 'x', labelsize = 15)
    axes.tick_params(axis = 'y', labelsize = 15)

    axes.set_xlabel(r'$\hat{q}/T^3$', fontsize = 15)
    axes.set_ylabel('Area-normalized', fontsize = 15)

    axes.text(0.95, 0.95, f"T = {args.T*1000:.0f} MeV", transform = axes.transAxes, ha = 'right', va = 'top', fontsize = 15)
    axes.text(0.95, 0.88, f"E = {args.E:.0f} GeV", transform = axes.transAxes, ha = 'right', va = 'top', fontsize = 15)
    axes.text(0.95, 0.81, "Posterior", transform = axes.transAxes, ha = 'right', va = 'top', fontsize = 15)

    if args.DoKSTest == True:
        pvalue = stats.kstest(Y1, Y2).pvalue
        axes.text(0.95, 0.85, f'KS p-value = {pvalue:.3f}', transform = axes.transAxes, ha = 'right', va = 'top')

    axes.legend(loc = 'upper left', fontsize = 15)

    if args.Suffix != '':
        args.Suffix = "_" + args.Suffix

    plt.tight_layout()
    figure.savefig(f'result/QHatSliceComparison{args.Suffix}.pdf', dpi = 192)

