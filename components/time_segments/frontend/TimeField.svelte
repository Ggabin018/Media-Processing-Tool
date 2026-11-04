<!--
	Segmented hh:mm:ss field, like a date input: click a part, type digits.
	- typing replaces the selected part; after 2 digits (or a digit that cannot start a valid 2-digit
	  value, e.g. 7 in minutes) the focus moves to the next part
	- ↑/↓: ±1 (Shift: ±10), ←/→ or ":" to move, Backspace clears the part then goes back
	- paste "1:02:30", "02:30" or "150" anywhere: fills the whole field
	- value: seconds, or null when allow_empty (shown as `empty_label`)
-->
<script lang="ts">
	import { createEventDispatcher, tick } from "svelte";

	export let value: number | null = 0;
	export let max: number | null = null;
	export let allow_empty = false;
	export let empty_label = "fin de la vidéo";
	export let disabled = false;
	export let invalid = false;
	export let aria_label = "time";

	const dispatch = createEventDispatcher<{ change: number | null }>();
	const LIMITS = [99, 59, 59];
	const NAMES = ["heures", "minutes", "secondes"];

	let inputs: HTMLInputElement[] = [];
	let parts = [0, 0, 0];
	let typed = 0; // digits typed in the focused part since it got the focus
	let focused = -1;
	let editing = false; // allow_empty: fields shown while the value is still empty (null)
	let group: HTMLDivElement;

	$: if (focused === -1) parts = split(value ?? 0);

	function split(seconds: number): number[] {
		seconds = Math.max(0, Math.floor(seconds));
		return [Math.min(99, Math.floor(seconds / 3600)), Math.floor((seconds % 3600) / 60), seconds % 60];
	}

	function pad(n: number): string {
		return String(n).padStart(2, "0");
	}

	function total(p: number[]): number {
		return p[0] * 3600 + p[1] * 60 + p[2];
	}

	function commit(): void {
		let seconds = total(parts);
		if (max != null && max > 0 && seconds > max) {
			seconds = Math.floor(max);
			parts = split(seconds);
		}
		if (allow_empty && seconds === 0) {
			// 00:00:00 on an end field means "until the end": keep the value empty (null)
			if (value !== null) {
				value = null;
				dispatch("change", value);
			}
			return;
		}
		if (seconds !== value) {
			value = seconds;
			dispatch("change", value);
		}
	}

	async function focus_part(i: number): Promise<void> {
		if (i < 0 || i > 2) return;
		await tick();
		inputs[i]?.focus();
		inputs[i]?.select();
	}

	function on_focus(i: number): void {
		focused = i;
		typed = 0;
		inputs[i]?.select();
	}

	function on_blur(): void {
		focused = -1;
		typed = 0;
		commit();
		if (allow_empty) {
			// wait for the focus to land: moving from mm to ss also blurs mm
			setTimeout(() => {
				if (!group?.contains(document.activeElement) && value === null) editing = false;
			}, 0);
		}
	}

	function set_part(i: number, n: number): void {
		parts[i] = Math.max(0, Math.min(LIMITS[i], n));
		parts = parts;
		commit();
	}

	function on_keydown(i: number, e: KeyboardEvent): void {
		if (disabled) return;
		const key = e.key;
		if (/^[0-9]$/.test(key)) {
			e.preventDefault();
			const d = Number(key);
			if (typed === 0) {
				set_part(i, d);
				typed = 1;
				if (d * 10 > LIMITS[i]) {
					typed = 0;
					focus_part(i + 1); // e.g. "7" in minutes can only mean 07
				}
			} else {
				set_part(i, (parts[i] % 10) * 10 + d);
				typed = 0;
				focus_part(i + 1);
			}
			if (i === 2 && typed === 0) inputs[i]?.select();
			return;
		}
		switch (key) {
			case "ArrowUp":
			case "ArrowDown": {
				e.preventDefault();
				const step = (e.shiftKey ? 10 : 1) * (key === "ArrowUp" ? 1 : -1);
				set_part(i, parts[i] + step);
				typed = 0;
				inputs[i]?.select();
				return;
			}
			case "ArrowLeft":
				e.preventDefault();
				focus_part(i - 1);
				return;
			case "ArrowRight":
			case ":":
			case ".":
			case " ":
				e.preventDefault();
				focus_part(i + 1);
				return;
			case "Backspace":
			case "Delete":
				e.preventDefault();
				if (parts[i] !== 0) {
					set_part(i, 0);
					typed = 0;
					inputs[i]?.select();
				} else if (key === "Backspace") {
					focus_part(i - 1);
				}
				return;
			case "Tab":
			case "Enter":
			case "Escape":
				return; // default behaviour
			default:
				if (key.length === 1 && !e.ctrlKey && !e.metaKey) e.preventDefault(); // letters...
		}
	}

	export function parse(text: string): number | null {
		const t = text.trim();
		if (!/^\d+(:\d+){0,2}$/.test(t)) return null;
		return t.split(":").reduce((acc, p) => acc * 60 + Number(p), 0);
	}

	function on_paste(e: ClipboardEvent): void {
		if (disabled) return;
		const seconds = parse(e.clipboardData?.getData("text") ?? "");
		e.preventDefault();
		if (seconds == null) return;
		parts = split(seconds);
		typed = 0;
		commit();
		inputs[focused]?.select();
	}

	async function start_editing(): Promise<void> {
		if (disabled) return;
		editing = true; // value stays null until a non-zero time is typed
		parts = [0, 0, 0];
		await focus_part(0);
	}

	function clear(): void {
		editing = false;
		value = null;
		dispatch("change", value);
	}
