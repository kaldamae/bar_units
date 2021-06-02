import csv
from src import db

from src.simulator import units, Unit, Weapon, fight, EXPLOSION_AOE

filename = "units.csv"
default_fields = ["id", "name", "buildcostenergy", "buildcostmetal", "buildtime", "weapondefs"]


def write(**kwargs):
  query_args = {
    "filters": kwargs.get("filters", []),
  }
  fields = kwargs.get("select", default_fields)

  all_weapons = False
  if "all_weapons" in fields:
    fields.remove("all_weapons")
    all_weapons = True

  with open(filename, 'w', encoding="utf8") as f:
    writer = csv.writer(f)
    if all_weapons:
      writer.writerow(fields + ["weapon1", "type", "range", "aoe", "damage", "reload",
                                "weapon2", "type", "range", "aoe", "damage", "reload",
                                "weapon3", "type", "range", "aoe", "damage", "reload"])
    else:
      writer.writerow(fields)

    for (key, row) in db.query(**query_args):
      row = convert_to_list(row, fields, all_weapons)
      writer.writerow(row)

  for u in units:
    for o in units:
      if o is u:
        break
      fight(u, o)
      # print("-"*60)
  result = sorted([(round(u.won / (u.won + u.lost)*100) if u.won > 0 or u.lost > 0 else 50, u.name) for u in
                   units])  # all draw isn't well distinguished
  for u in result:
    print(u[0], "%", u[1])
    # # print(u)
    # if u.name == "amph" or u.health == 1050:
    #   print(u)
    #   for w in u.weapons:
    #     print(w)

  print(f"Results output to {filename}")


def convert_to_list(row, output_fields, all_weapons):
  output = [row.get(k, "") if type(row.get(k, "")) is not float else "{:.1f}".format(row[k]) for k in output_fields]
  print(output)
  unit = Unit(*output)
  unit.weapons = []

  if all_weapons:
    for k, v in row.get("weapondefs", {}).items():
      # Filter out some weapons which do not abide by normal rules
      if k not in ["repulsor1", "disintegrator"] and "default" in v["damage"] \
          and v.get("explosiongenerator", "") != "custom:antinuke" and not v.get("paralyzer", False):
        output += [k, v["weapontype"], v["range"], v.get("areaofeffect", ""), v["damage"]["default"],
                   v.get("reloadtime", "")]
        unit.weapons.append(
          Weapon(k, v["weapontype"], v["range"], v.get("areaofeffect", 0), v["damage"]["default"], v["reloadtime"],
                 v.get("burst", 1)))

  if len(unit.weapons) > 0:
    # exceptions
    if unit.name == "fido":
      u1 = Unit(*[row[k] if type(row[k]) is str or type(row[k]) is bool else "{:.1f}".format(row[k]) for k in output_fields]
)
      u1.weapons = [unit.weapons[0]]
      u2 = Unit(*[row[k] if type(row[k]) is str or type(row[k]) is bool else "{:.1f}".format(row[k]) for k in output_fields])
      u2.weapons = [unit.weapons[1]]
      if u2.weapons[0].name == "gauss":
        u2.name = "fidogauss"
      else:
        u1.name = "fidogauss"
      add_units_with_exceptions(u1)
      add_units_with_exceptions(u2)
    else:
      add_units_with_exceptions(unit)
  return output


def add_units_with_exceptions(unit):
  if min([w.aoe for w in unit.weapons]) > EXPLOSION_AOE:
    # dont' add artillery units (for now) # FIXME: remove or add or smth
    return
  # print(unit.name, "aoe=", [w.aoe for w in unit.weapons], "min=", min([w.aoe for w in unit.weapons]))
  units.append(unit)
