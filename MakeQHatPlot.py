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

def PlotQHat(T = 0.15, E = 100, Q = 100, Scan = 'T', P = [[1, 1, 1, 1, 1, 1]], Type = "", Suffix = ""):

    if Suffix != "":
        Suffix = "_" + Suffix

    X = []
    Y = []
    XLabel = ""
    ExtraText = ""

    if Scan == 'T':
        X = np.arange(0.17, 0.45, 0.01)
        XLabel = "T"
        ExtraText = f"E = {E} GeV"
    elif Scan == 'E':
        X = np.arange(5, 200, 1)
        XLabel = "E"
        ExtraText = f"T = {T} GeV"
    elif Scan == 'Q':
        X = np.arange(5, 200, 1)
        XLabel = "Q"
        ExtraText = f"T = {T} GeV, E = {E} GeV"
    elif Scan == 'EQ':
        X = np.arange(5, 200, 1)
        XLabel = "E"
        ExtraText = f"T = {T} GeV, Q = E"
    else:
        print('Error!  Illegal scan variable')

    figure, axes = plt.subplots(figsize = (5, 5))

    NSample = P.shape[0]
    for i in range(NSample):
        if Scan == 'T':
            Y = [qhat(T = x, E = E, Q = Q, parameters = P[i]) for x in X]
            XLabel = "T (GeV)"
        elif Scan == 'E':
            Y = [qhat(T = T, E = x, Q = Q, parameters = P[i]) for x in X]
            XLabel = "E (GeV)"
        elif Scan == 'Q':
            Y = [qhat(T = T, E = E, Q = x, parameters = P[i]) for x in X]
            XLabel = "Q (GeV)"
        elif Scan == 'EQ':
            Y = [qhat(T = T, E = x, Q = x, parameters = P[i]) for x in X]
            XLabel = "E (GeV)"
        else:
            print('Error!  Illegal scan variable')

        axes.plot(X, Y, 'b', alpha = 50 / NSample)

    axes.text(0.95, 0.95, ExtraText, transform = axes.transAxes, ha = 'right', va = 'top')
    axes.text(0.95, 0.90, Type, transform = axes.transAxes, ha = 'right', va = 'top')

    axes.set_xlabel(XLabel)
    axes.set_ylabel(r'$\hat{q}/T^3$')

    plt.tight_layout()
    tag = AllData['tag']
    figure.savefig(f'result/{tag}/plots/QHat{Suffix}.pdf', dpi = 192)


Posterior = MCMCSamples[ np.random.choice(range(len(MCMCSamples)), 2500), :]

PlotQHat(T = 0.2, E = 100, Q = 100, Scan = 'T', P = Posterior, Type = "Posterior", Suffix = "Posterior_T_E100")
PlotQHat(T = 0.3, E = 100, Q = 100, Scan = 'E', P = Posterior, Type = "Posterior", Suffix = "Posterior_E_T0.3")

Design = AllData["design"]

PlotQHat(T = 0.2, E = 100, Q = 100, Scan = 'T', P = Design, Type = "Design", Suffix = "Design_T_E100")
PlotQHat(T = 0.3, E = 100, Q = 100, Scan = 'E', P = Design, Type = "Design", Suffix = "Design_E_T0.3")



