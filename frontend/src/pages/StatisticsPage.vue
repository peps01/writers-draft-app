<template>
  <q-layout>
    <q-page-container>
      <q-page>
        <div class="wda-page" style="max-width: 900px">
          <div
            style="
              display: flex;
              align-items: center;
              justify-content: space-between;
              margin-bottom: 16px;
            "
          >
            <q-btn
              flat
              icon="arrow_back"
              label="Back to Project"
              :to="`/projects/${projectId}`"
              no-caps
              style="
                font-family: var(--wda-font-ui);
                font-size: 0.85rem;
                color: var(--wda-text-muted);
              "
            />
            <q-btn
              flat
              round
              :icon="$q.dark.isActive ? 'light_mode' : 'dark_mode'"
              @click="$q.dark.toggle()"
              size="sm"
            />
          </div>

          <div class="wda-page-title">Writing Statistics</div>
          <div class="wda-page-subtitle">Track your progress and stay motivated</div>

          <div v-if="store.loading" class="text-center q-mt-xl">
            <q-spinner size="lg" color="primary" />
          </div>

          <div v-else-if="store.error" class="empty-state">
            <q-icon name="error_outline" size="3rem" style="color: var(--wda-text-muted)" />
            <p class="empty-state-title">Could not load statistics</p>
            <p class="empty-state-desc">{{ store.error }}</p>
          </div>

          <template v-else-if="store.stats">
            <!-- Summary cards -->
            <div class="row q-col-gutter-md q-mb-lg">
              <div class="col-6 col-sm-3">
                <div class="stat-card">
                  <div class="stat-number">{{ formatNumber(store.stats.total_words) }}</div>
                  <div class="stat-label">Total Words</div>
                </div>
              </div>
              <div class="col-6 col-sm-3">
                <div class="stat-card">
                  <div class="stat-number">{{ store.stats.total_scenes }}</div>
                  <div class="stat-label">Total Scenes</div>
                </div>
              </div>
              <div class="col-6 col-sm-3">
                <div class="stat-card">
                  <div class="stat-number streak-number">
                    {{ store.stats.writing_streak }}
                    <q-icon
                      v-if="store.stats.writing_streak > 0"
                      name="whatshot"
                      color="orange"
                      size="sm"
                    />
                  </div>
                  <div class="stat-label">Writing Streak</div>
                </div>
              </div>
              <div class="col-6 col-sm-3">
                <div class="stat-card">
                  <div class="stat-number">{{ store.stats.total_days_written }}</div>
                  <div class="stat-label">Days Written</div>
                </div>
              </div>
            </div>

            <!-- Daily word goal section -->
            <div v-if="authStore.showWordGoal" class="wda-card q-mb-lg" style="padding: 24px">
              <div
                style="
                  font-family: var(--wda-font-heading);
                  font-size: 1.1rem;
                  font-weight: 600;
                  margin-bottom: 12px;
                "
              >
                Today's Progress
              </div>
              <div
                v-if="todayWords === null"
                style="color: var(--wda-text-muted); font-size: 0.85rem"
              >
                No writing data yet for today.
              </div>
              <template v-else>
                <div class="row items-center q-mb-sm">
                  <div class="col">
                    <div style="font-size: 0.9rem">
                      <template v-if="todayWords >= goalTarget">
                        <q-icon name="check_circle" color="positive" size="sm" class="q-mr-xs" />
                        <span style="color: var(--wda-positive)">Goal reached!</span>
                        {{ formatNumber(todayWords) }} / {{ formatNumber(goalTarget) }} words.
                      </template>
                      <template v-else> Goal: {{ formatNumber(goalTarget) }} words/day </template>
                    </div>
                  </div>
                  <div class="col-auto text-caption" style="color: var(--wda-text-muted)">
                    {{ formatNumber(todayWords) }} / {{ formatNumber(goalTarget) }} words today
                  </div>
                </div>
                <q-linear-progress
                  :value="goalProgress"
                  color="primary"
                  track-color="grey-3"
                  size="20px"
                  class="q-mb-sm"
                >
                  <div class="absolute-full flex flex-center text-caption text-weight-bold">
                    {{ Math.round(goalProgress * 100) }}%
                  </div>
                </q-linear-progress>
                <div style="color: var(--wda-text-muted); font-size: 0.8rem">
                  <router-link to="/settings">Change goal or turn off in Settings.</router-link>
                </div>
              </template>
            </div>

            <!-- Words per day chart -->
            <div class="wda-card q-mb-lg" style="padding: 24px">
              <div
                style="
                  font-family: var(--wda-font-heading);
                  font-size: 1.1rem;
                  font-weight: 600;
                  margin-bottom: 16px;
                "
              >
                Words per Day
              </div>
              <div v-if="!hasData" class="empty-state">
                <q-icon name="bar_chart" size="2.5rem" style="color: var(--wda-text-muted)" />
                <p class="empty-state-title">No data yet</p>
                <p class="empty-state-desc">Start writing to see your stats here.</p>
              </div>
              <div v-else>
                <div style="position: relative; height: 250px; width: 100%">
                  <canvas ref="chartCanvas"></canvas>
                </div>
                <div
                  style="
                    color: var(--wda-text-muted);
                    font-size: 0.75rem;
                    text-align: center;
                    margin-top: 8px;
                  "
                >
                  Dates shown in UTC.
                </div>
              </div>
            </div>

            <!-- Longest and shortest scenes -->
            <div class="row q-col-gutter-md">
              <div class="col-12 col-sm-6">
                <div class="wda-card" style="padding: 24px">
                  <div style="font-size: 0.8rem; color: var(--wda-text-muted); margin-bottom: 8px">
                    Longest scene
                  </div>
                  <div v-if="store.stats.longest_scene">
                    <router-link
                      :to="`/projects/${projectId}/write`"
                      style="
                        font-size: 1rem;
                        color: var(--wda-primary);
                        font-family: var(--wda-font-heading);
                      "
                    >
                      {{ store.stats.longest_scene.title }}
                      <q-icon name="open_in_new" size="sm" class="q-ml-xs" />
                    </router-link>
                    <div style="font-size: 0.8rem; color: var(--wda-text-muted); margin-top: 4px">
                      {{ formatNumber(store.stats.longest_scene.word_count) }} words
                    </div>
                  </div>
                  <div v-else style="color: var(--wda-text-muted); font-size: 0.85rem">
                    No scenes yet.
                  </div>
                </div>
              </div>
              <div class="col-12 col-sm-6">
                <div class="wda-card" style="padding: 24px">
                  <div style="font-size: 0.8rem; color: var(--wda-text-muted); margin-bottom: 8px">
                    Shortest scene
                  </div>
                  <div v-if="store.stats.shortest_scene">
                    <router-link
                      :to="`/projects/${projectId}/write`"
                      style="
                        font-size: 1rem;
                        color: var(--wda-primary);
                        font-family: var(--wda-font-heading);
                      "
                    >
                      {{ store.stats.shortest_scene.title }}
                      <q-icon name="open_in_new" size="sm" class="q-ml-xs" />
                    </router-link>
                    <div style="font-size: 0.8rem; color: var(--wda-text-muted); margin-top: 4px">
                      {{ formatNumber(store.stats.shortest_scene.word_count) }} words
                    </div>
                  </div>
                  <div v-else style="color: var(--wda-text-muted); font-size: 0.85rem">
                    No scenes yet.
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useStatisticsStore } from '@/stores/statistics'
import { useAuthStore } from '@/stores/auth'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const route = useRoute()
const projectId = route.params.id
const store = useStatisticsStore()
const authStore = useAuthStore()

