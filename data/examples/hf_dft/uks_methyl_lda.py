#!/usr/bin/env python
#JSON {"lot": "UKS/6-31G(d)",
#JSON  "scf": "ODASCFSolver",
#JSON  "er": "cholesky",
#JSON  "difficulty": 3,
#JSON  "description": "Basic UKS DFT example with LDA exhange-correlation functional (Dirac+VWN)"}

import numpy as np
from horton import *  # pylint: disable=wildcard-import,unused-wildcard-import


# Load the coordinates from file.
# Use the XYZ file from HORTON's test data directory.
fn_xyz = context.get_fn('test/methyl.xyz')
mol = IOData.from_file(fn_xyz)

# Create a Gaussian basis set
obasis = get_gobasis(mol.coordinates, mol.numbers, '6-31g(d)')

# Compute Gaussian integrals
olp = obasis.compute_overlap()
kin = obasis.compute_kinetic()
na = obasis.compute_nuclear_attraction(mol.coordinates, mol.pseudo_numbers)
er_vecs = obasis.compute_electron_repulsion_cholesky()

# Define a numerical integration grid needed the XC functionals
grid = BeckeMolGrid(mol.coordinates, mol.numbers, mol.pseudo_numbers)

# Create alpha orbitals
orb_alpha = Orbitals(obasis.nbasis)
orb_beta = Orbitals(obasis.nbasis)

# Initial guess
guess_core_hamiltonian(olp, kin + na, orb_alpha, orb_beta)

# Construct the restricted HF effective Hamiltonian
external = {'nn': compute_nucnuc(mol.coordinates, mol.pseudo_numbers)}
terms = [
    UTwoIndexTerm(kin, 'kin'),
    UDirectTerm(er_vecs, 'hartree'),
    UGridGroup(obasis, grid, [
        ULibXCLDA('x'),
        ULibXCLDA('c_vwn'),
    ]),
    UTwoIndexTerm(na, 'ne'),
]
ham = UEffHam(terms, external)

# Decide how to occupy the orbitals (5 alpha electrons, 4 beta electrons)
occ_model = AufbauOccModel(5, 4)

# Converge WFN with Optimal damping algorithm (ODA) SCF
# - Construct the initial density matrix (needed for ODA).
occ_model.assign(orb_alpha, orb_beta)
dm_alpha = orb_alpha.to_dm()
dm_beta = orb_beta.to_dm()
# - SCF solver
scf_solver = ODASCFSolver(1e-6)
scf_solver(ham, olp, occ_model, dm_alpha, dm_beta)

# Derive orbitals (coeffs, energies and occupations) from the Fock and density
# matrices. The energy is also computed to store it in the output file below.
fock_alpha = np.zeros(olp.shape)
fock_beta = np.zeros(olp.shape)
ham.reset(dm_alpha, dm_beta)
ham.compute_energy()
ham.compute_fock(fock_alpha, fock_beta)
orb_alpha.from_fock_and_dm(fock_alpha, dm_alpha, olp)
orb_beta.from_fock_and_dm(fock_beta, dm_beta, olp)

# Assign results to the molecule object and write it to a file, e.g. for
# later analysis. Note that the ODA algorithm can only really construct an
# optimized density matrix and no orbitals.
mol.title = 'UKS computation on methyl'
mol.energy = ham.cache['energy']
mol.obasis = obasis
mol.orb_alpha = orb_alpha
mol.orb_beta = orb_beta
mol.dm_alpha = dm_alpha
mol.dm_beta = dm_beta

# useful for visualization:
mol.to_file('methyl.molden')
# useful for post-processing (results stored in double precision):
mol.to_file('methyl.h5')

# CODE BELOW IS FOR horton-regression-test.py ONLY. IT IS NOT PART OF THE EXAMPLE.
rt_results = {
    'energy': ham.cache['energy'],
    'orb_alpha': orb_alpha.energies,
    'orb_beta': orb_beta.energies,
    'nn': ham.cache["energy_nn"],
    'kin': ham.cache["energy_kin"],
    'ne': ham.cache["energy_ne"],
    'grid': ham.cache["energy_grid_group"],
    'hartree': ham.cache["energy_hartree"],
}
# BEGIN AUTOGENERATED CODE. DO NOT CHANGE MANUALLY.
rt_previous = {
    'energy': -39.412861352038362,
    'orb_alpha': np.array([
        -9.7986641740613987, -0.59037356181925227, -0.35712112475716062,
        -0.35711814127330571, -0.17897624391068653, 0.064414593683065985,
        0.12859550665244227, 0.1286022613079241, 0.48643392993932805, 0.51815798698535132,
        0.51816073449908595, 0.64799772935183231, 0.81867137022954717, 0.8186825418101783,
        0.87717078206804322, 1.5932713394377551, 1.5933036087995407, 1.8896038416439345,
        2.0355150501432409, 2.0355833955135787
    ]),
    'orb_beta': np.array([
        -9.7834425568662748, -0.55780396666508092, -0.34266462908198192,
        -0.34266130308089421, -0.10290590481176703, 0.079713388245337261,
        0.13851412062905316, 0.13852069091005992, 0.53435326811086259,
        0.53435664070764843, 0.5484929378783111, 0.66762277681399684, 0.82654978013430225,
        0.82656358980864608, 0.90748481446416474, 1.6580879405897262, 1.6581212526856688,
        1.9652075912613196, 2.0560189475043336, 2.0560890565988919
    ]),
    'grid': -6.002585769463057,
    'hartree': 28.075840265574,
    'kin': 39.23182259169053,
    'ne': -109.79772338250348,
    'nn': 9.0797849426636361,
}
