shader_type spatial;
render_mode diffuse_burley, specular_schlick_ggx;

uniform vec3 color_a : source_color = vec3(0.10, 0.12, 0.17);
uniform vec3 color_b : source_color = vec3(0.13, 0.16, 0.22);
uniform float tile_size = 1.6;

varying vec3 world_pos;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec2 cell = floor(world_pos.xz / tile_size);
	float checker = mod(cell.x + cell.y, 2.0);
	vec3 base = mix(color_a, color_b, checker);

	vec2 grid = abs(fract(world_pos.xz / tile_size + 0.5) - 0.5) / fwidth(world_pos.xz / tile_size);
	float line = 1.0 - min(min(grid.x, grid.y), 1.0);
	ALBEDO = mix(base, base * 1.35, line * 0.22);
	ROUGHNESS = 0.82;
	SPECULAR = 0.25;
}
