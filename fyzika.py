import math
import pygame
import config


def nastav_kolo(typ):
    if typ == "0" or typ == 0:
        config.SUS_FRONT, config.SUS_REAR = 0.5, 0.5
        config.DAMP_FRONT, config.DAMP_REAR = 0.95, 0.95
    elif typ == "1" or typ == 1:
        config.SUS_FRONT, config.SUS_REAR = 0.12, 0.5
        config.DAMP_FRONT, config.DAMP_REAR = 0.5, 0.9
    elif typ == "2" or typ == 2:
        config.SUS_FRONT, config.SUS_REAR = 0.12, 0.12
        config.DAMP_FRONT, config.DAMP_REAR = -0.4, -0.4

cache_hodnot0 = {}
cache_hodnot1 = {}
cache_hodnot2 = {}
cache_hodnot3 = {}

def generace_bod(x):
  mapa = config.vybrana_mapa 
  if mapa == 1:
      if x in cache_hodnot1:
            return cache_hodnot1[x]
      i = x / config.krok
      obtiznost = 1 + (x / config.obtiznost_mapy)
      y = (
          math.sin(i * 0.002) * (200 * obtiznost)   
          + math.sin(i * 0.05 + math.cos(i * 0.01)) * (50 * obtiznost)  
          + math.sin(i * 0.25 + math.cos(i * 0.03)) * (4 + obtiznost) 
          + math.sin(i * 0.015) * 20 
          + math.cos(i * 0.2) * 10     
      )
      cache_hodnot1[x] = y
      return y
  elif mapa == 2:
        if x in cache_hodnot2:
            return cache_hodnot2[x]
        i = x / config.krok
        obtiznost = 1 + (x / config.obtiznost_mapy)
        y = (
            math.sin(i * 0.002) * (1000 * obtiznost)   
            + math.sin(i * 0.05) * (50 * obtiznost)  
            + math.sin(i * 0.25) * (4 + obtiznost) 
            + math.sin(i * 0.015) * 20 
            + math.cos(i * 0.2) * 10 
        )
        cache_hodnot2[x] = y
        return y
  
  elif mapa == 3:
        if x in cache_hodnot3:
            return cache_hodnot3[x]
        i = x / config.krok
        obtiznost = 1 + (x / config.obtiznost_mapy)
        y = (
            math.sin(i * 0.012) * (400 * obtiznost)    
            + math.sin(i * 0.07) * (150 * obtiznost)   
                  
        )
        cache_hodnot3[x] = y
        return y

  else:
    if x in cache_hodnot0:
      return cache_hodnot0[x]
    i = x / config.krok
    obtiznost = 1 + (x / config.obtiznost_mapy)
    y = (math.sin(i * 0.004) * (120 * obtiznost)
          + math.sin(i * 0.025 + math.cos(i * 0.002)) * (60 * obtiznost)
          + math.sin(i * 0.13 + math.cos(i * 0.03)) * (18 + obtiznost * 5)
          + math.sin(i * 0.0025)
          + math.cos(i * 0.7) * 2
    )
    cache_hodnot0[x] = y
    return y

class Vector:
  def __init__(self, x, y):
    self.x = x
    self.y = y
  
  def __add__(self, other):
    return Vector(self.x + other.x, self.y + other.y)
  
  def __sub__(self, other):
    return Vector(self.x - other.x, self.y - other.y)
  
  def __mul__(self, other):
    return Vector(self.x * other, self.y * other)
  
  def __truediv__(self, other):
    return Vector(self.x / other, self.y / other)

  def normalized(self):
    length = math.sqrt(self.x * self.x + self.y * self.y)
    return Vector(self.x / length, self.y / length)
  
  def perpendicular(self):
    if self.x == 0:
      return Vector(0, 1)
    return Vector(self.y, -self.x).normalized()
  
  def distance_to(self, other):
    return math.sqrt((self.x - other.x) * (self.x - other.x) + (self.y - other.y) * (self.y - other.y))
  
  def dot(self, other):
    return self.x * other.x + self.y * other.y

  def __str__(self):
    return f"({self.x}, {self.y})"

def lerp(a, b, t):
  return a * (1 - t) + b * t

def closest_point_on_line(a: Vector, b: Vector, p: Vector) -> Vector:
    ab = b - a
    ap = p - a
    t = ap.dot(ab) / ab.dot(ab)
    return a + (ab * t)

