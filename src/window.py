import glfw

def initialize_window(width, height, title):
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
    window = glfw.create_window(width, height, title, None, None)
    glfw.make_context_current(window)
    return window
