import { ref } from 'vue';
import axios from 'axios';
import {
  faPlaneDeparture,
  faShieldAlt,
  faMapMarkedAlt,
  faBell,
  faClock,
  faShoppingCart
} from '@fortawesome/free-solid-svg-icons';
import { dom } from '@fortawesome/fontawesome-svg-core';

// --- Default Domain Configuration ---
// This is the format expected by your API.
export const defaultDomainConfig = {
  config: {
    domain: 'default', // or "supermarket"
    loginText: 'Login to Monitor',
    hero: {
      title: 'Newcastle Airport Monitoring',
      subtitle:
        'Ensuring seamless airport operations with real-time monitoring of security, occupancy, and environmental conditions.',
      image: {
        name: 'newcastle-airport-image.webp',
        data: '' // BASE64 placeholder; if you have one, insert it here.
      }
    }
  },
  features: [
    {
      icon: 'shield', // String identifier to be mapped later
      title: 'Security Alerts',
      description: 'Get notified of any security breaches in real-time.'
    },
    {
      icon: 'map',
      title: 'Live Airport Map',
      description: 'Monitor passenger flow and track luggage locations.'
    },
    {
      icon: 'bell',
      title: 'Instant Notifications',
      description: 'Receive alerts for emergency and unusual activities.'
    },
    {
      icon: 'clock',
      title: '24/7 Monitoring',
      description: 'Track airport conditions anytime, anywhere.'
    }
  ],
  howItWorks: [
    { step: 1, title: 'Login', description: 'Access the system securely.' },
    { step: 2, title: 'Monitor', description: 'Track security, environmental data, and passenger flow in real-time.' },
    { step: 3, title: 'Receive Alerts', description: 'Get instant updates on critical situations.' }
  ],
  theme: {
    primaryDarkBg: '#003865',
    primaryDarkText: '#003865',
    primarySecondaryBg: 'lightgray',
    primarySecondaryText: 'lightgray',
    primaryLightBg: 'white',
    primaryLightText: 'white',
    accent: '#FFD700',
    accentHover: '#E6C200'
  }
};

// A reactive variable to hold the current configuration.
export const domainConfig = ref(defaultDomainConfig);

// --- Fetching the Domain Configuration from Backend ---
// This function fetches the config (which follows the API format) and then maps string icon identifiers
// to actual FontAwesome icon objects for use in the UI.
export async function fetchDomainConfig() {
  try {
    const response = await axios.get('http://localhost:5010/home', { withCredentials: true });
    if (response.status === 200 && response.data) {
      const fetchedConfig = response.data;

      // Mapping from string to FontAwesome icon
      const iconMapping: Record<string, any> = {
        shield: faShieldAlt,
        map: faMapMarkedAlt,
        bell: faBell,
        clock: faClock,
        plane: faPlaneDeparture,
        shoppingCart: faShoppingCart
      };
      
      // Map icons in features if they are strings.
      if (Array.isArray(fetchedConfig.features)) {
        fetchedConfig.features = fetchedConfig.features.map((feature: any) => ({
          ...feature,
          icon: typeof feature.icon === 'string' ? iconMapping[feature.icon] || feature.icon : feature.icon
        }));
      }
      
      // Merge fetched config with default (ensuring all keys are present)
      domainConfig.value = {
        config: { ...defaultDomainConfig.config, ...fetchedConfig.config },
        theme: { ...defaultDomainConfig.theme, ...fetchedConfig.theme },
        features: fetchedConfig.features || defaultDomainConfig.features,
        howItWorks: fetchedConfig.howItWorks || defaultDomainConfig.howItWorks
      };
    }
  } catch (error) {
    console.error('Error fetching domain config:', error);
  }
}

// --- Global Message State & Fetching Function ---
export const messages = ref<
  { message_id: number; sender_email: string; left_message: string; time_sent: string }[]
>([]);
export const showModal = ref(false);

export async function fetchMessages() {
  try {
    const response = await axios.get('http://localhost:5007/get_messages', {
      headers: {
        'session-id':
          document.cookie.split('; ').find(row => row.startsWith('session_id='))?.split('=')[1] || ''
      },
      withCredentials: true
    });
    if (response.data.messages && response.data.messages.length > 0) {
      messages.value = response.data.messages;
      showModal.value = true;
    } else {
      showModal.value = false;
    }
  } catch (error) {
    console.error('Error fetching messages:', error);
    showModal.value = false;
  }
}

// --- Utility: Get the Hero Icon Based on the Domain ---
export function getHeroIcon(domain: string) {
  return domain === 'Supermarket' ? faShoppingCart : faPlaneDeparture;
}
