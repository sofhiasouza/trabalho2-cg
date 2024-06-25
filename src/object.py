from OpenGL.GL import *
import numpy as np
from PIL import Image

class Object:
    def __init__(self, model_file_path, texture_file_path, position, rotation, scale, texture_id, is_inside,  is_light, is_sky = False):
        self.model_file_path = model_file_path
        self.texture_file_path = texture_file_path
        self.angle = rotation[0]
        self.r_x = rotation[1]
        self.r_y = rotation[2] 
        self.r_z = rotation[3]
        self.t_x = position[0]
        self.t_y = position[1]
        self.t_z = position[2]
        self.s_x = scale[0]
        self.s_y = scale[1]
        self.s_z = scale[2]
        self.texture_id = texture_id
        self.is_inside = is_inside
        self.is_light = is_light
        self.is_sky = is_sky
        
        self.model_size = 0
        self.model_start = 0
        self.ka = 0.5
        self.kd = 0.5
        self.ks = 0.5
        self.ns = 0.5

        if self.is_light:
            self.ns = 1
            self.ka = 1
            self.kd = 1
            self.ks = 1


    def load_model_from_file(self):
        """Loads a Wavefront OBJ file. """
        vertices = []
        normals = []
        texture_coords = []
        faces = []

        material = None

        # abre o arquivo obj para leitura
        for line in open(self.model_file_path, "r"): ## para cada linha do arquivo .obj
            if line.startswith('#'): continue ## ignora comentarios
            values = line.split() # quebra a linha por espaço
            if not values: continue


            ### recuperando vertices
            if values[0] == 'v':
                vertices.append(values[1:4])

            ### recuperando vertices
            if values[0] == 'vn':
                normals.append(values[1:4])

            ### recuperando coordenadas de textura
            elif values[0] == 'vt':
                texture_coords.append(values[1:3])

            ### recuperando faces 
            elif values[0] in ('usemtl', 'usemat'):
                material = values[1]
            elif values[0] == 'f':
                face = []
                face_texture = []
                face_normals = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if(len(w) == 3):
                        face_normals.append(int(w[2]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        face_texture.append(int(w[1]))
                    else:
                        face_texture.append(0)

                faces.append((face, face_texture, face_normals, material))

        model = {}
        model['vertices'] = vertices
        model['texture'] = texture_coords
        model['faces'] = faces
        model['normals'] = normals

        return model

    def load_texture_from_file(self):
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        img = Image.open(self.texture_file_path)
        img_width = img.size[0]
        img_height = img.size[1]
        image_data = img.tobytes("raw", "RGB", 0, -1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img_width, img_height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)


    def load_model(self, vertices_list, textures_coord_list, normals_list):
        modelo = self.load_model_from_file()
        self.model_start = len(vertices_list)
        ### inserindo vertices do modelo no vetor de vertices
        print('Processando modelo. Vertice inicial:',len(vertices_list))
        for face in modelo['faces']:
            for vertice_id in face[0]:
                vertices_list.append( modelo['vertices'][vertice_id-1] )
            for texture_id in face[1]:
                textures_coord_list.append( modelo['texture'][texture_id-1] )
            if len(face[2]) > 0 and len(modelo['normals']) > 0 and len(modelo['normals']) >= face[2][0]:
                for normal_id in face[2]:
                    normals_list.append( modelo['normals'][normal_id-1] )
        print('Processando modelo. Vertice final:',len(vertices_list))

        self.model_size = len(vertices_list) - self.model_start

        ### carregando textura equivalente e definindo um id (buffer): 
        self.load_texture_from_file()


    def draw(self, model, program):
        # aplica a matriz model
        
        mat_model = model(self.angle, self.r_x, self.r_y, self.r_z, self.t_x, self.t_y, self.t_z, self.s_x, self.s_y, self.s_z)
        loc_model = glGetUniformLocation(program, "model")
        glUniformMatrix4fv(loc_model, 1, GL_TRUE, mat_model)

        if self.is_sky == True:
            self.kd = 0.0
            self.ks = 0.0

        loc_inside = glGetUniformLocation(program, "inside") # recuperando localizacao da variavel inside na GPU
        glUniform1i(loc_inside, self.is_inside) ### envia inside pra gpu
        
        loc_ka = glGetUniformLocation(program, "ka") # recuperando localizacao da variavel ka na GPU
        glUniform1f(loc_ka, self.ka) ### envia ka pra gpu
        
        loc_kd = glGetUniformLocation(program, "kd") # recuperando localizacao da variavel kd na GPU
        glUniform1f(loc_kd, self.kd) ### envia kd pra gpu    
        
        loc_ks = glGetUniformLocation(program, "ks") # recuperando localizacao da variavel ks na GPU
        glUniform1f(loc_ks, self.ks) ### envia ks pra gpu        
        
        loc_ns = glGetUniformLocation(program, "ns") # recuperando localizacao da variavel ns na GPU
        glUniform1f(loc_ns, self.ns) ### envia ns pra gpu        

        if self.is_light == True:
            # recuperando localizacao da variavel lightPos na GPU
            loc_light_pos = glGetUniformLocation(program, "lightPosInside") 
            if self.is_inside == False: 
                loc_light_pos = glGetUniformLocation(program, "lightPosOutside") 
            # posicao da fonte de luz
            glUniform3f(loc_light_pos, self.t_x, self.t_y, self.t_z)
        
        #define id da textura do modelo
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
            
        # desenha o modelo
        glDrawArrays(GL_TRIANGLES, self.model_start, self.model_size) ## renderizando