class VerletEntity:
  def __init__(self, position):
    self.position = position
    self.last_position = position
  
  def apply_gravity(self, gravity):
    self.position += gravity
  
  def set_speed(self, velocity):
    self.last_position = self.position - velocity
  
  def get_speed(self):
    return self.position - self.last_position
  
  def tick(self):
    dp = self.position - self.last_position 
    self.last_position = self.position
    self.position += dp

  def damp_speed(self, k):
    self.set_speed(self.get_speed() * k)

  def set_position(self, position):
    self.position = position 

  def get_position(self):
    return self.position
  
  def apply_force(self, force):
    self.position += force
  
  def move_by(self, delta_position):
    self.position += delta_position
    self.last_position += delta_position
  
  def move_to(self, position):
    delta_position = position - self.position
    self.move_by(delta_position)

  def damp_relative_speed(self, other, k):
    #k (float): damping factor (e.g. 0.9 keeps 90% of relative speed)

    v1 = self.get_speed()
    v2 = other.get_speed()
    delta_pos = self.position - other.position

    if delta_pos.x == 0 and delta_pos.y == 0:
        return
    dir_norm = delta_pos.normalized()

    rel_speed = (v1 - v2).dot(dir_norm)

    damp_amount = rel_speed * (1 - k)

    dv = dir_norm * damp_amount

    self.set_speed(v1 - dv * 0.5)
    other.set_speed(v2 + dv * 0.5)

def wheel_collision_check(ventity, radius):
  closest_distance = radius
  closest_point = None
  step = radius * 2 / (config.WHEEL_COLLISION_CHECK_SUBDIVISIONS - 1)
  for i in range(config.WHEEL_COLLISION_CHECK_SUBDIVISIONS):
    point = Vector(ventity.position.x - radius + i * step, generace_bod(ventity.position.x - radius + i * step))
    if point.distance_to(ventity.position) < closest_distance:
      closest_distance = point.distance_to(ventity.position)
      closest_point = point 
  
  return closest_point

