from dataclasses import dataclass

# TODO: note to self: this has too many problems and other stuff to simulate simply (most notably aoe and rocket attacks and accuracy)


units = []
EXPLOSION_AOE = 1000 # 70
MIN_UNITS = 3
MAX_TIME = 30

@dataclass
class Unit:
  name: str
  type: str
  level: int
  metal: int
  energy: int
  health: int
  maxvelocity: int  # already multiplied with 30
  size: float
  weapons = None  # list of weapons
  won = 0
  lost = 0

  def __init__(self, name, typ, level, metal, energy, health, maxvelocity, cvs):
    self.name = name
    self.type = typ
    self.level = round(float(level))
    self.metal = round(float(metal))
    self.energy = round(float(energy))
    self.health = round(float(health))
    self.maxvelocity = 0 if maxvelocity is None else round(float(maxvelocity) * 30)
    self.size = 0 if cvs is "" else sum([float(x)/3 for x in cvs.split(" ")])

    if name == "com":
      # 3.8 to make it more-or-less equal to 14 pw
      self.metal /= 3.8
      self.energy /= 3.8


@dataclass
class Weapon:
  name: str
  type: str
  range: int
  aoe: int
  damage: float
  reload: float

  def __init__(self, name, type, range, aoe, damage, reload, burst=1):
    self.name = name
    self.type = type
    self.range = round(float(range))
    self.aoe = round(float(aoe))
    self.damage = float(damage) * burst
    self.reload = float(reload)


@dataclass
class Fighter:
 def __init__(self, u: Unit):
   self.unit = u
   self.hp = u.health
   self.cd = []
   self.offset_x = 0
   self.offset_y = 0
   for _ in u.weapons:
     self.cd.append(0)


def find_fight_mode(u1, u2):
  distance = -1
  u1_max_range = 1
  u2_max_range = 0
  for w in u1.weapons:
    if distance < w.range:
      distance = w.range
  for w in u2.weapons:
    if distance == w.range:
      u2_max_range = 1
    elif distance < w.range:
      distance = w.range
      u2_max_range = 1
      u1_max_range = 0
  mode = u1_max_range - u2_max_range
  return distance, mode


def balance(u1, u2, diff):
  side1 = [Fighter(u1)]
  side2 = [Fighter(u2)]
  for i in range(100):
    if len(side1) * u1.metal * (1 - diff) < len(side2) * u2.metal < len(side1) * u1.metal * (1 + diff) and len(
        side1) >= MIN_UNITS and len(side2) >= MIN_UNITS:
      break
    if len(side1) * u1.metal < len(side2) * u2.metal:
      side1.append(Fighter(u1))
    else:
      side2.append(Fighter(u2))
  # create_formation(side1)
  # create_formation(side2, tight=True)
  return side1, side2


def attack(f1: Fighter, defender_side, distance, num1, num2, debug=False):
  # All weapons shoot at this guy, even if dead, because shots generally have flying time
  for i in range(len(f1.unit.weapons)):
    if f1.unit.weapons[i].type == "LightningCannon":
      shoot_lightning(f1, defender_side, distance, i, num1, num2)
    elif f1.unit.weapons[i].aoe > EXPLOSION_AOE:
      shoot_aoe(f1, defender_side, distance, i, num1, num2)
    else:
      shoot(f1, defender_side[-1], distance, i, num1, num2)


def shoot(f1, f2, distance, i, num1, num2, debug=False, half_damage=False):
  if distance <= f1.unit.weapons[i].range:
    if f1.cd[i] <= 0:
      f1.cd[i] += f1.unit.weapons[i].reload
      if half_damage:
        f2.hp -= f1.unit.weapons[i].damage/2
      else:
        f2.hp -= f1.unit.weapons[i].damage
      if debug:
        print(f1.unit.name, num1, "shoots", f2.unit.name, num2, "with", f1.unit.weapons[i].name, "for",
              f1.unit.weapons[i].damage, "at", distance, "hp=" + str(f2.hp))


def shoot_lightning(shooter: Fighter, defender_side, distance, i, num1, num2):
  shoot(shooter, defender_side[-1], distance, i, num1, num2)
  if len(defender_side) > 1:
    shoot(shooter, defender_side[-2], distance, i, num1, num2, half_damage=True)
  if len(defender_side) > 2:
    shoot(shooter, defender_side[-3], distance, i, num1, num2, half_damage=True)



def shoot_aoe(shooter: Fighter, defender_side, distance, i, num1, num2):
  shoot(shooter, defender_side[-1], distance, i, num1, num2)  # TODO: change to actual aoe calculation with extra targets


# TODO: find out which units cannot reverse and shoot.

# FIXME: emp weapons do not do actual damage. how to remove them?

def shoot_all(distance, shooter_side, defender_side):
  for i in range(len(shooter_side)):
    attack(shooter_side[i], defender_side, distance, i, len(defender_side) - 1)
    if defender_side[-1].hp <= 0:
      defender_side.pop()
    if len(defender_side) == 0:
      return True
  return False


