shader_type canvas_item;

uniform sampler2D screen_texture : hint_screen_texture, filter_linear_mipmap;
uniform float vignette_intensity : hint_range(0.0, 1.0) = 0.34;
uniform float grain_amount : hint_range(0.0, 0.15) = 0.028;
uniform float aberration : hint_range(0.0, 0.004) = 0.00055;
uniform float contrast : hint_range(0.8, 1.3) = 1.06;
uniform float saturation : hint_range(0.5, 1.5) = 0.94;

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void fragment() {
	vec2 uv = SCREEN_UV;
	vec2 centered = uv - vec2(0.5);
	float edge = smoothstep(0.28, 0.78, length(centered));
	vec2 offset = centered * aberration;

	vec3 col;
	col.r = texture(screen_texture, uv + offset).r;
	col.g = texture(screen_texture, uv).g;
	col.b = texture(screen_texture, uv - offset).b;

	col = (col - 0.5) * contrast + 0.5;
	float luma = dot(col, vec3(0.2126, 0.7152, 0.0722));
	col = mix(vec3(luma), col, saturation);

	float grain = (hash(uv * vec2(1920.0, 1080.0) + TIME * 13.0) - 0.5) * grain_amount;
	col += vec3(grain);
	col *= 1.0 - edge * vignette_intensity;

	COLOR = vec4(max(col, vec3(0.0)), 1.0);
}
