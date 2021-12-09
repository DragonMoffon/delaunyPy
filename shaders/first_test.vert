#version 330

in vec2 in_pos;

out vec3 colour;

void main() {
    colour = vec3(in_pos + 0.5, .2);
    gl_Position = vec4(2*in_pos, 0.0, 1.0);
}