def fight(u1: Unit, u2: Unit):
  distance, mode = find_fight_mode(u1, u2)
  max_distance = distance
  # if mode == 0, then they have equal range and will walk towards eachother
  # if mode > 0, then side1 will try to run away
  # if mode < 0, then side2 will try to run away

  # balance approx metal cost of unit batches
  diff = 0.1
  # TODO: bigger battles where both sides have N before balance
  side1, side2 = balance(u1, u2, diff)
  max_num1 = len(side1)
  max_num2 = len(side2)
  max_hp1 = max_num1 * u1.health
  max_hp2 = max_num2 * u2.health
  # print("-"*30)
  # print(max_num1, u1.name, "fighting", max_num2, u2.name, round(max_num1 * u1.metal / (max_num2 * u2.metal), 2),
  #       "mode", mode)


  tick = 1 / 30
  # counter = 0
  time = 0
  while len(side1) > 0 and len(side2) > 0:
    # side1 has definite advantage, double experiments are necessary
    if (shoot_all(distance, side1, side2)):
      health = sum([f.hp for f in side1])
      print(max_num1, u1.name, "won", max_num2, u2.name, "in", round(time, 1), "s (" + str(round(health/max_hp1*100)) + " % hp)")
      u1.won += 1
      u2.lost += 1
      break
    if (shoot_all(distance, side2, side1)):
      health = sum([f.hp for f in side2])
      print(max_num2, u2.name, "won", max_num1, u1.name, "in", round(time, 1), "s (" + str(round(health/max_hp2*100)) + " % hp)")
      u1.lost += 1
      u2.won += 1
      break
    time += tick
    if distance <= 0:
      distance = 0
      pass
    elif mode == 0 or distance > max_distance:
      distance += -u1.maxvelocity * tick - u2.maxvelocity * tick
    elif mode > 0:
      distance += u1.maxvelocity * tick - u2.maxvelocity * tick
    elif mode < 0:
      distance += -u1.maxvelocity * tick + u2.maxvelocity * tick
    else:
      print("RESISTANCE IS FUTILE!")
    for f in side1 + side2:
      for i in range(len(f.cd)):
        if f.cd[i] >= tick:
          f.cd[i] -= tick
        else:
          f.cd[i] = 0

    # counter += 1
    # if counter == 29:
    #   health1 = sum([f.hp for f in side1])
    #   health2 = sum([f.hp for f in side2])
    #   # print([round(c, 1) for c in side1[0].cd])
    #   print(len(side1), "vs", len(side2), "  d =", round(distance, 1), "  time = ", round(time, 1)), "s (" + str(
    #     round(health1 / max_hp1 * 100)) + " %, " + str(round(health2 / max_hp2 * 100)) + " % hp)"
    #   counter = 0
    if time > MAX_TIME:
      mode = 0
      # health1 = sum([f.hp for f in side1])
      # health2 = sum([f.hp for f in side2])
      # print(max_num1, u1.name, "draw", max_num2, u2.name, "in", round(time, 1),
      #       "s (" + str(round(health1 / max_hp1 * 100)) + " %, " + str(round(health2 / max_hp2 * 100)) + " % hp)")
      # break


def create_formation(fighters: Fighter, tight=True):
  print("\n\ncreating " + ("tight " if tight else "") + "formation for", fighters[0].unit.name)
  shortest_weapon_range = 10000
  for w in fighters[0].unit.weapons:
    if shortest_weapon_range > w.range:
      shortest_weapon_range = w.range
  # formation size (quite arbitrarily) = 2 * range / (n - 1) - unit_size1
  offset = fighters[0].unit.size
  print("offset tight = ", offset)
  if not tight:
    offset = offset*2
    print("offset = ", offset)
  if not tight and 2 * shortest_weapon_range / (fighters.size() - 1) - fighters[0].unit.size > 0:
    offset = 2 * shortest_weapon_range / (fighters.size() - 1)
    print("offset sparse = ", offset)  # TODO: see vist ei tööta õigesti? Mõte oli selles, et kui on liiga vähe rahvast, siis nad on väga hõredalt
  x = 0
  y = -shortest_weapon_range
  for f in fighters:
    f.offset_x = x
    f.offset_y = y
    y += offset
    if y > shortest_weapon_range:
      y = -shortest_weapon_range
      x += offset
    print(f.offset_x, f.offset_y)



# TODO: scenarios:
#  micro (olemas) (põgeneb kui 1 relv on in range, vb 2. katse, kus põgeneb kui kõik relvad on in range, parim tulemus jätta. Aga kui mõlemal mitu?)
#  assault (mõlemad liiguvad üksteisele lähemale)
#  defence (1 pool seisab paigal)
#  combo: 30 sec micro -> defence (lõpmatuseni)
# TODO:
#  give a % of shots hit, based on speed and range somehow?
#  how to deal with switchable weapons? (fido has exception, others?)
# TODO:
#  fire pattern: kas kahur peaks tulistama otsest järjest või kesekelt või suvalt?

# TODO: aoe (lightning is in?)
# TODO: emp weapons to be removed somehow


# Speed test results
#  rocko walks to target about 8.5s, hammer 7.0, flea 0.7, but might get significant error due to target size
#  shellshocker and samson 13s, which is quite accurate (better measurements?)
#  how to deal with aoe damage? should just hit 2 units normally. Or if there is a low shot, then maybe miss some

# hammer
# collisionvolumescales = "29 28 29",
# weapon
# areaofeffect = 36,
# turret = true,
# Arvan, et on umbes samas suurusühikus.
# Iseenesest võiks olla umbes nii, et kui on vähem kui 10 tegelast reas, siis on iga tegelase vahel 1 tegelase jagu
# tühja ruumi, kui 10+, siis on kõik kõrvuti. Või siis on nii, et nad on reas vastavalt sellele, kui suur on nende
# laskmisulatus, kui range on 300 ja suurus on 30, siis nad on
# 2*range / (n-1) - size
# 2 -> 570
# 10 -> 37
# 21 -> 0
# 22+ ei saagi olla (st need on teises reas ja nende range on size võrra suurem). Nii peab hakkama 2d asukohta jälgima.
# ugh. teen 1.5D, ainult kaugus ja rida

# lisaks võib teha cost arvutusse selle lisa, et kui on vaja ka tehaseid ehitada (andmed g drives)
