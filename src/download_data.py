"""Download the two source datasets into data/.

Sources (both published by Our World in Data, CC BY):
  * owid-energy-data.csv - OWID energy dataset, compiled from Ember's
    Electricity Data Explorer and the Energy Institute Statistical Review.
  * owid-co2-data.csv    - OWID CO2 dataset (Global Carbon Project et al.).
Run once before src/analysis.py.
"""
import urllib.request

FILES = {
    "data/owid-energy-data.csv":
        "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv",
    "data/owid-co2-data.csv":
        "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv",
}

for path, url in FILES.items():
    print(f"downloading {url} -> {path}")
    urllib.request.urlretrieve(url, path)
print("done")
