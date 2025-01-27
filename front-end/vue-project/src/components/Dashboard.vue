<script setup lang="ts">
const props = defineProps({
  overlayAreas: {
    type: Array,
    required: true,
  },
});

const getTextColor = (color: string): string => {
  const hex = color.replace('#', '');
  const r = parseInt(hex.slice(0, 2), 16);
  const g = parseInt(hex.slice(2, 4), 16);
  const b = parseInt(hex.slice(4, 6), 16);
  const brightness = (r * 299 + g * 587 + b * 114) / 1000;
  return brightness < 128 ? 'white' : 'black';
};

</script>

<template>
  <div class="dashboard">
    <h2>Dashboard</h2>
    <div 
        v-for="(area, index) in props.overlayAreas" 
        :key="index" 
        class="dashboard-area"
        :style="{ backgroundColor: area.color, color: getTextColor(area.color)}"
        >
      <h3>{{ area.label }}</h3>
      <p>Luggage Count: {{ area.luggage?.length || 0 }}</p>
      <p>People Count: {{ area.people?.length || 0 }}</p>
      
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  width: 300px;
  padding: 20px;
  background-color: #f8f8ff;
  border-left: 1px solid #ccc;
  overflow-y: auto;
  box-shadow: -4px 0 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  color: black;
  font-weight: bold;
}

.dashboard-area {
  margin-bottom: 20px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.dashboard-area h3 {
  margin: 0;
  font-size: 18px;
  font-weight: bold;
  text-decoration: underline;
}

.dashboard-area p {
  margin: 5px 0;
  font-size: 14px;
}
</style>
