<svelte:options accessors={true} />

<script lang="ts">
	import type { Gradio } from "@gradio/utils";
	// @gradio/atoms (Block, BlockTitle) and StatusTracker are not used on purpose: importing them
	// pulls Gradio's markdown renderer (marked, katex, prism, mermaid: several MB) into the bundle.
	// The block container below reproduces Block's layout with the same CSS variables.
	import type { LoadingStatus } from "@gradio/statustracker";
	import TimeField from "./TimeField.svelte";

	type Segment = [number, number | null];

	export let gradio: Gradio<{
		change: never;
		input: never;
		clear_status: LoadingStatus;
	}>;
	export let label = "Segments";
	export let info: string | undefined = undefined;
	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let visible = true;
	export let value: Segment[] = [[0, null]];
	export let max_segments: number | null = null;
	export let maximum: number | null = null;
	export let show_label = true;
	export let scale: number | null = null;
	export let min_width: number | undefined = undefined;
	export let loading_status: LoadingStatus | undefined = undefined;
	export let value_is_output = false;
	export let interactive = true;
	export let root: string;

	$: if (!Array.isArray(value) || value.length === 0) value = [[0, null]];
	$: single = max_segments === 1;
	$: can_add = interactive && (max_segments == null || value.length < max_segments);

	function hms(seconds: number): string {
		const s = Math.floor(seconds);
		const p = (n: number) => String(n).padStart(2, "0");
		return `${p(Math.floor(s / 3600))}:${p(Math.floor((s % 3600) / 60))}:${p(s % 60)}`;
	}

	/** why a row is invalid ("" when it is fine); the back-end re-checks everything */
	function problem(seg: Segment, i: number, count: number, max: number | null): string {
		const [start, end] = seg;
		const has_end = end != null && end > 0;
		if (!has_end && i < count - 1) return "seule la dernière ligne peut aller jusqu'à la fin";
		if (has_end && end <= start) return "la fin doit être après le début";
		if (max != null && max > 0 && start >= max) return "le début est après la fin de la vidéo";
		return "";
	}

	function emit(): void {
		gradio.dispatch("change");
		if (!value_is_output) gradio.dispatch("input");
	}

	function set(i: number, k: 0 | 1, v: number | null): void {
		value = value.map((seg, j) => (j === i ? ((k === 0 ? [v ?? 0, seg[1]] : [seg[0], v]) as Segment) : seg));
		emit();
	}

	function add(): void {
		const last = value[value.length - 1];
		const start = last ? (last[1] != null && last[1] > 0 ? last[1] : last[0]) : 0;
		value = [...value, [start, null]];
		emit();
	}

	function remove(i: number): void {
		if (value.length <= 1) return;
		value = value.filter((_, j) => j !== i);
		emit();
	}
</script>

<div
	id={elem_id}
	class="block {elem_classes?.join(' ') || ''}"
	class:hidden={visible === false}
	class:auto-margin={scale === null}
	style:flex-grow={scale}
	style:min-width={`calc(min(${min_width ?? 0}px, 100%))`}
>
	{#if show_label && label}<span class="block-label">{label}</span>{/if}
	{#if info}<span class="block-info">{info}</span>{/if}

	<div class="segments">
		<div class="head">
			<span>début → fin · cliquez sur hh, mm ou ss et tapez</span>
			{#if maximum != null && maximum > 0}<span class="max">max {hms(maximum)}</span>{/if}
		</div>
		{#each value as seg, i (i)}
			{@const why = problem(seg, i, value.length, maximum)}
			<div class="row" class:bad={why !== ""}>
				{#if !single}<span class="num">{i + 1}</span>{/if}
				<TimeField
					value={seg[0]}
					max={maximum}
					invalid={why !== ""}
					disabled={!interactive}
					aria_label={`début du segment ${i + 1}`}
					on:change={(e) => set(i, 0, e.detail)}
				/>
				<span class="arrow">→</span>
				<TimeField
					value={seg[1] != null && seg[1] > 0 ? seg[1] : null}
					max={maximum}
					allow_empty
					invalid={why !== ""}
					disabled={!interactive}
					aria_label={`fin du segment ${i + 1}`}
					on:change={(e) => set(i, 1, e.detail)}
				/>
				{#if !single && interactive}
					<button
						type="button"
						class="remove"
						title="Supprimer ce segment"
						disabled={value.length <= 1}
						on:click={() => remove(i)}>✖</button
					>
				{/if}
				{#if why}<span class="why">{why}</span>{/if}
			</div>
		{/each}
		{#if !single && can_add}
			<button type="button" class="add" on:click={add}>+ Ajouter un segment</button>
		{/if}
	</div>
</div>

<style>
	.block {
		position: relative;
		margin: 0;
		box-shadow: var(--block-shadow);
		border: var(--block-border-width) solid var(--block-border-color);
		border-radius: var(--block-radius);
		background: var(--block-background-fill);
		width: 100%;
		line-height: var(--line-sm);
		padding: var(--block-padding);
		overflow: hidden;
	}
	.auto-margin {
		margin-left: auto;
		margin-right: auto;
	}
	.hidden {
		display: none;
	}
	.block-label {
		display: block;
		margin-bottom: var(--spacing-lg);
		color: var(--block-title-text-color);
		font-weight: var(--block-title-text-weight);
		font-size: var(--block-title-text-size);
		line-height: var(--line-sm);
	}
	.block-info {
		display: block;
		margin-top: calc(-1 * var(--spacing-md));
		margin-bottom: var(--spacing-lg);
		color: var(--block-info-text-color);
		font-size: var(--block-info-text-size);
	}
	.segments {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-md);
	}
	.head,
	.row {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: var(--spacing-md);
	}
	.head {
		font-size: var(--text-sm);
		color: var(--body-text-color-subdued);
	}
	.max {
		margin-left: auto;
	}
	.num {
		width: 1.5em;
		text-align: right;
		color: var(--body-text-color-subdued);
		font-size: var(--text-sm);
	}
	.arrow {
		color: var(--body-text-color-subdued);
	}
	.why {
		flex-basis: 100%;
		color: var(--color-red-500, #ef4444);
		font-size: var(--text-sm);
		padding-left: 2em;
	}
	.remove,
	.add {
		border: var(--button-border-width) solid var(--button-secondary-border-color);
		background: var(--button-secondary-background-fill);
		color: var(--button-secondary-text-color);
		border-radius: var(--button-small-radius, var(--radius-sm));
		cursor: pointer;
	}
	.remove {
		padding: 2px 8px;
	}
	.remove:disabled {
		opacity: 0.4;
		cursor: default;
	}
	.add {
		align-self: flex-start;
		padding: var(--button-small-padding, 4px 10px);
		font-size: var(--text-sm);
	}
	.add:hover,
	.remove:hover:not(:disabled) {
		background: var(--button-secondary-background-fill-hover);
	}
</style>
