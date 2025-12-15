"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    departments = departments.copy()
    regions = regions.copy()
    # Convert codes to strings (keep original for 2A/2B)
    departments["code"] = departments["code"].astype(str)
    departments["region_code"] = departments["region_code"].astype(str)
    regions["code"] = regions["code"].astype(str)
    df = departments.merge(
        regions,
        left_on="region_code",
        right_on="code",
        how="inner"
    )
    return df.rename(
        columns={
            "region_code": "code_reg",
            "name_y": "name_reg",
            "code_x": "code_dep",
            "name_x": "name_dep",
        }
    )[["code_reg", "name_reg", "code_dep", "name_dep"]]
    # return pd.DataFrame({})


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    referendum = referendum.copy()
    # Ensure department codes are strings with leading zeros
    referendum["Department code"] = referendum["Department code"].astype(str).str.zfill(2)

    # Drop DOM-TOM-COM and French abroad (codes containing 'Z')
    referendum = referendum[~referendum["Department code"].str.contains("Z")]

    df = referendum.merge(
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="left"  # all remaining rows should now have a match
    )
    return df

    # return pd.DataFrame({})


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    cols = ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
    result = referendum_and_areas.groupby("code_reg")[cols].sum()
    result["name_reg"] = referendum_and_areas.groupby("code_reg")["name_reg"].first()
    return result[["name_reg"] + cols]

    # return pd.DataFrame({})


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo = gpd.read_file("data/regions.geojson")

    df = geo.merge(
        referendum_result_by_regions.reset_index(),
        left_on="code",  # or whatever your geo column is called
        right_on="code_reg",
        how="left"
    )

    df["ratio"] = (
        df["Choice A"]
        / (df["Choice A"] + df["Choice B"])
    )

    df.plot(
        column="ratio",
        legend=True,
        figsize=(10, 8),
        cmap="RdBu"
    )

    return df

    # return gpd.GeoDataFrame({})


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()

