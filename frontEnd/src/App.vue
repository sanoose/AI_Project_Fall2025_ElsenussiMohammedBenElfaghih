<template>
  <div class="app-container" :dir="locale === 'ar' ? 'rtl' : 'ltr'">
    <!-- خلفية مضيئة متدرجة -->
    <div class="background-glow">
      <div class="glow-circle glow-1"></div>
      <div class="glow-circle glow-2"></div>
      <div class="glow-circle glow-3"></div>
    </div>

    <!-- شريط التنقل -->
    <nav class="navigation-bar">
      <div class="nav-inner">
        <!-- شعار -->
        <div class="logo-area">
          <div class="logo-symbol">
            <div class="logo-glow"></div>
            <svg viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" 
                    fill="currentColor"/>
            </svg>
          </div>
          <h1 class="logo-title">{{ t('appTitle') }}</h1>
        </div>

        <!-- تبديل اللغة -->
        <button @click="toggleLocale" class="language-toggle">
          <span class="toggle-text">{{ locale === 'en' ? '🇸🇦 العربية' : '🇺🇸 English' }}</span>
          <svg class="toggle-icon" viewBox="0 0 24 24">
            <path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/>
          </svg>
        </button>
      </div>
    </nav>

    <!-- المحتوى الرئيسي -->
    <main class="main-area">
      <!-- البطاقة الرئيسية -->
      <div class="main-card">
        <!-- شريط علوي متحرك -->
        <div class="card-top-animation"></div>
        
        <div class="card-body">
          <!-- العنوان الرئيسي -->
          <div class="hero-section">
            <h2 class="hero-title">{{ t('appTitle') }}</h2>
            <p class="hero-subtitle">{{ t('appSubtitle') }}</p>
          </div>

          <!-- منطقة إدخال النص -->
          <div class="input-container">
            <div class="input-header">
              <div class="input-dot"></div>
              <label class="input-label">{{ t('textInputLabel') }}</label>
            </div>
            
            <div class="text-area-wrapper">
              <textarea
                v-model="text"
                :placeholder="t('textInputPlaceholder')"
                rows="6"
                class="text-area"
                :class="{
                  'good-language': detected.lang === 'ar' || detected.lang === 'en',
                  'mixed-language': mixedError,
                  'typing-effect': text.trim() && !mixedError && !loading
                }"
                @input="onTextChange"
                :style="{ 
                  textAlign: locale === 'ar' ? 'right' : 'left',
                  direction: locale === 'ar' ? 'rtl' : 'ltr' 
                }"
              ></textarea>
              
              <!-- عداد الأحرف -->
              <div class="char-counter">{{ text.length }} {{ locale === 'ar' ? 'حرف' : 'chars' }}</div>
            </div>
          </div>

          <!-- كشف اللغة -->
          <div class="language-info">
            <div class="info-row">
              <!-- حالة الكشف -->
              <div class="detection-box">
                <span class="detection-title">{{ t('detectedLabel') }}</span>
                <div class="detection-badge" :class="langClass">
                  <span class="badge-text">{{ detectedLabelText }}</span>
                  <span v-if="counts" class="count-details">
                    ({{ locale === 'ar' ? 'عربي' : 'ar' }}: {{ counts.ar }}, {{ locale === 'ar' ? 'إنجليزي' : 'en' }}: {{ counts.en }})
                  </span>
                </div>
              </div>

                <div>
                        <!-- خيار Return Probs -->
              <label class="probs-toggle">
                <input type="checkbox" v-model="return_probs" class="toggle-checkbox" />
                <div class="toggle-slider">
                  <div class="toggle-button"></div>
                </div>
                <span class="toggle-label">{{ t('returnProbs') }}</span>
              </label>
              <br>
              <label class="probs-toggle">
                <input type="checkbox" v-model="return_explain" class="toggle-checkbox" />
                <div class="toggle-slider">
                  <div class="toggle-button"></div>
                </div>
                <span class="toggle-label">{{ t('returnExplain') }}</span>
              </label>
                </div>
            </div>

            <!-- رسالة خطأ اللغة المختلطة -->
            <div v-if="mixedError" class="warning-box shake">
              <div class="warning-icon">
                <svg viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                </svg>
              </div>
              <div class="warning-content">
                <h4 class="warning-title">{{ locale === 'ar' ? 'تنبيه!' : 'Warning!' }}</h4>
                <p class="warning-message">{{ t('mixedError') }}</p>
              </div>
            </div>
          </div>

          <!-- أزرار التحكم -->
          <div class="control-buttons">
            <!-- زر التنبؤ -->
            <button @click="predict" :disabled="btnDisabled" class="predict-button">
              <div class="button-glow"></div>
              <div class="button-content">
                <div v-if="loading" class="spinner"></div>
                <span class="button-text">
                  {{ loading ? t('predictingButton') : t('predictButton') }}
                </span>
                 <svg v-if="!loading" class="eyes" width="20" height="20" viewBox="0 0 24 24">
                <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
              </svg>
              </div>
            </button>

            <!-- زر المسح -->
            <button @click="clearAll" :disabled="loading" class="clear-button">
              <div class="button-content">
                <svg class="clear-icon" viewBox="0 0 24 24">
                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
                <span class="button-text">{{ t('clearButton') }}</span>
              </div>
            </button>
          </div>

          <!-- رسالة الخطأ -->
          <div v-if="error" class="error-container fade-in">
            <div class="error-icon">
              <svg viewBox="0 0 24 24">
                <path d="M11 15h2v2h-2zm0-8h2v6h-2zm.99-5C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/>
              </svg>
            </div>
            <div class="error-details">
              <h4 class="error-title">{{ locale === 'ar' ? 'خطأ في التحليل' : 'Analysis Error' }}</h4>
              <p class="error-message">{{ error }}</p>
            </div>
          </div>

          <!-- عرض النتائج -->
          <div v-if="result" class="results-container slide-up">
            <div class="results-header">
              <div class="results-icon">
                <svg viewBox="0 0 24 24">
                  <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z"/>
                  <path d="M7 12h2v5H7zm8-5h2v10h-2zm-4 7h2v3h-2zm0-4h2v2h-2z"/>
                </svg>
              </div>
              <h3 class="results-title">{{ locale === 'ar' ? 'نتائج التحليل' : 'Analysis Results' }}</h3>
            </div>

            <!-- بطاقات النتائج -->
            <div class="results-cards">
              <div class="result-card">
                <div class="card-header">
                  <svg class="card-icon" viewBox="0 0 24 24">
                    <path d="M12.87 15.07l-2.54-2.51.03-.03c1.74-1.94 2.98-4.17 3.71-6.53H17V4h-7V2H8v2H1v1.99h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04zM18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12zm-2.62 7l1.62-4.33L19.12 17h-3.24z"/>
                  </svg>
                  <span class="card-label">{{ t('language') }}</span>
                </div>
                <div class="card-value">
                  <span class="value-text">{{ result.lang.toUpperCase() }}</span>
                  <span class="value-flag">{{ result.lang === 'ar' ? '🇸🇦' : '🇺🇸' }}</span>
                </div>
              </div>

              <div class="result-card">
                <div class="card-header">
                  <svg class="card-icon" viewBox="0 0 24 24">
                    <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM7 10h2v7H7zm4-3h2v10h-2zm4-3h2v13h-2z"/>
                  </svg>
                  <span class="card-label">Label ID</span>
                </div>
                <div class="card-value" :class="result.label_id === 1 ? 'positive' : 'negative'">
                  <span class="value-text">{{ result.label_id }}</span>
                  <span class="value-emoji">{{ result.label_id === 1 ? '😊' : '😞' }}</span>
                </div>
              </div>

              <div class="result-card">
                <div class="card-header">
                  <svg class="card-icon" viewBox="0 0 24 24">
                    <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
                  </svg>
                  <span class="card-label">{{ t('confidence') }}</span>
                </div>
                <div class="confidence-display">
                  <span class="confidence-value">{{ (result.confidence * 100).toFixed(1) }}%</span>
                  <div class="confidence-bar">
                    <div class="confidence-fill" :style="{ width: `${result.confidence * 100}%` }"></div>
                  </div>
                </div>
              </div>

              <div class="result-card">
                <div class="card-header">
                  <svg class="card-icon" viewBox="0 0 24 24">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                  </svg>
                  <span class="card-label">{{ t('display') }}</span>
                </div>
                <div class="card-value pulse" :class="result.label_id === 1 ? 'positive' : 'negative'">
                  <span class="value-text">{{ displayLabel(result.label_id) }}</span>
                  <span class="value-emoji">{{ result.label_id === 1 ? '🎉' : '📉' }}</span>
                </div>
              </div>
            </div>

            <!-- النتائج الخام -->
            <details class="raw-results">
              <summary class="raw-summary">
                <div class="summary-content">
                  <svg class="summary-icon" viewBox="0 0 24 24">
                    <path d="M9.4 16.6L4.8 12l4.6-4.6L8 6l-6 6 6 6 1.4-1.4zm5.2 0l4.6-4.6-4.6-4.6L16 6l6 6-6 6-1.4-1.4z"/>
                  </svg>
                  <span>{{ t('rawResponse') }}</span>
                </div>
                <div class="json-tag">JSON</div>
              </summary>
              <div class="raw-content">
                <pre>{{ JSON.stringify(result, null, 2) }}</pre>
              </div>
            </details>


          </div>
        </div>
      </div>

      <!-- التذييل -->
      <footer class="page-footer">
        <div class="legend">
          <div class="legend-item">
            <div class="legend-dot negative-dot"></div>
            <span>0 = {{ t('negative') }}</span>
          </div>
          <div class="divider"></div>
          <div class="legend-item">
            <div class="legend-dot positive-dot"></div>
            <span>1 = {{ t('positive') }}</span>
          </div>
        </div>
        <p class="footer-text">AI Sentiment Analysis © {{ new Date().getFullYear() }}</p>
      </footer>
    </main>

    <!-- مؤشرات التحميل المتحركة -->
    <div class="loading-indicators">
      <div class="loading-dot dot-1"></div>
      <div class="loading-dot dot-2"></div>
      <div class="loading-dot dot-3"></div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { useLocale } from "./composables/useLocale";

