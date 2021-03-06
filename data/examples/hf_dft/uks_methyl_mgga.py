#!/usr/bin/env python
#JSON {"lot": "UKS/6-31G(d)",
#JSON  "scf": "CDIISSCFSolver",
#JSON  "er": "cholesky",
#JSON  "difficulty": 6,
#JSON  "description": "Basic UKS DFT example with MGGA exhange-correlation functional (TPSS)"}

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
        ULibXCMGGA('x_tpss'),
        ULibXCMGGA('c_tpss'),
    ]),
    UTwoIndexTerm(na, 'ne'),
]
ham = UEffHam(terms, external)

# Decide how to occupy the orbitals (5 alpha electrons, 4 beta electrons)
occ_model = AufbauOccModel(5, 4)

# Converge WFN with CDIIS SCF
# - Construct the initial density matrix (needed for CDIIS).
occ_model.assign(orb_alpha, orb_beta)
dm_alpha = orb_alpha.to_dm()
dm_beta = orb_beta.to_dm()
# - SCF solver
scf_solver = CDIISSCFSolver(1e-6)
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
# later analysis. Note that the CDIIS algorithm can only really construct an
# optimized density matrix and no orbitals.
mol.title = 'UKS computation on methyl'
mol.energy = ham.cache['energy']
mol.obasis = obasis
mol.orb_alpha = orb_alpha
mol.orb_beta = orb_beta
mol.dm_alpha = dm_alpha
mol.dm_beta = dm_beta

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
    'energy': -39.836677347925914,
    'orb_alpha': np.array([
        -10.019635076738147, -0.61357555665158736, -0.3628121339087883,
        -0.36276528782852813, -0.19070293326772045, 0.071676580515679725,
        0.1451627609382326, 0.14520445336541474, 0.51037249458810541, 0.55245497246844399,
        0.55247011455993678, 0.66897270052023006, 0.84604700858521387,
        0.84613026545140801, 0.89858158554272938, 1.6194517568114566, 1.6194677518472744,
        1.9300340527577873, 2.0952910889031027, 2.0961171453114171
    ]),
    'orb_beta': np.array([
        -10.004003922798798, -0.5755426452796184, -0.35601452017897062,
        -0.35588391063394165, -0.06548534259187741, 0.098337149121920125,
        0.1595980803482438, 0.15986087404787613, 0.56917620502894739, 0.56946718254784001,
        0.60089298391388379, 0.70441988947800527, 0.87990225342684414,
        0.88198311255364803, 0.95807927778738833, 1.7277678928512459, 1.7299240596423406,
        2.0576938854035931, 2.174113280602203, 2.1750154723644353
    ]),
    'grid': -6.447610544950923,
    'hartree': 28.092381575581616,
    'kin': 39.36717793738765,
    'ne': -109.9284112586079,
    'nn': 9.0797849426636361,
}
