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

// --- Default Domain Configuration ---
// This object is used as the default. Later, it can be updated by fetching from the backend.
export const defaultDomainConfig = {
  domain: 'airport', // or "supermarket"
  heroTitle: 'Newcastle Airport Monitoring',
  heroSubtitle:
    'Ensuring seamless airport operations with real-time monitoring of security, occupancy, and environmental conditions.',
  loginText: 'Login to Monitor',
  heroImage: '/newcastle-airport-image.webp',
  features: [
    {
      icon: faShieldAlt,
      title: 'Security Alerts',
      description: 'Get notified of any security breaches in real-time.'
    },
    {
      icon: faMapMarkedAlt,
      title: 'Live Airport Map',
      description: 'Monitor passenger flow and track luggage locations.'
    },
    {
      icon: faBell,
      title: 'Instant Notifications',
      description: 'Receive alerts for emergency and unusual activities.'
    },
    {
      icon: faClock,
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
    primaryDarkBg: '#003865', // Dark Blue
    primaryDarkText: '#003865', 

    primarySecondaryBg: 'lightgray', // Dark Blue
    primarySecondaryText: 'lightgray', 

    primaryLightBg: 'white',
    primaryLightText: 'white',
    accent: '#FFD700', // Gold
    accentHover: "#E6C200" // Gold Hover
  }
};

// A reactive variable to hold the current configuration.
export const domainConfig = ref(defaultDomainConfig);

// --- Fetching the Domain Configuration from Backend ---
// Suppose the backend exposes an endpoint (e.g. GET /get_domain_config) that returns a config JSON.
// The backend might return icon identifiers as strings (e.g., "shield", "map", etc.) which then mapped.
export async function fetchDomainConfig() {
    try {
      const response = await axios.get('http://localhost:5010/home', { withCredentials: true });
      if (response.data.config) {
        const fetchedConfig = response.data.config;
  
        // Map icon identifier strings (if provided) to actual icon objects.
        const iconMapping: Record<string, any> = {
          shield: faShieldAlt,
          map: faMapMarkedAlt,
          bell: faBell,
          clock: faClock,
          plane: faPlaneDeparture,
          shoppingCart: faShoppingCart
        };
  
        if (Array.isArray(fetchedConfig.features)) {
          fetchedConfig.features = fetchedConfig.features.map((feature: any) => ({
            ...feature,
            icon: typeof feature.icon === 'string' ? iconMapping[feature.icon] || feature.icon : feature.icon
          }));
        }
  
        // Merge the fetched config with the default to ensure all keys are present.
        domainConfig.value = {
          ...defaultDomainConfig,
          ...fetchedConfig,
          theme: { ...defaultDomainConfig.theme, ...fetchedConfig.theme },
          features: fetchedConfig.features || defaultDomainConfig.features,
          howItWorks: fetchedConfig.howItWorks || defaultDomainConfig.howItWorks
        };
      }
    } catch (error) {
      const err = error as any;
      console.error('Error fetching domain config:', err.response?.data || err.message);
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
    const err = error as any;
    console.error('Error fetching messages:', err.response?.data || err.message);
    showModal.value = false;
  }
}

// --- Utility: Get the Hero Icon Based on the Domain ---
export function getHeroIcon(domain: string) {
  return domain === 'supermarket' ? faShoppingCart : faPlaneDeparture;
}
