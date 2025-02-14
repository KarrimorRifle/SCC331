<script setup lang="ts">
import { defineProps, computed } from 'vue';

const props = defineProps({
  movementArrows: {
    type: Array as () => { from: string; to: string }[],
    required: true,
  },
  areaPositions: {
    type: Object as () => Record<string, { x: number; y: number }>,
    required: true,
  },
});

const getArrowPosition = (from: string, to: string) => {
  const positions = props.areaPositions;
  if (!positions[from] || !positions[to]) return null;

  const start = positions[from];
  const end = positions[to];
  const offsetFactor = 0.3; // Adjust arrow length

  const dx = end.x - start.x;
  const dy = end.y - start.y;
  const distance = Math.sqrt(dx * dx + dy * dy);

  // Normalize vector and apply offset
  const normalizedDx = (dx / distance) * (distance * offsetFactor);
  const normalizedDy = (dy / distance) * (distance * offsetFactor);

  let x1 = start.x + normalizedDx;
  let y1 = start.y + normalizedDy;
  let x2 = end.x - normalizedDx;
  let y2 = end.y - normalizedDy;

  if (start.x === end.x) {
    x1 += 20;
    x2 += 20;
  }
  if (start.y === end.y) {
    y1 += 20;
    y2 += 20;
  }

  return { x1, y1, x2, y2 };
};
</script>

<template>
  <svg class="movement-arrows" viewBox="0 0 300 300">
    <line
      v-for="arrow in movementArrows"
      v-bind="getArrowPosition(arrow.from, arrow.to)"
      :key="`${arrow.from}-${arrow.to}`"
      stroke="black"
      stroke-width="1"
      marker-end="url(#arrowhead)"
    />
    <defs>
      <marker id="arrowhead" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
        <polygon points="0 0, 6 3, 0 6" fill="black" />
      </marker>
    </defs>
  </svg>
</template>

<style scoped>
.movement-arrows {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
}
</style>
