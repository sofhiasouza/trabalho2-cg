
import math
import glm
import numpy as np


class Model:
  
  def __init__(self, window, objects):

    self.ka_inside = 0.5 # coeficiente de reflexao ambiente interna do modelo
    self.kd_inside = 0.5 # coeficiente de reflexao difusa interna do modelo
    self.ks_inside = 0.5 # coeficiente de reflexao especular interna do modelo
    self.ka_outside = 0.5 # coeficiente de reflexao ambiente externa do modelo
    self.kd_outside = 0.5 # coeficiente de reflexao difusa externa do modelo
    self.ks_outside = 0.5 # coeficiente de reflexao especular externa do modelo
    self.ns = 0.9 # expoente de reflexao especular

    self.cameraPos   = glm.vec3(0.0,  0.0,  1.0)
    self.cameraFront = glm.vec3(0.0,  0.0, -1.0)
    self.cameraUp    = glm.vec3(0.0,  1.0,  0.0)

    self.polygonal_mode = False
    self.objects = objects

    self.firstMouse = True
    self.yaw = -90.0 
    self.pitch = 0.0
    self.lastX =  600
    self.lastY =  800

  def key_event(self, window,key,scancode,action,mods):
    cameraSpeed = 1
    newCameraPos = glm.vec3(self.cameraPos.x, self.cameraPos.y, self.cameraPos.z)
    if key == 87 and (action==1 or action==2): # tecla W
        newCameraPos += cameraSpeed * self.cameraFront
    
    if key == 83 and (action==1 or action==2): # tecla S
        newCameraPos -= cameraSpeed * self.cameraFront
    
    if key == 65 and (action==1 or action==2): # tecla A
        newCameraPos -= glm.normalize(glm.cross(self.cameraFront, self.cameraUp)) * cameraSpeed
        
    if key == 68 and (action==1 or action==2): # tecla D
        newCameraPos += glm.normalize(glm.cross(self.cameraFront, self.cameraUp)) * cameraSpeed

    distance = np.linalg.norm(np.array(newCameraPos) - np.array([0.0, 0.0, 0.0]))
    if distance < 370:
        self.cameraPos.x = newCameraPos.x
        self.cameraPos.y = newCameraPos.y
        self.cameraPos.z = newCameraPos.z
    
    if key == 80 and action==1 and self.polygonal_mode==True: # tecla P
        self.polygonal_mode=False
    else:
        if key == 80 and action==1 and self.polygonal_mode==False: # tecla P
            self.polygonal_mode=True
    

    # Teclas para movimentação de objeto
    obj = self.objects[8] # slender é o objeto que queremos movimentar

    if key == 265 and (action==1 or action==2): # tecla seta pra cima
        obj.angle += 2
        
    if key == 264 and (action==1 or action==2): # tecla seta pra baixo
        obj.angle -= 2

    if key == 262 and (action==1 or action==2): # tecla seta pra direita
        obj.s_x += 0.2
        obj.s_y += 0.2
        obj.s_z += 0.2
        
    if key == 263 and (action==1 or action==2): # tecla seta pra esquerda
        obj.s_x -= 0.2
        obj.s_y -= 0.2
        obj.s_z -= 0.2

    if key == 73 and (action==1 or action==2): # tecla I
        obj.t_x += 0.2
    if key == 75 and (action==1 or action==2): # tecla K
        obj.t_x -= 0.2
    if key == 74 and (action==1 or action==2): # tecla J
        obj.t_z -= 0.2
    if key == 76 and (action==1 or action==2): # tecla L
        obj.t_z += 0.2

    # Teclas para aumento e diminuição da iluminação

    # Aumento e diminuição da reflexão ambiente interna
    if key == 90 and (action == 1 or action == 2): # tecla Z
        self.ka_inside = min(self.ka_inside + 0.1, 1)
    if key == 88 and (action == 1 or action == 2): # tecla X
        self.ka_inside = max(self.ka_inside - 0.1, 0)

    # Aumento e diminuição da reflexão difusa interna
    if key == 67 and (action == 1 or action == 2): # tecla C
        self.kd_inside = min(self.kd_inside + 0.1, 1)
    if key == 86 and (action == 1 or action == 2): # tecla V
        self.kd_inside = max(self.kd_inside - 0.1, 0)

    # Aumento e diminuição da reflexão especular interna
    if key == 66 and (action == 1 or action == 2): # tecla B
        self.ks_inside = min(self.ks_inside + 0.1, 1)
    if key == 78 and (action == 1 or action == 2): # tecla N
        self.ks_inside = max(self.ks_inside - 0.1, 0)

    

    # Aumento e diminuição da reflexão ambiente externa
    if key == 69 and (action == 1 or action == 2): # tecla E
        self.ka_outside = min(self.ka_outside + 0.1, 1)
    if key == 82 and (action == 1 or action == 2): # tecla R
        self.ka_outside = max(self.ka_outside - 0.1, 0)

    # Aumento e diminuição da reflexão difusa externa
    if key == 84 and (action == 1 or action == 2): # tecla T
        self.kd_outside = min(self.kd_outside + 0.1, 1)
    if key == 89 and (action == 1 or action == 2): # tecla Y
        self.kd_outside = max(self.kd_outside - 0.1, 0)

    # Aumento e diminuição da reflexão especular externa
    if key == 85 and (action == 1 or action == 2): # tecla U
        self.ks_outside = min(self.ks_outside + 0.1, 1)
    if key == 79 and (action == 1 or action == 2): # tecla O
        self.ks_outside = max(self.ks_outside - 0.1, 0)


    # Atualiza os coeficientes de reflexão dos objetos de acordo com onde estão
    for obj in self.objects:
        if obj.is_inside:
            obj.ka = self.ka_inside
            obj.kd = self.kd_inside
            obj.ks = self.ks_inside
        else:
            obj.ka = self.ka_outside
            obj.kd = self.kd_outside
            obj.ks = self.ks_outside


  def mouse_event(self, window, xpos, ypos):
    if self.firstMouse:
        self.lastX = xpos
        self.lastY = ypos
        self.firstMouse = False

    xoffset = xpos - self.lastX
    yoffset = self.lastY - ypos
    self.lastX = xpos
    self.lastY = ypos

    sensitivity = 0.3 
    xoffset *= sensitivity
    yoffset *= sensitivity

    self.yaw += xoffset
    self.pitch += yoffset

    
    if self.pitch >= 90.0: self.pitch = 90.0
    if self.pitch <= -90.0: self.pitch = -90.0

    front = glm.vec3()
    front.x = math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
    front.y = math.sin(glm.radians(self.pitch))
    front.z = math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
    self.cameraFront = glm.normalize(front)



  def model(self, angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z):
    
    angle = math.radians(angle)
    
    matrix_transform = glm.mat4(1.0) # instanciando uma matriz identidade

    
    # aplicando translacao
    matrix_transform = glm.translate(matrix_transform, glm.vec3(t_x, t_y, t_z))    
    
    # aplicando rotacao
    matrix_transform = glm.rotate(matrix_transform, angle, glm.vec3(r_x, r_y, r_z))
    
    # aplicando escala
    matrix_transform = glm.scale(matrix_transform, glm.vec3(s_x, s_y, s_z))
    
    matrix_transform = np.array(matrix_transform)
    
    return matrix_transform

  def view(self):
      self.cameraPos[1] = 5
      mat_view = glm.lookAt(self.cameraPos, self.cameraPos + self.cameraFront, self.cameraUp);
      mat_view = np.array(mat_view)
      return mat_view

  def projection(self):
      # perspective parameters: fovy, aspect, near, far
      mat_projection = glm.perspective(glm.radians(45.0), 1200/1600, 0.1, 1000.0)
      mat_projection = np.array(mat_projection)    
      return mat_projection