from cs_api import BASE_URL
import cs_api.client_side_api as api
import tkinter as tk
from tkinter import filedialog
import pandas as pd

import os
from zipfile import ZipFile
import matplotlib.pyplot as plt


def main():
    res = api.get_reset_database(base_url=BASE_URL)
    account, dataset, model = api.generate_template()

    # 1. Register and Login Account
    account.update({"username": "felixarjuna"})
    account.update({"password": "password"})

    api.post_register(base_url=BASE_URL, body=account)
    ACCESS_TOKEN = api.post_login(base_url=BASE_URL, account=account)

    # 2. Create Dataset
    name = 'ESM 5 - Perfect Index'
    desc = 'Test model with long periods'
    dataset.update({'name': name})
    dataset.update({'description': desc})
    dataset.update({'number_of_time_steps': 35040})
    dataset.update({'hours_per_time_step': 4})
    dataset = api.post_create_dataset(base_url=BASE_URL, dataset=dataset, access_token=ACCESS_TOKEN)
    dataset_id = dataset.get('id')

    # 3. Populate Model with ZIP File
    # filename = "esm6.zip"
    # data_dir = os.path.join(os.path.dirname(__file__), "data")
    # data = os.path.join(data_dir, filename)
    tk.Tk().withdraw()
    data = filedialog.askopenfilename()

    dataset = api.post_upload_zip(base_url=BASE_URL, data=data, dataset_id=dataset_id, access_token=ACCESS_TOKEN)
    print(dataset)

    # 4. Create Model
    model.update({'name': name})
    model.update({'description': desc})
    model.update({'ref_dataset': dataset_id})
    model = api.post_create_model(base_url=BASE_URL, model=model, access_token=ACCESS_TOKEN)
    model_id = model.get('id')

    # 5. Optimize Model
    filename = api.get_optimize_model(base_url=BASE_URL, output='json', model_id=model_id, access_token=ACCESS_TOKEN)

    # 6. Displaying the results
    # filename = "/Users/felixarjuna/sciebo/HiWi Felix/Arbeit/Lib for EnSysMod/API/EnSysMod_API_PY/output/ESM 4.xlsx"
    filename = "./output/ESM 5 - Perfect Index.zip"

    plot_result(file_path=filename)