class Bike:
  def __init__(self, position):
    self.rear_axel = VerletEntity(position)
    self.front_axel = VerletEntity(position + Vector(config.BIKE_LENGTH, 0))

    self.rear_wheel = VerletEntity(position)
    self.front_wheel = VerletEntity(position + Vector(config.BIKE_LENGTH, 0))
    
    self.animace_index = 0
    self.rychlost_animace = 0.5
    self.energie = 100

    self.celkova_rotace = 0.0
    self.posledni_uhel = None
    self.udelal_frontflip = False
    self.udelal_backflip = False
    self.pocet_backflipu = 0
    self.backflip_cas = 0
    self.pocet_frontflipu = 0
    self.frontflip_cas = 0
    self.zobrazeni_textu = ""
    self.text_cas = 0

  def copy_state_from(self, other):
        self.rear_axel.position = Vector(other.rear_axel.position.x, other.rear_axel.position.y)
        self.rear_axel.last_position = Vector(other.rear_axel.last_position.x, other.rear_axel.last_position.y)
        self.front_axel.position = Vector(other.front_axel.position.x, other.front_axel.position.y)
        self.front_axel.last_position = Vector(other.front_axel.last_position.x, other.front_axel.last_position.y)
        self.rear_wheel.position = Vector(other.rear_wheel.position.x, other.rear_wheel.position.y)
        self.rear_wheel.last_position = Vector(other.rear_wheel.last_position.x, other.rear_wheel.last_position.y)
        self.front_wheel.position = Vector(other.front_wheel.position.x, other.front_wheel.position.y)
        self.front_wheel.last_position = Vector(other.front_wheel.last_position.x, other.front_wheel.last_position.y)
        self.animace_index = other.animace_index
        self.rychlost_animace = other.rychlost_animace
        self.energie = other.energie

  def interpolate(self, other, alpha):
      interp = Bike(Vector(0, 0))
      interp.rear_axel.position = self.rear_axel.position * (1 - alpha) + other.rear_axel.position * alpha
      interp.front_axel.position = self.front_axel.position * (1 - alpha) + other.front_axel.position * alpha
      interp.rear_wheel.position = self.rear_wheel.position * (1 - alpha) + other.rear_wheel.position * alpha
      interp.front_wheel.position = self.front_wheel.position * (1 - alpha) + other.front_wheel.position * alpha
      interp.animace_index = self.animace_index * (1 - alpha) + other.animace_index * alpha
      interp.rychlost_animace = self.rychlost_animace
      interp.energie = self.energie * (1 - alpha) + other.energie * alpha
      return interp

  def tick(self, pressed_keys):
        predni_touch = False
        zadni_touch = False

        self.rear_axel.apply_gravity(Vector(*config.GRAVITY))
        self.front_axel.apply_gravity(Vector(*config.GRAVITY))
        self.rear_wheel.apply_gravity(Vector(*config.GRAVITY))
        self.front_wheel.apply_gravity(Vector(*config.GRAVITY))

        # suspension
        # rear wheel
        sus_force = (self.rear_axel.position - self.rear_wheel.position) * config.SUS_REAR
        self.rear_wheel.apply_force(sus_force)
        self.rear_axel.apply_force(sus_force * -1)
        self.rear_wheel.damp_relative_speed(self.rear_axel, config.DAMP_REAR)

        # front wheel
        sus_force = (self.front_axel.position - self.front_wheel.position) * config.SUS_FRONT
        self.front_wheel.apply_force(sus_force)
        self.front_axel.apply_force(sus_force * -1)
        self.front_wheel.damp_relative_speed(self.front_axel, config.DAMP_FRONT)

        # bike frame
        midpoint = (self.rear_axel.position + self.front_axel.position) / 2
        scaling_cof = config.BIKE_LENGTH / self.rear_axel.position.distance_to(self.front_axel.position)

        self.rear_axel.set_position(midpoint + (self.rear_axel.get_position() - midpoint) * scaling_cof)
        self.front_axel.set_position(midpoint + (self.front_axel.get_position() - midpoint) * scaling_cof)

        # collision check
        # rear wheel
        touch_point = wheel_collision_check(self.rear_wheel, config.WHEEL_RADIUS)
        if touch_point is not None:
            zadni_touch = True
            new_position = self.rear_wheel.get_position() + (self.rear_wheel.get_position() - touch_point).normalized() * (config.WHEEL_RADIUS - self.rear_wheel.get_position().distance_to(touch_point))
            self.rear_wheel.set_position(new_position)
            if self.energie > 0:
                if pressed_keys[pygame.K_a]:
                    self.animace_index -= self.rychlost_animace
                    if self.animace_index < 0:
                        self.animace_index = 12
                    self.rear_wheel.apply_force((self.rear_axel.position - self.front_axel.position).normalized() * config.SLAPANI_FROCE)
                if pressed_keys[pygame.K_d]:
                    self.animace_index += self.rychlost_animace
                    if self.animace_index >= 13:
                        self.animace_index = 0
                    self.rear_wheel.apply_force((self.front_axel.position - self.rear_axel.position).normalized() * config.SLAPANI_FROCE)

        if pressed_keys[pygame.K_a]:
            if self.energie > 0:
                self.animace_index -= self.rychlost_animace
                if self.animace_index < 0:
                    self.animace_index = 12
            self.front_axel.apply_force((self.rear_axel.position - self.front_axel.position).normalized().perpendicular() * config.INAIR_FORCE)
            self.rear_axel.apply_force((self.rear_axel.position - self.front_axel.position).normalized().perpendicular() * -config.INAIR_FORCE)
        if pressed_keys[pygame.K_d]:
            if self.energie > 0:
                self.animace_index += self.rychlost_animace
                if self.animace_index >= 13:
                    self.animace_index = 0
            self.front_axel.apply_force((self.rear_axel.position - self.front_axel.position).normalized().perpendicular() * -config.INAIR_FORCE)
            self.rear_axel.apply_force((self.rear_axel.position - self.front_axel.position).normalized().perpendicular() * config.INAIR_FORCE)

        # front wheel
        touch_point = wheel_collision_check(self.front_wheel, config.WHEEL_RADIUS)
        if touch_point is not None:
            predni_touch = True
            new_position = self.front_wheel.get_position() + (self.front_wheel.get_position() - touch_point).normalized() * (config.WHEEL_RADIUS - self.front_wheel.get_position().distance_to(touch_point))
            self.front_wheel.set_position(new_position)

        # rear wheel
        closest_point = closest_point_on_line(self.rear_axel.get_position(), self.rear_axel.get_position() + (self.rear_axel.get_position() - self.rear_axel.get_position()).perpendicular(), self.rear_wheel.get_position())
        midpoint = (closest_point + self.rear_wheel.get_position()) / 2
        self.rear_axel.move_by(midpoint - closest_point)
        self.rear_wheel.move_to(midpoint)

        closest_point = closest_point_on_line(self.front_axel.get_position(), self.front_axel.get_position() + (self.front_axel.get_position() - self.front_axel.get_position()).perpendicular(), self.front_wheel.get_position())
        midpoint = (closest_point + self.front_wheel.get_position()) / 2
        self.front_axel.move_by(midpoint - closest_point)
        self.front_wheel.move_to(midpoint)

        self.rear_axel.tick()
        self.front_axel.tick()
        self.rear_wheel.tick()
        self.front_wheel.tick()


        delta = self.front_axel.get_position() - self.rear_axel.get_position()
        uhel = math.atan2(delta.y, delta.x) # radiany

        if self.posledni_uhel is not None:
            uhel_rozdil = uhel - self.posledni_uhel

            if uhel_rozdil > math.pi:
                uhel_rozdil -= 2 * math.pi
            elif uhel_rozdil < -math.pi:
                uhel_rozdil += 2 * math.pi

            if not zadni_touch and not predni_touch:
                self.celkova_rotace += uhel_rozdil
                if self.celkova_rotace > 1.5 * math.pi:
                    self.udelal_frontflip = True
                    self.celkova_rotace = 0 
                elif self.celkova_rotace < -1.5 * math.pi:
                    self.udelal_backflip = True
                    self.celkova_rotace = 0  
            else:
                self.celkova_rotace = 0

        self.posledni_uhel = uhel

        return zadni_touch, predni_touch