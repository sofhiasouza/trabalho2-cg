from OpenGL.GL import *

def create_shader_program():
    vertex_code = """
    attribute vec3 position;
    attribute vec2 texture_coord;
    attribute vec3 normals;
    
    
    varying vec2 out_texture;
    varying vec3 out_fragPos;
    varying vec3 out_normal;
            
    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 projection;        
    
    void main(){
        gl_Position = projection * view * model * vec4(position,1.0);
        out_texture = vec2(texture_coord);
        out_fragPos = vec3(  model * vec4(position, 1.0));
        out_normal = vec3( model *vec4(normals, 1.0));            
    }
    """
    
    fragment_code = """
    uniform vec3 lightPosInside; // define coordenadas de posicao da luz interna
    uniform vec3 lightPosOutside; // define coordenadas de posicao da luz externa
    uniform int inside; //flag que indica se a luz é a interna ou a externa

    // parametros da iluminacao ambiente e difusa
    uniform float ka; // coeficiente de reflexao ambiente
    uniform float kd; // coeficiente de reflexao difusa
    
    // parametros da iluminacao especular
    uniform vec3 viewPos; // define coordenadas com a posicao da camera/observador
    uniform float ks; // coeficiente de reflexao especular
    uniform float ns; // expoente de reflexao especular
    
    // parametro com a cor da(s) fonte(s) de iluminacao
    vec3 lightColorInside = vec3(1.0, 0.95, 0.78);
    vec3 lightColorOutside = vec3(1, 0.55, 0.15);
    vec3 lightColorAmbient = vec3(1.0, 0.95, 0.78);

    // parametros recebidos do vertex shader
    varying vec2 out_texture; // recebido do vertex shader
    varying vec3 out_normal; // recebido do vertex shader
    varying vec3 out_fragPos; // recebido do vertex shader
    uniform sampler2D samplerTexture;

    vec3 diffuseInside = vec3(0.0);
    vec3 diffuseOutside = vec3(0.0);
    vec3 specularInside = vec3(0.0);
    vec3 specularOutside = vec3(0.0);
    
    void main(){ 

        //Luz Externa 
        if(inside == 0){ 
            
            // calculando reflexao difusa
            vec3 normOutside = normalize(out_normal); // normaliza vetores perpendiculares
            vec3 lightDirOutside = normalize(lightPosOutside - out_fragPos); // direcao da luz
            float diffOutside = max(dot(normOutside, lightDirOutside), 0.0); // verifica limite angular (entre 0 e 90)
            diffuseOutside = kd * diffOutside * lightColorOutside; // iluminacao difusa
            
            // calculando reflexao especular
            vec3 viewDirOutside = normalize(viewPos - out_fragPos); // direcao do observador/camera
            vec3 reflectDirOutside = reflect(-lightDirOutside, normOutside); // direcao da reflexao
            float specOutside = pow(max(dot(viewDirOutside, reflectDirOutside), 0.0), ns);
            specularOutside = ks * specOutside * lightColorOutside;    

        }           

        // Luz Interna
        if(inside == 1){
            
            // calculando reflexao difusa
            vec3 normInside = normalize(out_normal); // normaliza vetores perpendiculares
            vec3 lightDirInside = normalize(lightPosInside - out_fragPos); // direcao da luz
            float diffInside = max(dot(normInside, lightDirInside), 0.0); // verifica limite angular (entre 0 e 90)
            diffuseInside = kd * diffInside * lightColorInside; // iluminacao difusa
            
            // calculando reflexao especular
            vec3 viewDirInside = normalize(viewPos - out_fragPos); // direcao do observador/camera
            vec3 reflectDirInside = reflect(-lightDirInside, normInside); // direcao da reflexao
            float specInside = pow(max(dot(viewDirInside, reflectDirInside), 0.0), ns);
            specularInside = ks * specInside * lightColorInside;

            lightColorAmbient = vec3(1, 0.55, 0.15);    
        }

        // calculando reflexao ambiente
        vec3 ambient = ka * lightColorAmbient; 
        
        // aplicando o modelo de iluminacao
        vec4 texture = texture2D(samplerTexture, out_texture);
        vec4 result = vec4((ambient + diffuseOutside + diffuseInside + specularOutside + specularInside),1.0) * texture;
        gl_FragColor = result;
    }
    """
    
    # Request a program and shader slots from GPU
    program  = glCreateProgram()
    vertex   = glCreateShader(GL_VERTEX_SHADER)
    fragment = glCreateShader(GL_FRAGMENT_SHADER)

    # Set shaders source
    glShaderSource(vertex, vertex_code)
    glShaderSource(fragment, fragment_code)

    # Compile shaders
    glCompileShader(vertex)
    if not glGetShaderiv(vertex, GL_COMPILE_STATUS):
        error = glGetShaderInfoLog(vertex).decode()
        print(error)
        raise RuntimeError("Erro de compilacao do Vertex Shader")
        
    glCompileShader(fragment)
    if not glGetShaderiv(fragment, GL_COMPILE_STATUS):
        error = glGetShaderInfoLog(fragment).decode()
        print(error)
        raise RuntimeError("Erro de compilacao do Fragment Shader")
    
    # Attach shader objects to the program
    glAttachShader(program, vertex)
    glAttachShader(program, fragment)

    # Build program
    glLinkProgram(program)
    if not glGetProgramiv(program, GL_LINK_STATUS):
        print(glGetProgramInfoLog(program))
        raise RuntimeError('Linking error')
        
    # Make program the default program
    glUseProgram(program)

    return program
