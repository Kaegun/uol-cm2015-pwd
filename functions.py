import pandas as pd


def remove_invalid_rows_not_integer(data, column_name):
    # Remove rows where 'Year' column is not a valid integer
    filtered_data = data[
        len(data[column_name].astype(str)) > 0
        and data[column_name].astype(str).str.isdigit()
    ]
    # Convert the 'Year' column to an integer data type
    filtered_data.loc[:, column_name] = filtered_data[column_name].astype(int)
    return filtered_data


def remove_years_before(data, year):
    # Filter rows where the year is greater than or equal to the specified year
    filtered_data = data[data["Year"] >= year]
    return filtered_data


def convert_columns_to_float(data, columns_to_convert=[]):
    # Convert selected columns to float and replace NaN with zero
    for column in columns_to_convert:
        data.loc[:, column] = data[column].astype(float).fillna(0)


def transpose_data(
    input_file,
    rows_to_skip,
    id_columns,
    value_start_column,
    transposed_column_name,
    transposed_value_name="Value",
    columns_to_ignore=[],
):
    # Load your dataset into a pandas DataFrame
    data = pd.read_csv(input_file, skiprows=rows_to_skip)

    # Select only the columns you want to transpose
    data_selected = data.drop(columns=columns_to_ignore)

    # melt the selected data to transpose values per years as rows
    transposed_data = data_selected.melt(
        id_vars=id_columns,
        value_vars=data_selected.columns[value_start_column:],
        var_name=transposed_column_name,
        value_name=transposed_value_name,
    )

    # Remove any non-numeric characters from the 'Year' column
    transposed_data = remove_invalid_rows_not_integer(
        transposed_data, transposed_column_name
    )

    # Convert 'Value' column to float and replace NaN with zero
    convert_columns_to_float(transposed_data, [transposed_value_name])

    # Return the transposed dataset
    return transposed_data


# Define a function to create line graphs for top and bottom countries
def create_line_graph(plt, data, group_by_name, metric_names, top_n=3, bottom_n=3, fig_x=12, fig_y=6):
    plt.figure(figsize=(fig_x, fig_y))

    # Calculate the number of rows and columns needed for subplots
    num_rows = len(metric_names) // 2 + len(metric_names) % 2
    num_cols = 2

    # Create subplots with two plots per row, and adjust figsize for taller plots
    fig, axs = plt.subplots(num_rows, num_cols, figsize=(fig_x, fig_y))

    for idx, metric_name in enumerate(metric_names):
        row = idx // num_cols
        col = idx % num_cols
        
        # Filter top and bottom countries based on the metric
        top_group_by_items = (
            data.groupby(group_by_name)[metric_name]
            .mean()
            .sort_values(ascending=False)
            .head(top_n)
            .index
        )
        bottom_group_by_items = (
            data.groupby(group_by_name)[metric_name]
            .mean()
            .sort_values()
            .head(bottom_n)
            .index
        )

        ax = axs[row, col]

        # Plot line graphs for top countries (generically named 'group_item')
        for group_item in top_group_by_items:
            grouped_data = data[data[group_by_name] == group_item]
            ax.plot(
                grouped_data["Year"], grouped_data[metric_name], label=group_item + " (Top)"
            )

        # Plot line graphs for bottom countries (generically named 'group_item')
        for group_item in bottom_group_by_items:
            grouped_data = data[data[group_by_name] == group_item]
            ax.plot(
                grouped_data["Year"], grouped_data[metric_name], label=group_item + " (Bottom)"
            )

        ax.set_xlabel("Year")
        ax.set_ylabel(metric_name)
        ax.set_title(
            f"{metric_name} Comparison for Top {top_n} and Bottom {bottom_n} {group_by_name}s"
        )

        ax.legend()

    # If there's an odd number of countries, remove the last subplot
    if len(metric_names) % 2 == 1:
        fig.delaxes(axs[num_rows - 1, num_cols - 1])