def plot_result(file_path: str):
    import openpyxl
    import matplotlib
    from ast import literal_eval

    dir_graph = os.path.join(os.path.dirname(__file__), "graph")
    if not os.path.exists(dir_graph):
        os.mkdir(dir_graph)
    # Change 'default' to the style that you want to try out
    matplotlib.style.use('dark_background')

    template_names = {
        "SourceSinkSummary": "SourceSinkOptSummary_1dim",
        "SourceSinkTD": "SourceSink_TDoptVar_1dim",
        "SourceSinkTI": "SourceSink_TIoptVar_1dim",
        "TransmissionSummary": "TransmissionOptSummary_2dim",
        "TransmissionTD": "Transmission_TDoptVar_2dim",
        "TransmissionTI": "Transmission_TIoptVar_2dim"
    }

    if file_path.endswith(".zip"):
        with ZipFile(file_path, 'r') as zip_file:
            listOfFiles = zip_file.namelist()
            files_filtered = list(filter(lambda x: x in listOfFiles and x.endswith(".json"), listOfFiles))
            for file in files_filtered:
                if template_names["SourceSinkSummary"] in file:
                    with zip_file.open(file) as f:
                        df = pd.read_json(f, orient='index')
                        new_index = [literal_eval(index) for index in df.index.values]
                        df.index = pd.MultiIndex.from_tuples(new_index)

                        variable_name = ("My House", "operation", "[W_el*h/a]")
                        output_path = os.path.join(dir_graph, f"{variable_name[0]}_summary.png")
                        plot_summary(dataframe=df, variable_name=variable_name,
                                     output_path=output_path, title='Total Electricity Consumption', xlabel='Countries', ylabel="Electricity in ${W_{el}h}$")

                        variable_name = ("Wind turbine", "capacity", "[W_el]")
                        output_path = os.path.join(dir_graph, f"{variable_name[0]}_summary.png")
                        plot_summary(dataframe=df, variable_name=variable_name,
                                     output_path=output_path, title='Total Electricity Consumption', xlabel='Countries',
                                     ylabel="Installed Capacity in ${W_el}$")

                        variable_name = ("PV", "capacity", "[W_el]")
                        output_path = os.path.join(dir_graph, f"{variable_name[0]}_summary.png")
                        plot_summary(dataframe=df, variable_name=variable_name,
                                     output_path=output_path, title='Total Electricity Consumption', xlabel='Countries',
                                     ylabel="Installed Capacity in ${W_el}$")
                    # content = json.load(f)
                    # print(json.dumps(content, indent=2))
                if template_names["SourceSinkTD"] in file:
                    with zip_file.open(file) as f:
                        df = pd.read_json(f, orient='records').T
                        new_index = [literal_eval(index) for index in df.index.values]
                        df.index = pd.MultiIndex.from_tuples(new_index)
                        df = df.T

                        variable_name = "My House"
                        output_path = os.path.join(dir_graph, f"{variable_name}_operation_rate.png")
                        plot_td(dataframe=df, variable_name=variable_name,
                                output_path=output_path, title='Consumption Rate', xlabel='Timestep',
                                ylabel="Electricity Power in ${W}$")

                        variable_name = "PV"
                        output_path = os.path.join(dir_graph, f"{variable_name}_operation_rate.png")
                        plot_td(dataframe=df, variable_name=variable_name,
                                output_path=output_path, title='PV Production Rate', xlabel='Timestep',
                                ylabel="Electricity Power in ${W}$")

                        variable_name = "Wind turbine"
                        output_path = os.path.join(dir_graph, f"{variable_name}_operation_rate.png")
                        plot_td(dataframe=df, variable_name=variable_name,
                                output_path=output_path, title='Wind Production Rate', xlabel='Timestep',
                                ylabel="Electricity Power in ${W}$")
                if template_names["SourceSinkTI"] in file:
                    with zip_file.open(file) as f:
                        df = pd.read_json(f, orient='records')

    if file_path.endswith(".xlsx"):
        # Check the homepage of the dataframe
        # 1. Check if source exists and Check regions
        workbook = openpyxl.load_workbook(filename=file_path)
        sheet_names = workbook.sheetnames
        print('Sheet names: ', *sheet_names, sep='\n\t')

        for sheet_name in sheet_names:
            if sheet_name == template_names["SourceSinkSummary"]:
                variable_name = ("My House", "operation", "[W_el*h/a]")
                output_path = os.path.join(dir_graph, f"{variable_name[0]}_summary.png")
                df = pd.read_excel(file_path, sheet_name=sheet_name, index_col=[0, 1, 2])
                plot_summary(dataframe=df, variable_name=variable_name,
                             output_path=output_path, title='Total Electricity Consumption', xlabel='Countries',
                             ylabel="Electricity in ${W_{el}h}$")
                variable_name = ("Wind turbine", "capacity", "[W_el]")
                output_path = os.path.join(dir_graph, f"{variable_name[0]}_summary.png")
                df = pd.read_excel(file_path, sheet_name=sheet_name, index_col=[0, 1, 2])
                plot_summary(dataframe=df, variable_name=variable_name,
                             output_path=output_path, title='Total Electricity Consumption', xlabel='Countries',
                             ylabel="Installed Capacity in ${W_el}$")
                variable_name = ("PV", "capacity", "[W_el]")
                output_path = os.path.join(dir_graph, f"{variable_name[0]}_summary.png")
                df = pd.read_excel(file_path, sheet_name=sheet_name, index_col=[0, 1, 2])
                plot_summary(dataframe=df, variable_name=variable_name,
                             output_path=output_path, title='Total Electricity Consumption', xlabel='Countries',
                             ylabel="Installed Capacity in ${W_el}$")
            if sheet_name == template_names["SourceSinkTD"]:
                variable_name = "My House"
                output_path = os.path.join(dir_graph, f"{variable_name}.png")
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=[0, 1, 2], skiprows=0)
                plot_td(dataframe=df, variable_name=variable_name,
                        output_path=output_path, title='Consumption Rate', xlabel='Timestep',
                        ylabel="Electricity Power in ${W}$")

                variable_name = "PV"
                output_path = os.path.join(dir_graph, f"{variable_name}.png")
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=[0, 1, 2], skiprows=0)
                plot_td(dataframe=df, variable_name=variable_name,
                        output_path=output_path, title='PV Production Rate', xlabel='Timestep',
                        ylabel="Electricity Power in ${W}$")

                variable_name = "Wind turbine"
                output_path = os.path.join(dir_graph, f"{variable_name}.png")
                plot_td(dataframe=df, variable_name=variable_name,
                        output_path=output_path, title='Wind Production Rate', xlabel='Timestep',
                        ylabel="Electricity Power in ${W}$")

            if sheet_name == template_names["SourceSinkTI"]:
                dataframe = pd.read_excel(file_path, sheet_name=sheet_name, index_col=[0, 1])
                print("*** Only the variable optimum! ***")
            if sheet_name == template_names["TransmissionSummary"]:
                print("*** Transmission Summary here! ***")
            if sheet_name == template_names["TransmissionTD"]:
                print("*** Operation variables optimum for Transmission ***")
            if sheet_name == template_names["TransmissionTI"]:
                print("*** Capacity variables Optimum for Transmission ***")


def plot_td(dataframe: pd.DataFrame, variable_name: str, output_path: str,  title: str, ylabel: str, xlabel: str, show_plot: bool = False):
    DF = dataframe[("operationVariablesOptimum", variable_name)]
    sorted_df = DF[DF.sum().sort_values(ascending=False).index]
    sorted_df.plot(figsize=(12, 5), xlabel=xlabel, ylabel=ylabel, xlim=(0, 8760), title=title)
    if show_plot:
        plt.show()
    plt.savefig(output_path, dpi=200)


def plot_summary(dataframe: pd.DataFrame, variable_name: tuple, output_path: str,  title: str, ylabel: str, xlabel: str, show_plot: bool = False):
    DF = dataframe.loc[variable_name]
    DF.plot.bar(title=title, xlabel=xlabel, ylabel=ylabel, figsize=(10, 6), rot=0)
    if show_plot:
        plt.show()
    plt.savefig(output_path, dpi=200)


if __name__ == '__main__':
    main()


# https://stackoverflow.com/questions/60758625/sort-pandas-dataframe-by-sum-of-columns