</script>

{#if allow_empty && value === null && !editing}
	<button type="button" class="time empty" {disabled} on:click={start_editing} aria-label={aria_label}>
		{empty_label}
	</button>
{:else}
	<div bind:this={group} class="time" class:invalid class:disabled role="group" aria-label={aria_label}>
		{#each parts as part, i}
			<input
				bind:this={inputs[i]}
				value={pad(part)}
				inputmode="numeric"
				size="2"
				aria-label={NAMES[i]}
				{disabled}
				on:focus={() => on_focus(i)}
				on:click={() => inputs[i]?.select()}
				on:blur={on_blur}
				on:keydown={(e) => on_keydown(i, e)}
				on:paste={on_paste}
				on:input={(e) => (e.currentTarget.value = pad(parts[i]))}
			/>
			{#if i < 2}<span class="sep">:</span>{/if}
		{/each}
		{#if allow_empty && !disabled}
			<button type="button" class="reset" title={empty_label} on:click={clear}>×</button>
		{/if}
	</div>
{/if}

<style>
	.time {
		display: inline-flex;
		align-items: center;
		gap: 0;
		min-width: 9.5em;
		background: var(--input-background-fill);
		border: var(--input-border-width) solid var(--input-border-color);
		border-radius: var(--input-radius);
		padding: var(--input-padding);
		box-shadow: var(--input-shadow);
		color: var(--body-text-color);
		font-size: var(--input-text-size);
		font-variant-numeric: tabular-nums;
	}
	.time:focus-within {
		border-color: var(--input-border-color-focus);
		box-shadow: var(--input-shadow-focus);
	}
	.time.invalid {
		border-color: var(--color-red-500, #ef4444);
	}
	input {
		width: 2ch;
		padding: 0;
		margin: 0;
		border: none;
		outline: none;
		background: transparent;
		color: inherit;
		font: inherit;
		text-align: center;
		caret-color: transparent;
		border-radius: var(--radius-sm);
		cursor: pointer;
	}
	input:focus {
		background: var(--color-accent-soft);
	}
	input::selection {
		background: var(--color-accent-soft);
	}
	.sep {
		opacity: 0.6;
		padding: 0 1px;
	}
	.empty {
		color: var(--input-placeholder-color);
		cursor: pointer;
		font-style: italic;
		justify-content: center;
	}
	.reset {
		margin-left: auto;
		padding: 0 4px;
		border: none;
		background: transparent;
		color: var(--body-text-color-subdued);
		cursor: pointer;
		font-size: 1.1em;
		line-height: 1;
	}
	.disabled input {
		cursor: default;
	}
</style>
