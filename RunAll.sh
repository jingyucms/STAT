
python3 SetupAnalysis.py --Config yaml/Exponential20230320RBF_N4.yaml
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20230320RBF_N4.yaml --Observable Hadron
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20230320RBF_N4.yaml --Observable Jet
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20230320RBF_N4_PTUpTo30.yaml --Observable Hadron
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20230320RBF_N4_PTCut30.yaml --Observable Hadron
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20230320RBF_N4_OnlySmallJet.yaml
make RunSequence

exit

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_PTCut30_OnlyCMSHadron.yaml --Observable Hadron
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_PTCut30_OnlyALICEHadron.yaml --Observable Hadron
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_PTCut30_OnlyATLASHadron.yaml --Observable Hadron
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_PTCut30_OnlyRHICHadron.yaml --Observable Hadron
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_ExcludeALICEHadron.yaml
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_ExcludeALICEHadron.yaml --Observable Hadron
make RunSequence

for i in 10 12 14 16 18 20 22 24 26 28 30 40 50;
do
   python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_PTCut${i}.yaml --Observable Hadron
   make RunSequence
done

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_PTCut250.yaml --Observable Jet
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_PTUpTo250.yaml --Observable Jet
make RunSequence


python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_PTUpTo30.yaml --Observable Hadron
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_OnlyALICEHadron.yaml --Observable Hadron --EnergyMin 3000
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_OnlyALICEHadron.yaml --Observable Hadron --EnergyMax 3000
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_PTCut30.yaml
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_PTCut30.yaml --Observable Hadron
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_PTCut100.yaml --Observable Jet
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_PTUpTo100.yaml --Observable Jet
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_OnlyALICEJet.yaml --Observable Jet --EnergyMin 3000
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_OnlyALICEJet.yaml --Observable Jet --EnergyMax 3000
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_OnlyATLASJet.yaml --Observable Jet --EnergyMin 3000
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_OnlyATLASJet.yaml --Observable Jet --EnergyMax 3000
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_OnlyCMSJet.yaml --Observable Jet --EnergyMin 3000
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_OnlyCMSJet.yaml --Observable Jet --EnergyMax 3000
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4.yaml --Observable Jet --EnergyMax 1000
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4.yaml --Observable Hadron --EnergyMax 1000
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_OnlyCMSHadron.yaml --Observable Hadron
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_OnlyALICEHadron.yaml --Observable Hadron
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_OnlyATLASHadron.yaml --Observable Hadron
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_OnlyRHICHadron.yaml --Observable Hadron
make RunSequence


exit

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_PTCut20.yaml
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_PTCut20.yaml --Observable Jet
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_PTCut20.yaml --Observable Hadron
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_OnlyALICEJet.yaml --Observable Jet
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_OnlyATLASJet.yaml --Observable Jet
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_OnlyCMSJet.yaml --Observable Jet
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_OnlySmallJet.yaml --Observable Jet
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_OnlyALICEJet.yaml
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_OnlyATLASJet.yaml
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_OnlyCMSJet.yaml
make RunSequence

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_OnlySmallJet.yaml
make RunSequence

exit

python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N4_CFactorTest.yaml --Observable Jet
make RunSequence

python3 SetupAnalysis.py --Config yaml/Binomial20221007RBF_N4.yaml
make RunSequence

# python3 SetupAnalysis.py --Config yaml/Binomial20221007Matern_N4.yaml
# make RunSequence

python3 SetupAnalysis.py --Config yaml/Binomial20221007RBF_N4.yaml --DoSmoothing
make RunSequence

python3 SetupAnalysis.py --Config yaml/Binomial20221007RBF_N4_GoodPCA.yaml
make RunSequence

python3 SetupAnalysis.py --Config yaml/Binomial20221007RBF_N4.yaml --Observable Hadron
make RunSequence

python3 SetupAnalysis.py --Config yaml/Binomial20221007RBF_N4.yaml --Observable Jet
make RunSequence

python3 SetupAnalysis.py --Config yaml/Binomial20221007RBF_N4.yaml --CentralityMax 10
make RunSequence

python3 SetupAnalysis.py --Config yaml/Binomial20221007RBF_N4.yaml --CentralityMin 10
make RunSequence

python3 SetupAnalysis.py --Config yaml/Binomial20221007RBF_N4.yaml --EnergyMin 1000
make RunSequence

python3 SetupAnalysis.py --Config yaml/Binomial20221007RBF_N4.yaml --EnergyMax 1000
make RunSequence

python3 SetupAnalysis.py --Config yaml/Binomial20221007RBF_N4.yaml --EnergyMin 3000
make RunSequence

python3 SetupAnalysis.py --Config yaml/Binomial20221007RBF_N4.yaml --EnergyMin 1000 --EnergyMax 3000
make RunSequence

python3 SetupAnalysis.py --Config yaml/Binomial20221007RBF_N4.yaml --EnergyMax 1000 --CentralityMax 10
make RunSequence

python3 SetupAnalysis.py --Config yaml/Binomial20221007RBF_N4.yaml --EnergyMin 1000 --CentralityMax 10
make RunSequence

