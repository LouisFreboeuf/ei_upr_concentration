import os
import pandas as pd
import xml.etree.ElementTree as ET

class EcoSpoldProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.tree = ET.parse(file_path)
        self.root = self.tree.getroot()
        self.namespaces = {'ns': 'http://www.EcoInvent.org/EcoSpold02'}

    def extract_general_info(self):
        info = {}

        # Activity Name
        info['Activity Name'] = self.root.find('.//ns:activityName', self.namespaces).text

        # General Comment
        general_comment = self.root.findall('.//ns:generalComment/ns:text', self.namespaces)
        info['General Comment'] = [comment.text for comment in general_comment]

        # Geography
        info['Geography'] = self.root.find('.//ns:geography/ns:shortname', self.namespaces).text

        # Technology Comment
        info['Technology Comment'] = self.root.find('.//ns:technology/ns:comment/ns:text', self.namespaces).text

        # Time Period
        time_period = self.root.find('.//ns:timePeriod', self.namespaces)
        info['Start Date'] = time_period.get('startDate')
        info['End Date'] = time_period.get('endDate')
        info['Is Valid Entire Period'] = time_period.get('isDataValidForEntirePeriod')
        info['Time Comments'] = [comment.text for comment in time_period.findall('.//ns:comment/ns:text', self.namespaces)]

        # Macroeconomic Scenario
        macro_scenario = self.root.find('.//ns:macroEconomicScenario', self.namespaces)
        info['Macro Scenario'] = macro_scenario.find('.//ns:name', self.namespaces).text

        # Reference Product (First Intermediate Exchange)
        intermediate_exchange = self.root.find('.//ns:intermediateExchange', self.namespaces)
        if intermediate_exchange is not None:
            info['Reference Product'] = {
                'Name': intermediate_exchange.find('.//ns:name', self.namespaces).text,
                'Amount': intermediate_exchange.get('amount'),
                'Unit': intermediate_exchange.find('.//ns:unitName', self.namespaces).text,
                'Comment': intermediate_exchange.find('.//ns:comment', self.namespaces).text
            }
            # Properties of the reference
            properties = intermediate_exchange.findall('.//ns:property', self.namespaces)
            info['Reference Properties'] = [
                {
                    'Name': prop.find('.//ns:name', self.namespaces).text,
                    'Amount': prop.get('amount'),
                    'Unit': prop.find('.//ns:unitName', self.namespaces).text
                }
                for prop in properties
            ]

        return info

    def extract_exchanges(self, exchange_type):
        if exchange_type == "intermediate":
            exchanges = self.root.findall('.//ns:intermediateExchange', self.namespaces)
        elif exchange_type == "elementary":
            exchanges = self.root.findall('.//ns:elementaryExchange', self.namespaces)
        else:
            raise ValueError("Invalid exchange type. Use 'intermediate' or 'elementary'.")

        exchange_data = []

        for exchange in exchanges:
            exchange_dict = {
                'ID': exchange.get('id'),
                'Name': exchange.find('.//ns:name', self.namespaces).text,
                'Amount': exchange.get('amount'),
                'Unit': exchange.find('.//ns:unitName', self.namespaces).text,
                'Comment': exchange.find('.//ns:comment', self.namespaces).text if exchange.find('.//ns:comment', self.namespaces) is not None else "No comment"
            }

            # Compartment
            if exchange_type == "elementary":
                # Elementary flows have standard compartment info
                compartment = exchange.find('.//ns:compartment', self.namespaces)
                exchange_dict['Compartment'] = compartment.find('.//ns:compartment', self.namespaces).text if compartment is not None else "No compartment"
                exchange_dict['Subcompartment'] = compartment.find('.//ns:subcompartment', self.namespaces).text if compartment is not None else "No subcompartment"
            else:
                # Intermediate flows - use classification and geography
                classification = exchange.find('.//ns:classification/ns:classificationValue', self.namespaces)
                exchange_dict['Compartment'] = classification.text if classification is not None else "Technosphere"

                # Get geography as subcompartment
                geography = exchange.find('.//ns:geography/ns:shortname', self.namespaces)
                exchange_dict['Subcompartment'] = geography.text if geography is not None else "No subcompartment"

            # Uncertainty
            uncertainty = exchange.find('.//ns:uncertainty', self.namespaces)
            if uncertainty is not None:
                lognormal = uncertainty.find('.//ns:lognormal', self.namespaces)
                exchange_dict['Uncertainty Mean Value'] = lognormal.get('meanValue') if lognormal is not None else "No mean value"
                exchange_dict['Uncertainty Variance'] = lognormal.get('variance') if lognormal is not None else "No variance"
            else:
                exchange_dict['Uncertainty Mean Value'] = "No uncertainty"
                exchange_dict['Uncertainty Variance'] = "No uncertainty"

            # Flow Type and Group
            input_group = exchange.find('.//ns:inputGroup', self.namespaces)
            output_group = exchange.find('.//ns:outputGroup', self.namespaces)
            if input_group is not None:
                exchange_dict['Flow Type'] = "Input"
                exchange_dict['Group Number'] = input_group.text
            elif output_group is not None:
                exchange_dict['Flow Type'] = "Output"
                exchange_dict['Group Number'] = output_group.text
            else:
                exchange_dict['Flow Type'] = "Unknown"
                exchange_dict['Group Number'] = "No group"

            # Properties
            properties = exchange.findall('.//ns:property', self.namespaces)
            for prop in properties:
                prop_name = prop.find('.//ns:name', self.namespaces).text
                prop_amount = prop.get('amount')
                prop_unit = prop.find('.//ns:unitName', self.namespaces).text
                exchange_dict[f"{prop_name} ({prop_unit})"] = prop_amount

            exchange_data.append(exchange_dict)

        return pd.DataFrame(exchange_data)

    def convert_numerical_columns(self, df_intermediate, df_elementary):
        """
        Converts numeric-like columns in the DataFrames to proper numerical format (floats).
        """
        # Intermediate: convert Amount and dry mass
        if 'Amount' in df_intermediate.columns:
            df_intermediate['Amount'] = pd.to_numeric(df_intermediate['Amount'], errors='coerce').fillna(0)
        if 'dry mass (kg)' in df_intermediate.columns:
            df_intermediate['dry mass (kg)'] = pd.to_numeric(df_intermediate['dry mass (kg)'], errors='coerce').fillna(0)

        # Intermediate: convert all dimensionless properties
        for col in df_intermediate.columns:
            if '(dimensionless)' in col:
                df_intermediate[col] = pd.to_numeric(df_intermediate[col], errors='coerce').fillna(0)

        # Elementary: convert Amount
        if 'Amount' in df_elementary.columns:
            df_elementary['Amount'] = pd.to_numeric(df_elementary['Amount'], errors='coerce').fillna(0)

        return df_intermediate, df_elementary

    def save_to_excel(self, output_file):
        df_intermediate = self.extract_exchanges("intermediate")
        df_elementary = self.extract_exchanges("elementary")

        # Convert numeric columns before saving
        df_intermediate, df_elementary = self.convert_numerical_columns(df_intermediate, df_elementary)

        with pd.ExcelWriter(output_file, engine='openpyxl', mode='w') as writer:
            df_intermediate.to_excel(writer, sheet_name='intermediate_exchanges', index=False)
            df_elementary.to_excel(writer, sheet_name='elementary_exchanges', index=False)

        print(f"DataFrame saved to: {os.path.abspath(output_file)}")

# Usage
spold_path = r"C:\my\path\to\the\ecoinvent_unit-process.spold"
processor = EcoSpoldProcessor(spold_path)

# General Info Extraction
general_info = processor.extract_general_info()
# print(general_info)

# Exchange Data Extraction
df_intermediate = processor.extract_exchanges("intermediate")
df_elementary = processor.extract_exchanges("elementary")

# Save all to an Excel File for Manual treatment
extractor.save_to_excel("unit-process_name.xlsx")
