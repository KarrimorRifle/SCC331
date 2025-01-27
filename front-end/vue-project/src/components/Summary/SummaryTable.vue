<script setup lang="ts">
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
          <th>People Count</th>
          <th>Luggage Count</th>
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
</style>
