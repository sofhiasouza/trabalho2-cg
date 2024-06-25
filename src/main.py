import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import glm
import math
from PIL import Image

from model import Model
from object import Object
from window import initialize_window
from shaders import create_shader_program

# model_file_path, texture_file_path, texture_id, position, rotation, scale, textures, is_inside,  is_light, is_sky
objects_arguments = [
    ['../assets/ground_stone/ground1.obj', '../assets/ground_stone/stone.jpg', [0.0, -1.0, 0.0], [0.0, 0.0, 0.0, 1.0], [10.0, 10.0, 10.0], 1, False, False, True],
    ['../assets/sky/sky.obj', '../assets/sky/animecloud.png', [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0], [0.75, 0.75, 0.75], 2, False, False, True],
    ['../assets/ground_forest/ground2.obj', '../assets/ground_forest/grass.jpg', [0.0, -1.0, 0.0], [0.0, 0.0, 0.0, 1.0], [10.0, 10.0, 10.0], 3, False, False, True],
    ['../assets/house/house.obj', '../assets/house/textures/Cottage_Clean_Base_Color.png',[-50.0, -3.0, -30.0], [90.0, -90.0, 1.0, 0.0], [5.0, 5.0, 5.0], 5, False, False],
    ['../assets/table/wood_table.obj', '../assets/table/wood_table.png', [-50.0, -0.5, -30.0], [-90.0, 1.0, 0.0, 0.0], [0.25, 0.25, 0.25], 7, True, False],
    ['../assets/chair/chair.obj', '../assets/chair/chair.png',[-50.0, 2.5, -26.0], [0.0, 0.0, 1.0, 0.0], [0.4, 0.4, 0.4], 8, True, False],
    ['../assets/box/box.obj', '../assets/box/box.jpg', [-40.0, 0.0, -30.0], [-90.0, 1.0, 0.0, 0.0], [0.9, 0.9, 0.9], 9, True, False],
    ['../assets/raptor/raptor.obj', '../assets/raptor/raptor.jpg', [-10.0, -0.5, -30.0], [90.0, 1.0, 90.0, 0.0], [0.15, 0.15, 0.15], 10, False, False],
    ['../assets/slenderman/slenderman.obj', '../assets/slenderman/slenderman.png', [10.0, -0.5, -30.0], [90.0, 1.0, 90.0, 0.0], [0.7, 0.7, 0.7], 11, False, False],
    ['../assets/fence/fence.obj', '../assets/fence/fence.jpg', [0.0, -1.1, 0.0], [90.0, 0.0, 1.0, 0.0], [30.0, 30.0, 30.0], 4, False, False],
    ['../assets/luz/luz.obj', '../assets/luz/luz.png', [15.0, 0.0, -30.0], [90.0, 1.0, 90.0, 0.0], [0.3, 0.3, 0.3], 12, False, True],
    ['../assets/luz/luz.obj', '../assets/luz/luz.png', [-55.0, 0.0, -30.0], [90.0, 1.0, 90.0, 0.0], [0.3, 0.3, 0.3], 12, True, True]]


def main():
    if not glfw.init():
        return
    
    window = initialize_window(1600, 1200, "OpenGL App")

    if not window:
        glfw.terminate()
        return

    program = create_shader_program()

    glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
    glEnable(GL_TEXTURE_2D)
    qtd_texturas = 10
    textures = glGenTextures(qtd_texturas)

    vertices_list = []    
    normals_list = []    
    textures_coord_list = []

    # Cria os objetos
    objects = []
    for arguments in objects_arguments:
        obj = Object(*arguments)
        obj.load_model(vertices_list, textures_coord_list, normals_list)
        objects.append(obj)

    # Request a buffer slot from GPU
    buffer = glGenBuffers(3)

    # Enviando coordenadas de vértices para a GPU
    vertices = np.zeros(len(vertices_list), [("position", np.float32, 3)])
    vertices['position'] = vertices_list

    glBindBuffer(GL_ARRAY_BUFFER, buffer[0])
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    stride = vertices.strides[0]
    offset = ctypes.c_void_p(0)
    loc_vertices = glGetAttribLocation(program, "position")
    glEnableVertexAttribArray(loc_vertices)
    glVertexAttribPointer(loc_vertices, 3, GL_FLOAT, False, stride, offset)

    # Enviando coordenadas de textura para a GPU
    textures = np.zeros(len(textures_coord_list), [("position", np.float32, 2)]) # duas coordenadas
    textures['position'] = textures_coord_list

    glBindBuffer(GL_ARRAY_BUFFER, buffer[1])
    glBufferData(GL_ARRAY_BUFFER, textures.nbytes, textures, GL_STATIC_DRAW)
    stride = textures.strides[0]
    offset = ctypes.c_void_p(0)
    loc_texture_coord = glGetAttribLocation(program, "texture_coord")
    glEnableVertexAttribArray(loc_texture_coord)
    glVertexAttribPointer(loc_texture_coord, 2, GL_FLOAT, False, stride, offset)

    # Enviando coordenadas de normais para a GPU
    normals = np.zeros(len(normals_list), [("position", np.float32, 3)]) # três coordenadas
    normals['position'] = normals_list

    glBindBuffer(GL_ARRAY_BUFFER, buffer[2])
    glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)
    stride = normals.strides[0]
    offset = ctypes.c_void_p(0)
    loc_normals_coord = glGetAttribLocation(program, "normals")
    glEnableVertexAttribArray(loc_normals_coord)
    glVertexAttribPointer(loc_normals_coord, 3, GL_FLOAT, False, stride, offset)

    model = Model(window, objects)

    glfw.set_key_callback(window, model.key_event)
    glfw.set_cursor_pos_callback(window, model.mouse_event)

    glfw.show_window(window)
    glfw.set_cursor_pos(window, model.lastX, model.lastY)

    glEnable(GL_DEPTH_TEST) ### importante para 3D

    # Main loop
    while not glfw.window_should_close(window):

        glfw.poll_events() 
        
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glClearColor(1.0, 1.0, 1.0, 1.0)
        
        if model.polygonal_mode==True:
            glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
        if model.polygonal_mode==False:
            glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)   
        

        # draw objects
        for obj in objects:
            obj.draw(model.model, program)


        # draw fence dividing spaces
        obj = objects[9]
        for i in range(-40, -10, 10):
            obj.t_z = i
            obj.draw(model.model, program)
        for i in range(0, 40, 10):
            obj.t_z = i
            obj.draw(model.model, program)

       # draw 4 chairs
        chair_positions = [
            (-50.0, -34.0, 180.0),
            (-52.0, -30.0, -90.0),
            (-48.0, -30.0, 90.0),
            (-50.0, -26.0, 0.0)
        ]

        obj = objects[5]
        for t_x, t_z, angle in chair_positions:
            obj.t_x = t_x
            obj.t_z = t_z
            obj.angle = angle
            obj.draw(model.model, program)


        mat_view = model.view()
        loc_view = glGetUniformLocation(program, "view")
        glUniformMatrix4fv(loc_view, 1, GL_TRUE, mat_view)

        mat_projection = model.projection()
        loc_projection = glGetUniformLocation(program, "projection")
        glUniformMatrix4fv(loc_projection, 1, GL_TRUE, mat_projection)    

        # atualizando a posicao da camera/observador na GPU para calculo da reflexao especular
        loc_view_pos = glGetUniformLocation(program, "viewPos") # recuperando localizacao da variavel viewPos na GPU
        glUniform3f(loc_view_pos, model.cameraPos[0], model.cameraPos[1], model.cameraPos[2]) ### posicao da camera/observador (x,y,z)
        
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()
