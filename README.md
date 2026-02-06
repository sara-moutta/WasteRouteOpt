# WasteRouteOpt
A sector-based vehicle routing optimization framework for municipal solid waste collection designed to reduce computational costs while preserving operational efficiency.

# Input Data Structure

The dataset is organized into multiple CSV files, each representing a service sector obtained from the spatial partitioning framework.

Each CSV contains:

Customer coordinates (xFeet, yFeet)

Demand values per collection point

The algorithm processes each sector independently and aggregates the results to obtain the global routing solution.

A complete dataset corresponding to the entire service region is also provided for comparative analysis.
