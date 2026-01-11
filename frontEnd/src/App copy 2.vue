<template>
  <main class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-4 md:p-8">
    <!-- Language Switcher -->
    <div class="flex justify-end mb-6">
      <button
        @click="toggleLocale"
        class="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50 transition-all duration-200"
      >
        <span class="text-sm font-medium text-gray-700">
          {{ locale === 'en' ? t('switchToArabic') : t('switchToEnglish') }}
        </span>
        <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
        </svg>
      </button>
    </div>

    <div class="max-w-2xl mx-auto" :dir="locale === 'ar' ? 'rtl' : 'ltr'">
      <!-- Header -->
      <header class="text-center mb-10">
        <h1 class="text-4xl font-bold text-gray-900 mb-3">
          {{ t('appTitle') }}
        </h1>
        <p class="text-gray-600 text-lg">
          {{ t('appSubtitle') }}
        </p>
      </header>

      <!-- Main Card -->
      <div class="bg-white rounded-2xl shadow-xl border border-gray-200 p-6 md:p-8">
        <!-- Text Input -->
        <div class="mb-6">
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            {{ t('textInputLabel') }}
          </label>
          <textarea
            v-model="text"
            :placeholder="t('textInputPlaceholder')"
            rows="6"
            class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 resize-none"
            :class="{
              'border-red-300': mixedError,
              'border-green-300': detected.lang === 'ar' || detected.lang === 'en'
            }"
            @input="onTextChange"
          />
        </div>

        <!-- Language Detection Status -->
        <div class="mb-6">
          <div class="flex flex-wrap items-center justify-between gap-4 mb-4">
            <div class="flex items-center gap-3">
              <span class="text-sm text-gray-600">{{ t('detectedLabel') }}</span>
              <span class="px-4 py-2 rounded-full text-sm font-medium"
                :class="{
                  'bg-green-100 text-green-800 border border-green-200': langClass === 'ok',
                  'bg-red-100 text-red-800 border border-red-200': langClass === 'bad',
                  'bg-gray-100 text-gray-800 border border-gray-200': langClass === 'neutral'
                }">
                <b>{{ detectedLabelText }}</b>
                <span v-if="counts" class="text-gray-600 ml-2">
                  (ar: {{ counts.ar }}, en: {{ counts.en }})
                </span>
              </span>
            </div>

            <label class="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                v-model="return_probs"
                class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700">{{ t('returnProbs') }}</span>
            </label>
          </div>

          <!-- Mixed Language Error -->
          <div
            v-if="mixedError"
            class="p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3"
          >
            <svg class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            <p class="text-sm text-red-700">{{ t('mixedError') }}</p>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-3 mb-6">
          <button
            @click="predict"
            :disabled="btnDisabled"
            class="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2"
          >
            <svg v-if="loading" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            {{ loading ? t('predictingButton') : t('predictButton') }}
          </button>
          
          <button
            @click="clearAll"
            :disabled="loading"
            class="px-6 py-3 border-2 border-gray-300 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            {{ t('clearButton') }}
          </button>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl">
          <p class="text-red-700 text-sm">{{ error }}</p>
        </div>

        <!-- Results Section -->
        <div v-if="result" class="mt-8 pt-8 border-t border-gray-200">
          <h3 class="text-xl font-bold text-gray-900 mb-6">Results</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div class="bg-gray-50 p-4 rounded-xl">
              <div class="text-sm text-gray-500 mb-1">{{ t('language') }}</div>
              <div class="font-semibold text-gray-900">{{ result.lang }}</div>
            </div>
            
            <div class="bg-gray-50 p-4 rounded-xl">
              <div class="text-sm text-gray-500 mb-1">label_id</div>
              <div class="font-semibold text-gray-900">{{ result.label_id }}</div>
            </div>
            
            <div class="bg-gray-50 p-4 rounded-xl">
              <div class="text-sm text-gray-500 mb-1">{{ t('confidence') }}</div>
              <div class="font-semibold text-gray-900">
                {{ (result.confidence * 100).toFixed(2) }}%
              </div>
            </div>
            
            <div class="bg-gray-50 p-4 rounded-xl">
              <div class="text-sm text-gray-500 mb-1">{{ t('display') }}</div>
              <div class="font-semibold" :class="{
                'text-green-600': result.label_id === 1,
                'text-red-600': result.label_id === 0
              }">
                {{ displayLabel(result.label_id) }}
              </div>
            </div>
          </div>

          <!-- Raw Response -->
          <details class="mt-6">
            <summary class="cursor-pointer text-blue-600 hover:text-blue-800 font-medium flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
              {{ t('rawResponse') }}
            </summary>
            <div class="mt-4 p-4 bg-gray-900 rounded-xl overflow-auto">
              <pre class="text-sm text-gray-200">{{ JSON.stringify(result, null, 2) }}</pre>
            </div>
          </details>
        </div>
      </div>

      <!-- Footer -->
      <footer class="mt-10 text-center text-gray-500 text-sm">
        <p>0 = {{ t('negative') }} | 1 = {{ t('positive') }}</p>
      </footer>
    </div>
  </main>
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
  if (detected.value.lang === "ar" || detected.value.lang === "en") return "ok";
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
    const lang = detected.value.lang;
    console.log("text.value  == " +  lang  );
    
    const res = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: text.value,
        lang,
        return_probs: return_probs.value,
      }),
    });

    if (!res.ok) {
      const msg = await res.text();
      throw new Error(msg || `HTTP ${res.status}`);
    }

    result.value = await res.json();
  } catch (e) {
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

<style>
/* RTL Support */
[dir="rtl"] .rtl-flip {
  transform: scaleX(-1);
}

/* Smooth transitions */
* {
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
 