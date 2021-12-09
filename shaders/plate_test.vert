#version 330

in vec2 in_pos;
in float plate;

out vec3 colour;

void main() {
    colour = vec3(0.5, vec2(plate));
    gl_Position = vec4(2*in_pos, 0.0, 1.0);
}

