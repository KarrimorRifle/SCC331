import { faUser, faClipboardCheck, faShieldAlt, faSuitcase, faQuestion, faChevronLeft, faChevronRight, faChevronUp, faChevronDown, faL } from '@fortawesome/free-solid-svg-icons';

// Add helper function to return icon mapping based on type using imported icons
export const getIcon = (type: string) => {
  switch (type.toLowerCase()) {
    case 'guard':
      return faShieldAlt;
    case 'luggage':
      return faSuitcase;
    case 'users':
    case 'user':
      return faUser;
    case 'staff':
      return faClipboardCheck;
    default:
      return faQuestion;
  }
};

// New helper to return color per role
export const getRoleColor = (type: string) => {
  switch (type.toLowerCase()) {
    case 'guard':
      return 'blue';
    case 'luggage':
      return 'grey';
    case 'users':
    case 'user':
      return 'darkblue';
    case 'staff':
      return 'green';
    default:
      return 'black';
  }
};
