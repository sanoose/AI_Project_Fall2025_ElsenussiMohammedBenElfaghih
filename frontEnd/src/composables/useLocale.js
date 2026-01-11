import { ref, watch } from 'vue'
import translations from '../locales/index.json'

export function useLocale() {
  const locale = ref(localStorage.getItem('locale') || 'en')
  
  const t = (key) => {
    const keys = key.split('.')
    let value = translations[locale.value]
    
    for (const k of keys) {
      if (value && value[k] !== undefined) {
        value = value[k]
      } else {
        return key
      }
    }
    return value
  }
  
  const setLocale = (newLocale) => {
    locale.value = newLocale
    localStorage.setItem('locale', newLocale)
  }
  
  const toggleLocale = () => {
    setLocale(locale.value === 'en' ? 'ar' : 'en')
  }
  
  return {
    locale,
    t,
    setLocale,
    toggleLocale
  }
}