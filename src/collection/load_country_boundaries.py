import geopandas as gpd
import matplotlib.pyplot as plt

file_path = "data/raw/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"

countries = gpd.read_file(file_path)

print(countries.head())
print(countries.crs)
print(countries.shape)

countries.plot()
plt.show()