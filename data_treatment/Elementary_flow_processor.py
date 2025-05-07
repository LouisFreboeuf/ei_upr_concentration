import pandas as pd

class ElementaryFlowProcessor:
    def __init__(self):
        # Periodic table with names and symbols
        self.periodic_table = {
            "H": "hydrogen", "He": "helium", "Li": "lithium", "Be": "beryllium", "B": "boron", "C": "carbon",
            "N": "nitrogen", "O": "oxygen", "F": "fluorine", "Ne": "neon", "Na": "sodium", "Mg": "magnesium",
            "Al": "aluminium", "Si": "silicon", "P": "phosphorus", "S": "sulfur", "Cl": "chlorine", "Ar": "argon",
            "K": "potassium", "Ca": "calcium", "Sc": "scandium", "Ti": "titanium", "V": "vanadium",
            "Cr": "chromium", "Mn": "manganese", "Fe": "iron", "Co": "cobalt", "Ni": "nickel", "Cu": "copper",
            "Zn": "zinc", "Ga": "gallium", "Ge": "germanium", "As": "arsenic", "Se": "selenium", "Br": "bromine",
            "Kr": "krypton", "Rb": "rubidium", "Sr": "strontium", "Y": "yttrium", "Zr": "zirconium",
            "Nb": "niobium", "Mo": "molybdenum", "Tc": "technetium", "Ru": "ruthenium", "Rh": "rhodium",
            "Pd": "palladium", "Ag": "silver", "Cd": "cadmium", "In": "indium", "Sn": "tin", "Sb": "antimony",
            "Te": "tellurium", "I": "iodine", "Xe": "xenon", "Cs": "cesium", "Ba": "barium", "La": "lanthanum",
            "Ce": "cerium", "Pr": "praseodymium", "Nd": "neodymium", "Pm": "promethium", "Sm": "samarium",
            "Eu": "europium", "Gd": "gadolinium", "Tb": "terbium", "Dy": "dysprosium", "Ho": "holmium",
            "Er": "erbium", "Tm": "thulium", "Yb": "ytterbium", "Lu": "lutetium", "Hf": "hafnium",
            "Ta": "tantalum", "W": "tungsten", "Re": "rhenium", "Os": "osmium", "Ir": "iridium", "Pt": "platinum",
            "Au": "gold", "Hg": "mercury", "Tl": "thallium", "Pb": "lead", "Bi": "bismuth", "Po": "polonium",
            "At": "astatine", "Rn": "radon", "Fr": "francium", "Ra": "radium", "Ac": "actinium", "Th": "thorium",
            "Pa": "protactinium", "U": "uranium", "Np": "neptunium", "Pu": "plutonium", "Am": "americium",
            "Cm": "curium", "Bk": "berkelium", "Cf": "californium", "Es": "einsteinium", "Fm": "fermium",
            "Md": "mendelevium", "No": "nobelium", "Lr": "lawrencium", "Rf": "rutherfordium", "Db": "dubnium",
            "Sg": "seaborgium", "Bh": "bohrium", "Hs": "hassium", "Mt": "meitnerium", "Ds": "darmstadtium",
            "Rg": "roentgenium", "Cn": "copernicium", "Nh": "nihonium", "Fl": "flerovium", "Mc": "moscovium",
            "Lv": "livermorium", "Ts": "tennessine", "Og": "oganesson"
        }
        self.elements = list(self.periodic_table.keys())

        # Molar masses (g/mol)
        self.molar_masses = {
            'hydrogen': 1.008,
            'carbon': 12.011,
            'nitrogen': 14.007,
            'oxygen': 15.999,
            'phosphorus': 30.974,
            'sulfur': 32.06
        }

        # Common compound compositions
        self.compound_compositions = {
            'Nitrogen oxides': {'nitrogen': self.molar_masses['nitrogen'] / (self.molar_masses['nitrogen'] + 2 * self.molar_masses['oxygen']),
                                'oxygen': 2 * self.molar_masses['oxygen'] / (self.molar_masses['nitrogen'] + 2 * self.molar_masses['oxygen'])},
            'carbon dioxide': {'carbon': self.molar_masses['carbon'] / (self.molar_masses['carbon'] + 2 * self.molar_masses['oxygen']),
                               'oxygen': 2 * self.molar_masses['oxygen'] / (self.molar_masses['carbon'] + 2 * self.molar_masses['oxygen'])},
            'Sulfur dioxide': {'sulfur': self.molar_masses['sulfur'] / (self.molar_masses['sulfur'] + 2 * self.molar_masses['oxygen']),
                               'oxygen': 2 * self.molar_masses['oxygen'] / (self.molar_masses['sulfur'] + 2 * self.molar_masses['oxygen'])},
            'Sulfuric acid': {'sulfur': self.molar_masses['sulfur'] / (self.molar_masses['sulfur'] + 4 * self.molar_masses['oxygen'] + 2 * self.molar_masses['hydrogen']),
                              'oxygen': 4 * self.molar_masses['oxygen'] / (self.molar_masses['sulfur'] + 4 * self.molar_masses['oxygen'] + 2 * self.molar_masses['hydrogen']),
                              'hydrogen': 2 * self.molar_masses['hydrogen'] / (self.molar_masses['sulfur'] + 4 * self.molar_masses['oxygen'] + 2 * self.molar_masses['hydrogen'])},
            'Ammonium': {'nitrogen': self.molar_masses['nitrogen'] / (self.molar_masses['nitrogen'] + 4 * self.molar_masses['hydrogen']),
                         'hydrogen': 4 * self.molar_masses['hydrogen'] / (self.molar_masses['nitrogen'] + 4 * self.molar_masses['hydrogen'])},
            'Phosphorus': {'phosphorus': 1.0},
            'Water': {'hydrogen': 2 * self.molar_masses['hydrogen'] / (2 * self.molar_masses['hydrogen'] + self.molar_masses['oxygen']),
                      'oxygen': self.molar_masses['oxygen'] / (2 * self.molar_masses['hydrogen'] + self.molar_masses['oxygen'])},
        }

    def process_dataframe(self, df):
        if not df.empty:
            # Convert all numeric columns
            numeric_cols = ['Amount', 'dry mass (kg)'] + \
                           [f'{el} content (dimensionless)' for el in self.elements] + \
                           ['carbon content, fossil (dimensionless)',
                            'carbon content, non-fossil (dimensionless)',
                            'water content (dimensionless)']

            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            # Exclude specific flows
            excluded_flows = [
                "BOD5, Biological Oxygen Demand",
                "COD, Chemical Oxygen Demand",
                "DOC, Dissolved Organic Carbon",
                "TOC, Total Organic Carbon"
            ]

            df = df[~df['Name'].isin(excluded_flows)]

        return df

    def get_grouped_flows(self, df_elementary):
        volume_to_mass_conversion_factors = {
            'water': {'SCTP_factor': 1000}  # 1m3 = 1000kg of water
        }

        # Process kg flows
        df_kg = df_elementary[df_elementary['Unit'] == 'kg'].copy()
        df_kg = self.process_dataframe(df_kg)

        # Process m3 flows and convert to kg
        df_m3 = df_elementary[df_elementary['Unit'] == 'm3'].copy()
        df_m3 = self.process_dataframe(df_m3)

        for index, row in df_m3.iterrows():
            flow_name = row['Name'].strip().lower()
            if 'water' in flow_name:
                conversion_factor = volume_to_mass_conversion_factors['water']['SCTP_factor']
                df_m3.at[index, 'Amount'] *= conversion_factor
                df_m3.at[index, 'Unit'] = 'kg'

        # Combine the kg flows and converted m3 flows
        df_combined = pd.concat([df_kg, df_m3], ignore_index=True)

        # Calculate the total sum of all grouped flows
        total_sum_all_flows = df_combined['Amount'].sum()

        # Group by Compartment and Subcompartment
        grouped_kg = df_combined.groupby(['Compartment', 'Subcompartment', 'Flow Type'])

        return df_combined, grouped_kg

    def calculate_elemental_composition(self, df_combined, grouped_kg):
        results = []
        elemental_composition = {symbol: 0.0 for symbol in self.periodic_table.keys()}

        for (comp, subcomp, flow_type), group in grouped_kg:
            total_amount = group['Amount'].sum()
            group_composition = {symbol: 0.0 for symbol in self.periodic_table.keys()}

            for index, row in group.iterrows():
                amount = row['Amount']
                flow_name = row['Name'].lower()

                for compound, composition in self.compound_compositions.items():
                    if compound.lower() in flow_name:
                        for element_name, fraction in composition.items():
                            element_content = fraction * amount
                            symbol = [key for key, value in self.periodic_table.items() if value == element_name][0]
                            group_composition[symbol] += element_content

                for element_name, symbol in self.periodic_table.items():
                    content_col = f"{element_name} content (dimensionless)"
                    if content_col in df_combined.columns:
                        element_content = row[content_col] * amount
                        group_composition[symbol] += element_content

            for symbol in group_composition:
                group_composition[symbol] /= total_amount

            group_result = {'Compartment': comp, 'Subcompartment': subcomp, 'Flow Type': flow_type, 'Amount': total_amount}
            group_result.update(group_composition)
            results.append(group_result)

        df_el_combined = pd.DataFrame(results)
        return df_el_combined

    def calculate_total_concentration(self, df_el_combined):
        results = []

        for index, row in df_el_combined.iterrows():
            total_concentration_sum = sum(row[symbol] for symbol in self.periodic_table.keys() if symbol in row)
            rest_value = 1 - total_concentration_sum

            if total_concentration_sum != 1:
                df_el_combined.at[index, 'rest'] = rest_value
            else:
                df_el_combined.at[index, 'rest'] = 0

            direction = "to" if row['Flow Type'] == "Output" else "from"
            result = {
                'Flow Name': f"{row['Flow Type']} Elementary flow {direction} {row['Compartment']}, {row['Subcompartment']}",
                'Sub Process': 'No information',
                'Amount': row['Amount'],
                'Unit': 'kg',
                'Flow Type': row['Flow Type'],
                'Compartment': row['Compartment'],
                'Subcompartment': row['Subcompartment'],
                'rest': rest_value
            }

            for symbol in self.periodic_table.keys():
                if symbol in row:
                    result[symbol] = row[symbol]

            results.append(result)

        df_total_concentration = pd.DataFrame(results)
        cols = [col for col in df_total_concentration.columns if col != 'rest'] + ['rest']
        df_total_concentration = df_total_concentration[cols]

        return df_total_concentration

# Usage example
# processor = ElementaryFlowProcessor()
# df_combined, grouped_kg = processor.get_grouped_flows(df_elementary)
# df_el_combined = processor.calculate_elemental_composition(df_combined, grouped_kg)
# df_total_concentration = processor.calculate_total_concentration(df_el_combined)
# print(df_total_concentration)
