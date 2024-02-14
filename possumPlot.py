import geopandas as gpd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geodatasets as gds 
import os
from matplotlib.lines import Line2D

def initialize() -> None:
    '''
    Initializes the opossum shapefile by separating the MDD GeoPackage into 
    individual genus files instead. If the files and folder already exist,
    it does nothing
    Parameters:
        None
    Returns:
        None, writes files
    Raises:
        ValueError if the MDD file is missing
    '''
    if not os.path.isdir("Opossum_Shapes"):
        os.mkdir("Opossum_Shapes")

    if not os.path.isdir("Figs"):
        os.mkdir("Figs")
    
    if not os.path.exists("Opossum_Shapes/Didelphis.gpkg"):
        try:
            possums = gpd.read_file("MDD_Didelphimorphia.gpkg")
        except:
            raise ValueError("You need the Mammal Diversity Database GeoPackage for this program. Download the Didelphimorphia Geopackage at https://zenodo.org/records/6644198")
        possums["genus"] = possums.sciname.str.extract(r'\b(\w*)', expand = True) 
        possums["species"] = possums.sciname.str.extract(r'\b(\w+)$', expand = True) 

        new_cols = ["sciname", "genus", "species", "order", "family", "author", "year", "citation", "rec_sourse", "geometry"]
        possums = possums.reindex(columns = new_cols)

        genera = possums.genus.unique()

        for genus in genera:
            species = possums[possums["genus"].isin([genus])]
            species.to_file(f"Opossum_Shapes/{genus}.gpkg", driver = "GPKG")

        print("Initialization Complete: you can delete MDD_Didelphimorphia.gpkg now")

def plotGenera():
    '''
    Plots the distribution of an entire genus, without showing the boundaries between 
    species members. If multiple genera are given, it has each genus be a different
    color and their overlap is hatched  
    '''

def plotGeneraMembers():
    '''  
    '''   

def plotSpecies(species: list[str], land: "GeoDataFrame", filename: str) -> None:
    '''
    Plots the distribution of the species given  
    Parameters:
        species:  a list of strings of the species scientific names (genus species)
        land:     the GeoDataFrame for the land polygon
        filename: the name the plot should be saved as
    '''
    #only works for 2 species rn
    if len(species) > 2:
        return None

    genera = []
    for i in species:
        genus = i.split()[0]
        if genus not in genera:
            genera.append(genus)
    
    for i in range(len(genera)):
        genera[i] = gpd.read_file(F"Opossum_Shapes/{genera[i]}.gpkg")

    #[i]['genus'].iloc[0]
    for i in range(len(species)):
        for n in range(len(genera)):
            if species[i] in genera[n].loc[:, "sciname"].tolist():
                species[i] = genera[n].loc[genera[n]["sciname"] == species[i]]
                break

    #use the area of the geometry to determine the layering for the plots: bigger area on bottom
    #maybe set it up so the area is set up during the initialization so it only has to be done once?

    #use "none" as fill color for the ones on top
    #need to keep track of how many intersections there are and for which ones they intersect with
    #use intersects() to see which intersect
    #for a separate func tho

    print("plotting")

    fig, ax = plt.subplots(figsize=(10,10))
    plt.rcParams['hatch.linewidth'] = 4

    land.plot(ax=ax, color='gray', edgecolor='black', alpha=0.5)

    colors = ["green", "blue"]

    intersec = species[0].overlay(species[1], how = "intersection")

    species[0] = species[0].overlay(species[1], how = "difference")
    label_1    = species[0].iloc[0]["sciname"]
    species[0].plot(ax=ax, linewidth = 0, color = colors[0], alpha = 1, label = label_1)

    species[1] = species[1].overlay(species[0], how = "difference")
    label_2    = species[1].iloc[0]["sciname"]
    species[1].plot(ax=ax, linewidth = 0, color = colors[1], alpha = 1, label = label_2)

    if species[0].to_crs(3857).area.sum() > species[1].to_crs(3857).area.sum():
        intersec.plot(ax=ax, linewidth = 0, color = "none", edgecolor = colors[1], hatch = "//", alpha=1)
    else:
        intersec.plot(ax=ax, linewidth = 0, color = "none", edgecolor = colors[0], hatch = "//", alpha=1)

    labels = [label_1, label_2]
    legend_elements = []
    for i in range(len(labels)):
        legend_elements.append(Line2D([0], [0], marker='o', color='w', label=labels[i],markerfacecolor=colors[i], markersize=15))

    ax.legend(handles=legend_elements)

    plt.tight_layout()

    plt.savefig(f"Figs/{filename}")



def main():
    initialize()

    land_path = gds.get_path("naturalearthland")
    land = gpd.read_file(land_path)
    land = land.cx[-130:-60, 5:55]

    species = ["Didelphis virginiana", "Didelphis marsupialis"]
    plotSpecies(species, land, "plotSpeciesTest.png")

if __name__ == "__main__":
    main()