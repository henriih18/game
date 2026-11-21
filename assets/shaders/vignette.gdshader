shader_type canvas_item;

uniform float intensity : hint_range(0.0, 1.0) = 0.0;
uniform vec4 danger_color : source_color = vec4(0.85, 0.08, 0.12, 1.0);

void fragment() {
	vec2 centered = UV - vec2(0.5);
	centered.y *= 0.9;
	float dist = length(centered);
	float edge = smoothstep(0.3, 0.72, dist);
	float pulse = 0.88 + 0.12 * sin(TIME * 7.0);
	COLOR = vec4(danger_color.rgb, edge * intensity * pulse);
}
