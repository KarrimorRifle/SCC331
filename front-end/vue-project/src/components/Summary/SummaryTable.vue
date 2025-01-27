<script setup lang="ts">
import PersonMarker from '../ObjectMarker/PersonMarker.vue';
import LuggageMarker from '../ObjectMarker/LuggageMarker.vue';

const props = defineProps({
  areas: {
    type: Array,
    required: true,
  },
});
</script>

<template>
  <div class="summary-table">
    <table>
      <thead>
        <tr>
          <th>Area</th>
          <th>
            <div class="header-container">
              <div class="marker-wrapper">
                <PersonMarker :color="'#4caf50'" :position="{ top: 5, left: 0 }" />
              </div>
              People Count
            </div>
          </th>
          <th>
            <div class="header-container">
              <div class="marker-wrapper">
                <LuggageMarker :color="'#f44336'" :position="{ top: 5, left: 0 }" />
              </div>
              Luggage Count
            </div>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(area, index) in props.areas" :key="index">
          <td>{{ area.label }}</td>
          <td>{{ area.people?.length || 0 }}</td>
          <td>{{ area.luggage?.length || 0 }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.summary-table {
  padding: 20px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

th, td {
  padding: 10px;
  border: 1px solid #ccc;
  text-align: center;
}

th {
  background-color: #568ea6;
  color: white;
}

td {
  background-color: #f8f8ff;
  color: #333;
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative; /* Ensure markers stay positioned relative to this container */
}

.marker-wrapper {
  position: relative; /* Contains the absolutely positioned markers */
  width: 20px;
  height: 20px;
}
</style>
