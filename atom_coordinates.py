import numpy as np

# Values for bond length and angle obtained from the literature 
hydrides_literature = {
    # name: [bond_length, bond_angle]
    'H2O': [0.9572, 104.52],
    'H2S': [1.3356, 92.11],
    'H2Se': [1.460, 90.9],
    'H2Te': [1.651, 90.2635],
    # 'H2Po': []
}

# Values for bond length and angle obtained from Spartan calculation 
hydrides_spartan = {
    # name: [bond_length, bond_angle]
    'H2O': [0.963, 104.12],
    'H2S': [1.343, 93.14],
    'H2Se': [1.472, 91.08],
    'H2Te': [1.658, 90.08],
    # 'H2Po': []
}

# ASSIGN NECESSARY PARAMETER HERE
hydrides = hydrides_spartan

def coordinates(mol_parameters: list) -> list:
    bond_length = mol_parameters[0]
    bond_angle = mol_parameters[1]

    secondary_angle = 180 - bond_angle
    angle_rad = (secondary_angle * np.pi)/180

    atom_matrix = np.array([
        [-bond_length, 0.000, 0.000],
        [0.000, 0.000, 0.000],
        [bond_length * np.cos(angle_rad), bond_length * np.sin(angle_rad), 0.000]
    ])

    return atom_matrix.round(4)

for i in hydrides:
    print('#' * 10)
    print(f'MOLECULE: {i} BOND LENGTH: {hydrides[i][0]} BOND ANGLE: {hydrides[i][1]}')
    print(coordinates(hydrides[i]))