const { locale, t, toggleLocale } = useLocale();

const API_BASE = "http://127.0.0.1:8000";
const text = ref("");
const loading = ref(false);
const error = ref("");
const result = ref(null);
const return_probs = ref(false);
const return_explain = ref(false);
const detected = ref({ lang: "unknown", ar: 0, en: 0 });

function detectLang(text) {
  let ar = 0;
  let en = 0;

  for (const ch of text) {
    const code = ch.codePointAt(0);
    const isArabic =
      (code >= 0x0600 && code <= 0x06ff) ||
      (code >= 0x0750 && code <= 0x077f) ||
      (code >= 0x08a0 && code <= 0x08ff) ||
      (code >= 0xfb50 && code <= 0xfdff) ||
      (code >= 0xfe70 && code <= 0xfeff);
    const isLatin =
      (code >= 0x0041 && code <= 0x005a) ||
      (code >= 0x0061 && code <= 0x007a);

    if (isArabic) ar++;
    else if (isLatin) en++;
  }

  const letters = ar + en;
  if (letters === 0) return { lang: "unknown", ar, en };

  const arRatio = ar / letters;
  const enRatio = en / letters;

  if (arRatio >= 0.8) return { lang: "ar", ar, en };
  if (enRatio >= 0.8) return { lang: "en", ar, en };
  if (ar > 0 && en > 0) return { lang: "mixed", ar, en };

  return ar > en ? { lang: "ar", ar, en } : { lang: "en", ar, en };
}

