# Ondrejek potahal

import math
import pygame
# Konstanty

BIKE_LENGTH = 120
WHEEL_RADIUS = 40
SUS_REAR = 0.15
SUS_FRONT = 0.15
DAMP_FRONT = 0.99
DAMP_REAR = 0.99
SLAPANI_FROCE = 1
INAIR_FORCE = 0.2
WHEEL_COLLISION_CHECK_SUBDIVISIONS = 50
GRAVITY = None

krok = None
obtiznost_mapy = None
obrazovka_vyska = None


def generace_bod(x):
    i = x / krok
    obtiznost = 1 + (x / obtiznost_mapy)
    y = (obrazovka_vyska * 0.5
         + math.sin(i * 0.004) * (120 * obtiznost)
         + math.sin(i * 0.025 + math.cos(i * 0.002)) * (60 * obtiznost)
         + math.sin(i * 0.13 + math.cos(i * 0.03)) * (18 + obtiznost * 5)
         + math.sin(i * 0.0025)
         + math.cos(i * 0.7) * 2
    )
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

GRAVITY = Vector(0, 0.2)

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
  step = radius * 2 / (WHEEL_COLLISION_CHECK_SUBDIVISIONS - 1)
  for i in range(WHEEL_COLLISION_CHECK_SUBDIVISIONS):
    point = Vector(ventity.position.x - radius + i * step, generace_bod(ventity.position.x - radius + i * step))
    if point.distance_to(ventity.position) < closest_distance:
      closest_distance = point.distance_to(ventity.position)
      closest_point = point 
  
  return closest_point

class Bike:
  def __init__(self, position):
    self.rear_axel = VerletEntity(position)
    self.front_axel = VerletEntity(position + Vector(BIKE_LENGTH, 0))

    self.rear_wheel = VerletEntity(position)
    self.front_wheel = VerletEntity(position + Vector(BIKE_LENGTH, 0))
    
    self.animace_index = 0
    self.rychlost_animace = 0.5
    self.energie = 100

  def tick(self):
    self.rear_axel.apply_gravity(GRAVITY)
    self.front_axel.apply_gravity(GRAVITY)
    self.rear_wheel.apply_gravity(GRAVITY)
    self.front_wheel.apply_gravity(GRAVITY)
  
    # suspension
    # rear wheel
    sus_force = (self.rear_axel.position - self.rear_wheel.position) * SUS_REAR
    self.rear_wheel.apply_force(sus_force)
    self.rear_axel.apply_force(sus_force * -1)
    self.rear_wheel.damp_relative_speed(self.rear_axel, DAMP_REAR)

    # front wheel
    sus_force = (self.front_axel.position - self.front_wheel.position) * SUS_FRONT
    self.front_wheel.apply_force(sus_force)
    self.front_axel.apply_force(sus_force * -1)
    self.front_wheel.damp_relative_speed(self.front_axel, DAMP_FRONT)

    # bike frame
    midpoint = (self.rear_axel.position + self.front_axel.position) / 2
    scaling_cof = BIKE_LENGTH / self.rear_axel.position.distance_to(self.front_axel.position)

    self.rear_axel.set_position(midpoint + (self.rear_axel.get_position() - midpoint) * scaling_cof)
    self.front_axel.set_position(midpoint + (self.front_axel.get_position() - midpoint) * scaling_cof)

    # collision check
    # rear wheel
    touch_point = wheel_collision_check(self.rear_wheel, WHEEL_RADIUS)
    if touch_point is not None:
      new_position = self.rear_wheel.get_position() + (self.rear_wheel.get_position() - touch_point).normalized() * (WHEEL_RADIUS - self.rear_wheel.get_position().distance_to(touch_point))
      self.rear_wheel.set_position(new_position)
      keys = pygame.key.get_pressed()
      if self.energie > 0:
        if keys[pygame.K_a]:
          self.animace_index -= self.rychlost_animace
          if self.animace_index < 0:
              self.animace_index = 12
          self.rear_wheel.apply_force((self.rear_axel.position - self.front_axel.position).normalized() * SLAPANI_FROCE)
        if keys[pygame.K_d]:
          self.animace_index += self.rychlost_animace
          if self.animace_index >= 13:
              self.animace_index = 0
          self.rear_wheel.apply_force((self.front_axel.position - self.rear_axel.position).normalized() * SLAPANI_FROCE)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        if self.energie > 0:
            self.animace_index -= self.rychlost_animace
            if self.animace_index < 0:
                self.animace_index = 12
        self.front_axel.apply_force((self.rear_axel.position - self.front_axel.position).normalized().perpendicular() * INAIR_FORCE)
        self.rear_axel.apply_force((self.rear_axel.position - self.front_axel.position).normalized().perpendicular() * -INAIR_FORCE)
    if keys[pygame.K_d]:
        if self.energie > 0:
            self.animace_index += self.rychlost_animace
            if self.animace_index >= 13:
                self.animace_index = 0
        self.front_axel.apply_force((self.rear_axel.position - self.front_axel.position).normalized().perpendicular() * -INAIR_FORCE)
        self.rear_axel.apply_force((self.rear_axel.position - self.front_axel.position).normalized().perpendicular() * INAIR_FORCE)

    # front wheel
    touch_point = wheel_collision_check(self.front_wheel, WHEEL_RADIUS)
    if touch_point is not None:
      new_position = self.front_wheel.get_position() + (self.front_wheel.get_position() - touch_point).normalized() * (WHEEL_RADIUS - self.front_wheel.get_position().distance_to(touch_point))
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

  def get_mask(self, kolo_img, rafek_img, camera):
    angle = (-180 / math.pi) * math.atan2(self.front_axel.position.y - self.rear_axel.position.y, self.front_axel.position.x - self.rear_axel.position.x)
    ram_img = pygame.transform.rotozoom(kolo_img, angle, 1.0)
    ram_mask = pygame.mask.from_surface(ram_img)
    width, height = ram_img.get_width(), ram_img.get_height()
    offset_center_to_bl = pygame.math.Vector2(-width / 2, height / 2)
    rotated_offset = offset_center_to_bl.rotate(-angle)
    center_x = self.rear_axel.position.x - camera.x - rotated_offset.x
    center_y = self.rear_axel.position.y - camera.y - rotated_offset.y
    ram_rect = ram_img.get_rect(center=(center_x, center_y))
    ram_pos = (ram_rect.left, ram_rect.top)

    rafek_img_rear = pygame.transform.rotozoom(rafek_img, (self.rear_wheel.get_position().x / (WHEEL_RADIUS)) * (-180 / math.pi), 1.0)
    rafek_mask_rear = pygame.mask.from_surface(rafek_img_rear)
    rafek_rect_rear = rafek_img_rear.get_rect(center=(int(self.rear_wheel.position.x - camera.x),int(self.rear_wheel.position.y - camera.y)))
    rafek_pos_rear = (rafek_rect_rear.left, rafek_rect_rear.top)

    uhel_front = (self.front_wheel.get_position().x / (WHEEL_RADIUS)) * (-180 / math.pi)
    rafek_img_front = pygame.transform.rotozoom(rafek_img, uhel_front, 1.0)
    rafek_mask_front = pygame.mask.from_surface(rafek_img_front)
    rafek_rect_front = rafek_img_front.get_rect(center=(int(self.front_wheel.position.x - camera.x),int(self.front_wheel.position.y - camera.y)))
    rafek_pos_front = (rafek_rect_front.left, rafek_rect_front.top)

    return [(ram_mask, ram_pos),(rafek_mask_rear, rafek_pos_rear),(rafek_mask_front, rafek_pos_front)]

