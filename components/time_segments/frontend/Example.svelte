<script lang="ts">
	export let value: [number, number | null][] | null;
	export let type: "gallery" | "table";
	export let selected = false;

	function hms(seconds: number | null): string {
		if (seconds == null || seconds <= 0) return "fin";
		const p = (n: number) => String(n).padStart(2, "0");
		return `${p(Math.floor(seconds / 3600))}:${p(Math.floor((seconds % 3600) / 60))}:${p(seconds % 60)}`;
	}
</script>

<div class:table={type === "table"} class:gallery={type === "gallery"} class:selected>
	{(value ?? []).map(([s, e]) => `${hms(s || 0)} → ${hms(e)}`).join(", ")}
</div>

<style>
	.gallery {
		padding: var(--size-1) var(--size-2);
	}
	div {
		overflow: hidden;
		white-space: nowrap;
	}
</style>
