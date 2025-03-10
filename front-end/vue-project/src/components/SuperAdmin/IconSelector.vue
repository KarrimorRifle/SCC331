<template>
  <div class="icon-selector">
    <!-- Search Input -->
    <input
      type="text"
      v-model="searchText"
      placeholder="Search icons..."
      class="search-input"
      @input="handleSearch"
    />

    <!-- Icon Grid with Lazy Loading -->
    <div class="icon-grid" ref="iconGrid" @scroll="handleScroll">
      <div
        v-for="iconDef in visibleIcons"
        :key="iconDef.iconName"
        class="icon-option"
        @click="selectIcon(iconDef.iconName)"
      >
        <FontAwesomeIcon :icon="['fas', iconDef.iconName]" class="icon-preview" />
        <span>{{ iconDef.iconName }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { library } from '@fortawesome/fontawesome-svg-core';
import { fas } from '@fortawesome/free-solid-svg-icons';
library.add(fas);

// Extract all solid icons, filtering out non-icon exports like "fas"
const allIcons = Object.keys(fas)
  .filter(key => key.startsWith("fa") && key !== "fas")
  .map(key => fas[key])
  .filter(iconDef => iconDef && iconDef.prefix === 'fas');

const searchText = ref('');
const iconGrid = ref<HTMLElement | null>(null);
const itemsPerLoad = 50; // Load icons in batches
const visibleIcons = ref(allIcons.slice(0, itemsPerLoad));

/**
 * Function to load more icons when scrolling down
 */
const handleScroll = () => {
  if (!iconGrid.value) return;
  const { scrollTop, scrollHeight, clientHeight } = iconGrid.value;

  if (scrollTop + clientHeight >= scrollHeight - 10) {
    loadMoreIcons();
  }
};

/**
 * Function to load more icons
 */
const loadMoreIcons = () => {
  if (visibleIcons.value.length < allIcons.length) {
    const nextBatch = allIcons.slice(visibleIcons.value.length, visibleIcons.value.length + itemsPerLoad);
    visibleIcons.value.push(...nextBatch);
  }
};

/**
 * Function to handle search input with debounce
 */
const handleSearch = () => {
  nextTick(() => {
    const query = searchText.value.toLowerCase();

    // ✅ Reset the visible icons completely before adding new results
    visibleIcons.value = [];

    if (!query) {
      // ✅ If search is cleared, show default initial icons
      visibleIcons.value = [...allIcons.slice(0, itemsPerLoad)];
    } else {
      // ✅ Filter the icons and reset the list instead of appending
      const filtered = allIcons.filter(iconDef => iconDef.iconName.includes(query));
      visibleIcons.value = filtered.slice(0, itemsPerLoad);
    }
  });
};


const emit = defineEmits(['iconSelected']);

function selectIcon(iconName: string) {
  emit('iconSelected', iconName);
}
</script>

<style scoped>
.icon-selector {
  text-align: center;
  padding: 1rem;
}

.search-input {
  width: 100%;
  max-width: 300px;
  padding: 0.5rem;
  margin-bottom: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  gap: 0.5rem;
  justify-content: center;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #ccc;
  color: var(--primary-dark-text);
  padding: 0.5rem;
}

.icon-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 5px;
  cursor: pointer;
  width: 80px;
}

.icon-option:hover {
  background: var(--primary-light-bg-hover);
}

.icon-preview {
  font-size: 1.5rem;
}

.icon-option span {
  font-size: 0.7rem;
  margin-top: 0.3rem;
}
</style>