function onTextChange() {
  detected.value = detectLang(text.value);
  result.value = null;
  error.value = "";
}

const mixedError = computed(() => detected.value.lang === "mixed");

const counts = computed(() => {
  const { ar, en } = detected.value;
  return ar + en > 0 ? { ar, en } : null;
});

const detectedLabelText = computed(() => {
  const langMap = {
    'ar': t('arabic'),
    'en': t('english'),
    'mixed': t('mixed'),
    'unknown': t('unknown')
  };
  return langMap[detected.value.lang] || t('unknown');
});

const langClass = computed(() => {
  if (detected.value.lang === "ar" || detected.value.lang === "en") return "good";
  if (detected.value.lang === "mixed") return "bad";
  return "neutral";
});

const btnDisabled = computed(() => {
  if (loading.value) return true;
  if (!text.value.trim()) return true;
  if (mixedError.value) return true;
  if (detected.value.lang === "unknown") return true;
  return false;
});

function displayLabel(labelId) {
  return labelId === 1 ? t('positive') : t('negative');
}

async function predict() {
  loading.value = true;
  error.value = "";
  result.value = null;

  try {
    console.log(return_explain.value);
    console.log(return_probs.value );
    
    const lang = detected.value.lang;
    const res = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: text.value,
        lang,
        return_probs: return_probs.value,
        return_explain : return_explain.value  , 
        top_k: 10  
      }),
    });

    if (!res.ok) {
      const msg = await res.text();
      throw new Error(msg || `HTTP ${res.status}`);
    }

    result.value = await res.json();
    console.log(    result.value  );
    
  } catch (e) {
    console.log(e);
    
    error.value = e?.message || String(e);
  } finally {
    loading.value = false;
  }
}

