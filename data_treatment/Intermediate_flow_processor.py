import pandas as pd

class IntermediateFlowProcessor:
    def __init__(self, periodic_table):
        self.periodic_table = periodic_table
        self.element_symbols = list(periodic_table.keys())

    def get_m3_to_kg(self, df):
        # Process kg flows
        df_kg = df[df['Unit'] == 'kg'].copy()
        df_kg = self.process_dataframe(df_kg)

        # Process m3 flows
        df_m3 = df[df['Unit'] == 'm3'].copy()
        df_m3 = self.process_dataframe(df_m3)

        # Convert columns to numeric
        df_m3['Amount'] = pd.to_numeric(df_m3['Amount'], errors='coerce')
        if 'wet mass (kg)' in df_m3.columns:
            df_m3['wet mass (kg)'] = pd.to_numeric(df_m3['wet mass (kg)'], errors='coerce')
        if 'dry mass (kg)' in df_m3.columns:
            df_m3['dry mass (kg)'] = pd.to_numeric(df_m3['dry mass (kg)'], errors='coerce')

        # Apply conversions
        for index, row in df_m3.iterrows():
            if 'wet mass (kg)' in df_m3.columns:
                df_m3.at[index, 'Amount'] = df_m3.at[index, 'Amount'] * df_m3.at[index, 'wet mass (kg)']
            else:
                df_m3.at[index, 'Amount'] *= 1000  # m³ → kg conversion

            if 'dry mass (kg)' in df_m3.columns:
                df_m3.at[index, 'dry mass (kg)'] /= 1000  # Scale dry mass

            df_m3.at[index, 'Unit'] = 'kg'  # Update unit

        return pd.concat([df_kg, df_m3], ignore_index=True)

    def process_dataframe(self, df):
        if not df.empty:
            numeric_cols = ['Amount', 'dry mass (kg)'] + \
                           [f'{el} content (dimensionless)' for el in self.element_symbols] + \
                           ['carbon content, fossil (dimensionless)',
                            'carbon content, non-fossil (dimensionless)',
                            'water content (dimensionless)']

            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        return df

    def calculate_flow_composition(self, df_intermediate):
        df_intermediate_kg = df_intermediate[df_intermediate['Unit'] == 'kg'].copy()

        numeric_cols = [col for col in df_intermediate_kg.columns
                        if 'content' in col or col in ['dry mass (kg)', 'Amount']]
        df_intermediate_kg[numeric_cols] = df_intermediate_kg[numeric_cols].apply(
            pd.to_numeric, errors='coerce').fillna(0)

        element_data = {}
        for symbol in self.element_symbols:
            element_name = self.periodic_table[symbol]
            content_col = f"{element_name} content (dimensionless)"
            if content_col in df_intermediate_kg.columns:
                element_data[symbol] = df_intermediate_kg[content_col] * df_intermediate_kg['dry mass (kg)']
            else:
                element_data[symbol] = 0.0

        if 'water content (dimensionless)' in df_intermediate_kg.columns:
            water_content = df_intermediate_kg['water content (dimensionless)'] * df_intermediate_kg['dry mass (kg)']
            element_data['H'] += (2 * 1.008 / (2 * 1.008 + 15.999)) * water_content
            element_data['O'] += (15.999 / (2 * 1.008 + 15.999)) * water_content

        element_df = pd.DataFrame(element_data, index=df_intermediate_kg.index)
        element_df['rest'] = (1 - element_df.sum(axis=1)).clip(lower=0)

        base_df = df_intermediate_kg.copy()
        base_df = base_df.rename(columns={'Name': 'Flow Name'})
        base_df['Sub Process'] = 'No information'

        standard_columns = [
            'Flow Name',
            'Sub Process',
            'Amount',
            'Unit',
            'Flow Type',
            'Compartment',
            'Subcompartment'
        ]

        result_df = pd.concat([
            base_df[standard_columns],
            element_df[self.element_symbols],
            element_df[['rest']]
        ], axis=1)

        return result_df

    def flip_negative_amounts(self, df_intermediate):
        df_intermediate = df_intermediate.copy()
        df_intermediate['Amount'] = pd.to_numeric(df_intermediate['Amount'], errors='coerce')
        df_intermediate.loc[df_intermediate['Amount'] < 0, 'Flow Type'] = 'Output'
        df_intermediate.loc[df_intermediate['Amount'] < 0, 'Amount'] = -df_intermediate['Amount']
        return df_intermediate

# Usage example
# periodic_table = {...}  # Define your periodic table here
# processor = IntermediateFlowProcessor(periodic_table)
# df_intermediate1 = processor.get_m3_to_kg(df_intermediate)
# df_intermediate2 = processor.flip_negative_amounts(df_intermediate1)
# result_df_intermediate = processor.calculate_flow_composition(df_intermediate2)
# print(result_df_intermediate)
