<template>
  <q-page>
    <div class="wda-page wda-page--full">
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
              <q-icon name="edit_note" class="stat-icon" />
              <div class="stat-number">{{ formatNumber(store.stats.total_words) }}</div>
              <div class="stat-label">Total Words</div>
            </div>
          </div>
          <div class="col-6 col-sm-3">
            <div class="stat-card">
              <q-icon name="description" class="stat-icon" />
              <div class="stat-number">{{ store.stats.total_scenes }}</div>
              <div class="stat-label">Total Scenes</div>
            </div>
          </div>
          <div class="col-6 col-sm-3">
            <div class="stat-card">
              <q-icon name="local_fire_department" class="stat-icon" style="color: #E55A2B" />
              <div class="stat-number streak-number">
                {{ store.stats.writing_streak }}
              </div>
              <div class="stat-label">Writing Streak</div>
            </div>
          </div>
          <div class="col-6 col-sm-3">
            <div class="stat-card">
              <q-icon name="calendar_today" class="stat-icon" />
              <div class="stat-number">{{ store.stats.total_days_written }}</div>
              <div class="stat-label">Days Written</div>
            </div>
          </div>
        </div>

        <!-- Daily word goal section -->
        <div v-if="authStore.showWordGoal" class="progress-card q-mb-lg">
          <div style="font-family: var(--wda-font-heading); font-size: 1.1rem; font-weight: 600; margin-bottom: 12px;">
            Today's Progress
          </div>
          <div v-if="todayWords === null" style="color: var(--wda-text-muted); font-size: 0.85rem">
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
            <div class="progress-bar-container">
              <div class="progress-bar-fill" :style="{ width: Math.round(goalProgress * 100) + '%' }"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 4px; color: var(--wda-text-muted); font-size: 0.78rem;">
              <span>{{ Math.round(goalProgress * 100) }}% complete</span>
              <router-link to="/settings" style="color: var(--wda-action)">Change goal</router-link>
            </div>
          </template>
        </div>

        <!-- Words per day chart -->
        <div class="chart-card q-mb-lg">
          <div class="chart-header">
            <div>
              <h3 class="chart-title">Words per Day</h3>
              <p class="chart-subtitle">Last 90 days &middot; Dates in UTC</p>
            </div>
            <div class="chart-legend">
              <span class="legend-dot active"></span> Words written
              <span class="legend-dot zero"></span> No activity
            </div>
          </div>
          <div class="chart-body">
            <div v-if="!hasData" class="empty-state" style="padding: 20px 0">
              <q-icon name="bar_chart" size="2.5rem" style="color: var(--wda-text-muted)" />
              <p class="empty-state-title">No data yet</p>
              <p class="empty-state-desc">Start writing to see your stats here.</p>
            </div>
            <div v-else style="position: relative; height: 250px; width: 100%">
              <canvas ref="chartCanvas"></canvas>
            </div>
          </div>
        </div>

        <!-- Longest and shortest scenes -->
        <div class="scene-extreme-cards">
          <div v-if="store.stats.longest_scene" class="scene-extreme-card" @click="navigateToWrite">
            <div class="extreme-label">Longest scene</div>
            <div class="extreme-title">{{ store.stats.longest_scene.title }}</div>
            <div>
              <span class="extreme-count">{{ formatNumber(store.stats.longest_scene.word_count) }}</span>
              <span class="extreme-unit">words</span>
            </div>
          </div>
          <div v-else class="scene-extreme-card">
            <div class="extreme-label">Longest scene</div>
            <div style="color: var(--wda-text-muted); font-size: 0.85rem">No scenes yet.</div>
          </div>
          <div v-if="store.stats.shortest_scene" class="scene-extreme-card" @click="navigateToWrite">
            <div class="extreme-label">Shortest scene</div>
            <div class="extreme-title">{{ store.stats.shortest_scene.title }}</div>
            <div>
              <span class="extreme-count">{{ formatNumber(store.stats.shortest_scene.word_count) }}</span>
              <span class="extreme-unit">words</span>
            </div>
          </div>
          <div v-else class="scene-extreme-card">
            <div class="extreme-label">Shortest scene</div>
            <div style="color: var(--wda-text-muted); font-size: 0.85rem">No scenes yet.</div>
          </div>
        </div>
      </template>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStatisticsStore } from '@/stores/statistics'
import { useAuthStore } from '@/stores/auth'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const route = useRoute()
const router = useRouter()
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

function navigateToWrite() {
  router.push(`/projects/${projectId}/write`)
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
    getComputedStyle(document.documentElement).getPropertyValue('--wda-primary').trim() || '#F4A825'

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
          grid: { color: 'rgba(255,255,255,.06)' },
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