function clearAll() {
  text.value = "";
  detected.value = { lang: "unknown", ar: 0, en: 0 };
  result.value = null;
  error.value = "";
}
</script>

<style scoped>
/* CSS متكامل مع ألوان متناسقة وتوجيه نص */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
}

body {
  background: #f8fafc;
  color: #1e293b;
  overflow-x: hidden;
}

/* الأنيميشن */
@keyframes gradientMove {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes typing {
  0%, 100% { border-color: #e2e8f0; }
  50% { border-color: #3b82f6; }
}

/* الحاوية الرئيسية */
.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  position: relative;
}

/* خلفية مضيئة */
.background-glow {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
}

.glow-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
}

.glow-1 {
  top: 10%;
  right: 10%;
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #60a5fa, #3b82f6);
  animation: pulse 4s infinite;
}

.glow-2 {
  bottom: 20%;
  left: 10%;
  width: 250px;
  height: 250px;
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  animation: pulse 5s infinite 0.5s;
}

.glow-3 {
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #10b981, #059669);
  animation: pulse 6s infinite 1s;
}

/* شريط التنقل */
.navigation-bar {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #e2e8f0;
  padding: 1rem 2rem;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.nav-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-symbol {
  position: relative;
  width: 40px;
  height: 40px;
}

.logo-glow {
  position: absolute;
  inset: -2px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border-radius: 12px;
  filter: blur(8px);
  opacity: 0.5;
}

.logo-symbol svg {
  position: relative;
  width: 100%;
  height: 100%;
  color: #3b82f6;
}

.logo-title {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #1e40af, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* زر تبديل اللغة */
.language-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  color: #475569;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.language-toggle:hover {
  background: #f8fafc;
  border-color: #3b82f6;
  color: #3b82f6;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.1);
}

.toggle-icon {
  width: 16px;
  height: 16px;
  transition: transform 0.3s ease;
}

.language-toggle:hover .toggle-icon {
  transform: rotate(180deg);
}

/* المحتوى الرئيسي */
.main-area {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  position: relative;
  z-index: 1;
}

.main-card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.card-top-animation {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, 
    #3b82f6, 
    #8b5cf6, 
    #ec4899, 
    #f59e0b, 
    #10b981, 
    #3b82f6);
  background-size: 200% 100%;
  animation: gradientMove 3s linear infinite;
}

.card-body {
  padding: 2.5rem;
}

/* العنوان الرئيسي */
.hero-section {
  text-align: center;
  margin-bottom: 2.5rem;
}

.hero-title {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #1e40af, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.75rem;
  line-height: 1.2;
}

.hero-subtitle {
  color: #64748b;
  font-size: 1.125rem;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

/* منطقة إدخال النص */
.input-container {
  margin-bottom: 2rem;
}

.input-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.input-dot {
  width: 8px;
  height: 8px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.input-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.text-area-wrapper {
  position: relative;
}

.text-area {
  width: 100%;
  padding: 1.25rem;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  color: #1e293b;
  font-size: 1rem;
  line-height: 1.6;
  resize: vertical;
  transition: all 0.3s ease;
  font-family: inherit;
}

.text-area:focus {
  outline: none;
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.text-area::placeholder {
  color: #94a3b8;
}

.text-area.good-language {
  border-color: #10b981;
}

.text-area.mixed-language {
  border-color: #ef4444;
}

.text-area.typing-effect {
  animation: typing 1.5s infinite;
}

.char-counter {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  background: rgba(255, 255, 255, 0.9);
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

/* RTL دعم للعربية */
[dir="rtl"] .char-counter {
  right: auto;
  left: 1rem;
}

/* معلومات اللغة */
.language-info {
  margin-bottom: 2rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.detection-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.detection-title {
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
}

.detection-badge {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.detection-badge.good {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.detection-badge.bad {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
  animation: shake 0.5s ease-in-out;
}

.detection-badge.neutral {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
}

.count-details {
  font-size: 0.75rem;
  opacity: 0.8;
}

/* تبديل Return Probs */
.probs-toggle {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
}

.toggle-checkbox {
  display: none;
}

.toggle-slider {
  width: 48px;
  height: 24px;
  background: #e2e8f0;
  border-radius: 12px;
  position: relative;
  transition: all 0.3s ease;
}

.toggle-checkbox:checked + .toggle-slider {
  background: #3b82f6;
}

.toggle-button {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.toggle-checkbox:checked + .toggle-slider .toggle-button {
  left: 26px;
}

.toggle-label {
  font-size: 0.875rem;
  color: #475569;
  font-weight: 500;
}

/* صندوق التحذير */
.warning-box {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.25rem;
  background: linear-gradient(135deg, #fef3c7, #fef3c7);
  border: 1px solid #f59e0b;
  border-radius: 12px;
}

.warning-box.shake {
  animation: shake 0.5s ease-in-out;
}

.warning-icon {
  width: 24px;
  height: 24px;
  color: #d97706;
  flex-shrink: 0;
}

.warning-icon svg {
  width: 100%;
  height: 100%;
}

.warning-content {
  flex: 1;
}

.warning-title {
  font-size: 1rem;
  font-weight: 600;
  color: #92400e;
  margin-bottom: 0.25rem;
}

.warning-message {
  font-size: 0.875rem;
  color: #92400e;
  line-height: 1.5;
}

/* أزرار التحكم */
.control-buttons {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  justify-content: space-between;
}

.predict-button {
  position: relative;
  /* flex: 1; */
  border: none;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  min-height: 56px;
  height: 36px;
  width: 150px !important;
}

.predict-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.button-glow {
  position: absolute;
  inset: -2px;
  background: linear-gradient(90deg, 
    #3b82f6, 
    #8b5cf6, 
    #ec4899, 
    #f59e0b, 
    #10b981, 
    #3b82f6);
  background-size: 200% 100%;
  border-radius: 14px;
  animation: gradientMove 3s linear infinite;
  opacity: 0.5;
  filter: blur(4px);
}

.button-content {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #3b82f6, #be1b1b);
  /* background: linear-gradient(135deg, #3b82f6, #2563eb); */
  border-radius: 12px;
  height: 100%;
}

.predict-button:not(:disabled):hover .button-content {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  transform: translateY(-2px);
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid white;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.button-text {
  font-size: 1rem;
  font-weight: 600;
  color: white;
}

.arrow {
  width: 20px;
  height: 20px;
  color: white;
}

.clear-button {
  padding: 1rem 2rem;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  color: #475569;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.clear-button:not(:disabled):hover {
  background: #f8fafc;
  border-color: #94a3b8;
  color: #1e293b;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.clear-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.clear-icon {
  width: 20px;
  height: 20px;
  color: #64748b;
}

/* رسالة الخطأ */
.error-container {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.25rem;
  background: linear-gradient(135deg, #fee2e2, #fee2e2);
  border: 1px solid #ef4444;
  border-radius: 12px;
  margin-bottom: 2rem;
  animation: fadeIn 0.3s ease-out;
}

.error-icon {
  width: 24px;
  height: 24px;
  color: #dc2626;
  flex-shrink: 0;
}

.error-icon svg {
  width: 100%;
  height: 100%;
}

.error-details {
  flex: 1;
}

.error-title {
  font-size: 1rem;
  font-weight: 600;
  color: #991b1b;
  margin-bottom: 0.25rem;
}

.error-message {
  font-size: 0.875rem;
  color: #991b1b;
  line-height: 1.5;
  white-space: pre-wrap;
}

/* عرض النتائج */
.results-container {
  background: linear-gradient(135deg, #f8fafc, #ffffff);
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 2rem;
  animation: slideUp 0.5s ease-out;
  position: relative;
  overflow: hidden;
}

.results-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #10b981, #3b82f6);
}

.results-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.results-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #10b981, #3b82f6);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.results-icon svg {
  width: 24px;
  height: 24px;
  color: white;
}

.results-title {
  font-size: 1.75rem;
  font-weight: 700;
  background: linear-gradient(135deg, #10b981, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* بطاقات النتائج */
.results-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.result-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.result-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  border-color: #3b82f6;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.card-icon {
  width: 20px;
  height: 20px;
  color: #64748b;
}

.card-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.card-value {
  font-size: 1.5rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.card-value.positive {
  color: #10b981;
}

.card-value.negative {
  color: #ef4444;
}

.card-value.pulse {
  animation: pulse 2s infinite;
}

.value-text {
  font-weight: 800;
}

.value-flag, .value-emoji {
  font-size: 1.25rem;
}

.confidence-display {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.confidence-value {
  font-size: 1.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #10b981, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.confidence-bar {
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #3b82f6);
  border-radius: 3px;
  transition: width 1s ease-out;
}

/* النتائج الخام */
.raw-results {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}

.raw-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: white;
  cursor: pointer;
  list-style: none;
  transition: all 0.3s ease;
}

.raw-summary:hover {
  background: #f8fafc;
}

.raw-summary::-webkit-details-marker {
  display: none;
}

.summary-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.summary-icon {
  width: 16px;
  height: 16px;
  color: #64748b;
  transition: transform 0.3s ease;
}

.raw-results[open] .summary-icon {
  transform: rotate(90deg);
}

.raw-summary span {
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
}

.json-tag {
  padding: 0.25rem 0.75rem;
  background: #e2e8f0;
  border-radius: 6px;
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
}

.raw-content {
  padding: 1.5rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  max-height: 300px;
  overflow: auto;
}

.raw-content pre {
  font-family: 'SF Mono', Monaco, Consolas, monospace;
  font-size: 0.75rem;
  color: #475569;
  line-height: 1.6;
  white-space: pre-wrap;
}

.raw-content::-webkit-scrollbar {
  width: 8px;
}

.raw-content::-webkit-scrollbar-track {
  background: #e2e8f0;
  border-radius: 4px;
}

.raw-content::-webkit-scrollbar-thumb {
  background: #94a3b8;
  border-radius: 4px;
}

.raw-content::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}

/* التذييل */
.page-footer {
  text-align: center;
  margin-top: 3rem;
}

.legend {
  display: inline-flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1.5rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  margin-bottom: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.negative-dot {
  background: #ef4444;
  animation: pulse 2s infinite;
}

.positive-dot {
  background: #10b981;
  animation: pulse 2s infinite 0.5s;
}

.legend-item span {
  font-size: 0.875rem;
  color: #475569;
  font-weight: 500;
}

.divider {
  width: 1px;
  height: 16px;
  background: #e2e8f0;
}

.footer-text {
  font-size: 0.875rem;
  color: #94a3b8;
}

/* مؤشرات التحميل */
.loading-indicators {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  z-index: 50;
}

.loading-dot {
  width: 6px;
  height: 6px;
  background: #3b82f6;
  border-radius: 50%;
}

.dot-1 {
  animation: bounce 1s infinite;
}

.dot-2 {
  animation: bounce 1s infinite 0.2s;
}

.dot-3 {
  animation: bounce 1s infinite 0.4s;
}

/* تصميم متجاوب */
@media (max-width: 768px) {
  .main-area {
    padding: 1rem;
  }
  
  .card-body {
    padding: 1.5rem;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .results-cards {
    grid-template-columns: 1fr;
  }
  
  .control-buttons {
    flex-direction: column;
  }
  
  .info-row {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .navigation-bar {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 1.75rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .card-body {
    padding: 1rem;
  }
  
  .predict-button, .clear-button {
    min-height: 48px;
    font-size: 0.875rem;
  }
  
  .results-title {
    font-size: 1.5rem;
  }
}
</style>