const chartCanvas = ref(null)
let chartInstance = null

const todayWords = computed(() => {
  if (!store.stats?.daily_words) return null
  const todayStr = new Date().toISOString().slice(0, 10)
  const entry = store.stats.daily_words.find((d) => d.date === todayStr)
  return entry ? entry.words : 0
})

const goalTarget = computed(() => authStore.dailyWordGoal || 1000)

const goalProgress = computed(() => {
  if (!todayWords.value || !goalTarget.value) return 0
  return Math.min(1, todayWords.value / goalTarget.value)
})

const hasData = computed(() => {
  if (!store.stats?.daily_words) return false
  return store.stats.daily_words.some((d) => d.words > 0)
})

function formatNumber(n) {
  if (n == null) return '0'
  return n.toLocaleString()
}

function buildChart() {
  if (!chartCanvas.value || !store.stats?.daily_words) return

  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }

  const data = store.stats.daily_words
  const labels = data.map((d) => d.date)
  const values = data.map((d) => d.words)

  const monthLabels = labels.map((label, i) => {
    const date = new Date(label + 'T00:00:00Z')
    if (date.getUTCDate() === 1) {
      return date.toLocaleDateString('en-US', { month: 'short', timeZone: 'UTC' })
    }
    if (i === 0) {
      return date.toLocaleDateString('en-US', { month: 'short', timeZone: 'UTC' })
    }
    return ''
  })

  const primaryColor =
    getComputedStyle(document.documentElement).getPropertyValue('--wda-primary').trim() || '#1B3A6B'

  chartInstance = new Chart(chartCanvas.value, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          data: values,
          backgroundColor: values.map((v) => (v > 0 ? primaryColor : '#E0E0E0')),
          borderWidth: 0,
          borderRadius: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title: (items) => items[0].label,
            label: (item) => `${item.parsed.y} words`,
          },
        },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: {
            maxRotation: 0,
            callback: (val, idx) => monthLabels[idx] || '',
          },
        },
        y: {
          beginAtZero: true,
          grid: { color: '#F0F0F0' },
          ticks: {
            callback: (val) => formatNumber(val),
          },
        },
      },
    },
  })
}

watch(
  () => store.stats,
  () => {
    if (store.stats?.daily_words) {
      nextTick(buildChart)
    }
  },
)

onMounted(async () => {
  await store.fetchStatistics(projectId)
  if (store.stats?.daily_words) {
    await nextTick()
    buildChart()
  }
})
</script>
