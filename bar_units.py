import csv
import sys
from src import github, db, output

default = (
  [["armorcore", "is", True]],
  [
      "id", "name"
  ]
)

site = (
    [["armorcore", "is", True]],
    [
        "id", "name", "faction", "categories",
        "buildoptions", "buildcostmetal", "buildcostenergy", "energymake", "metalmake", "buildtime",
        "dps", "range", "dps_per_metal", "speed", "health",
        "radardistance", "height"
    ]
)

metalmake = (
    [
      ["armorcore", "is", True],
      ["energymake", ">", 5],
      ["type", "is", "building"]
    ],
    [
        "id", "name", "faction", "buildcostmetal", "buildcostenergy", "energymake"
    ]
)

"""
Example filters
All T2 tanks
filters = [
  ["type", "is", "tank"],
  ["techlevel", "is", 2],
  ["dps1", ">", 0]
] + default_filters,

Two specific tanks
filters = [
  ["name", "in", ["Bulldog", "Reaper"]],
],

# All T1 arm bots
filters = [
  ["type", "is", "bot"],
  ["techlevel", "is", 1],
  ["arm", "is", True],
] + default_filters,
"""

def main(filters, selection):
  github._check_rate_limit()
  github.get_all_unit_files()

  output.write(
    filters = filters,
    select = selection
  )

if __name__ == '__main__':
  if len(sys.argv) == 1:
    filters, selection = default
    # TODO: separate these from stuff that simulator actually needs
    filters += [
      # ["type", "in", ["bot", "tank"]],
      # ["type", "in", ["bot", "tank", "ship"]],
      # ["name", "in", ["corak", "armfido"]],
      # ["name", "in", ["armthor", "armbanth"]],
      # ["name", "not in", ["mando", "gremlin", "decom"]],  # TODO: arm/cor
      ["dps1", ">", 0],
      # ["techlevel", "in", [1, 2]],
      ["techlevel", "is", 2]
      # ["arm", "is", True],
    ]
    selection = ["name", "type", "techlevel", "buildcostmetal", "buildcostenergy", "health", "maxvelocity",
                 "collisionvolumescales", "all_weapons"]
  elif len(sys.argv) == 2:
    fname = sys.argv[1]
    if fname == "site":
      filters, selection = site
    elif fname == "metalmake":
      filters, selection = metalmake
    else:
      filters, selection = default
  
  main(filters, selection)

  # "id", "buildtime", "sightdistance", "dps", "range", "dps_per_metal", "health_per_metal",
  # "maxwaterdepth", (see vist pole igal asjal olemas)
