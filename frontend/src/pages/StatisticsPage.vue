<template>
  <q-layout>
    <q-page-container>
      <q-page class="q-pa-md" style="max-width: 900px; margin: 0 auto">
        <q-btn
          flat
          icon="arrow_back"
          label="Back to Project"
          :to="`/projects/${projectId}`"
          no-caps
          class="q-mb-md"
        />

        <div class="text-h4 q-mb-md">Writing Statistics</div>

        <div v-if="store.loading" class="text-center q-mt-xl">
          <q-spinner size="lg" />
        </div>

        <div v-else-if="store.error" class="text-center q-mt-xl text-negative">
          {{ store.error }}
        </div>

        <template v-else-if="store.stats">
          <!-- Summary cards -->
          <div class="row q-col-gutter-md q-mb-lg">
            <div class="col-6 col-sm-3">
              <q-card flat bordered>
                <q-card-section class="text-center">
                  <div class="text-h5 text-primary">{{ formatNumber(store.stats.total_words) }}</div>
                  <div class="text-caption text-grey">Total Words</div>
                </q-card-section>
              </q-card>
            </div>
            <div class="col-6 col-sm-3">
              <q-card flat bordered>
                <q-card-section class="text-center">
                  <div class="text-h5 text-primary">{{ store.stats.total_scenes }}</div>
                  <div class="text-caption text-grey">Total Scenes</div>
                </q-card-section>
              </q-card>
            </div>
            <div class="col-6 col-sm-3">
              <q-card flat bordered>
                <q-card-section class="text-center">
                  <div class="text-h5 text-primary">
                    {{ store.stats.writing_streak }}
                    <q-icon v-if="store.stats.writing_streak > 0" name="whatshot" color="orange" size="sm" />
                  </div>
                  <div class="text-caption text-grey">Writing Streak</div>
                </q-card-section>
              </q-card>
            </div>
            <div class="col-6 col-sm-3">
              <q-card flat bordered>
                <q-card-section class="text-center">
                  <div class="text-h5 text-primary">{{ store.stats.total_days_written }}</div>
                  <div class="text-caption text-grey">Days Written</div>
                </q-card-section>
              </q-card>
            </div>
          </div>

          <!-- Daily word goal section -->
          <q-card v-if="authStore.showWordGoal" flat bordered class="q-mb-lg">
            <q-card-section>
              <div class="text-h6 q-mb-sm">Today's Progress</div>
              <div v-if="todayWords === null" class="text-grey text-caption">
                No writing data yet for today.
              </div>
              <template v-else>
                <div class="row items-center q-mb-sm">
                  <div class="col">
                    <div class="text-body2">
                      <template v-if="todayWords >= goalTarget">
                        <q-icon name="check_circle" color="positive" size="sm" class="q-mr-xs" />
                        <span class="text-positive">Goal reached!</span>
                        {{ formatNumber(todayWords) }} / {{ formatNumber(goalTarget) }} words.
                      </template>
                      <template v-else>
                        Goal: {{ formatNumber(goalTarget) }} words/day
                      </template>
                    </div>
                  </div>
                  <div class="col-auto text-caption text-grey">
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
                <div class="text-caption text-grey">
                  <router-link to="/settings">Change goal or turn off in Settings.</router-link>
                </div>
              </template>
            </q-card-section>
          </q-card>

          <!-- Words per day chart -->
          <q-card flat bordered class="q-mb-lg">
            <q-card-section>
              <div class="text-h6 q-mb-sm">Words per Day</div>
              <div v-if="!hasData" class="text-grey text-center q-py-xl">
                No writing data yet. Start writing to see your stats here.
              </div>
              <div v-else>
                <div class="chart-container" style="position: relative; height: 250px; width: 100%">
                  <canvas ref="chartCanvas"></canvas>
                </div>
                <div class="text-caption text-grey q-mt-sm text-center">Dates shown in UTC.</div>
              </div>
            </q-card-section>
          </q-card>

          <!-- Longest and shortest scenes -->
          <div class="row q-col-gutter-md">
            <div class="col-12 col-sm-6">
              <q-card flat bordered>
                <q-card-section>
                  <div class="text-caption text-grey q-mb-xs">Longest scene</div>
                  <div v-if="store.stats.longest_scene">
                    <router-link
                      :to="`/projects/${projectId}/write`"
                      class="text-body1 text-primary"
                    >
                      {{ store.stats.longest_scene.title }}
                      <q-icon name="open_in_new" size="sm" class="q-ml-xs" />
                    </router-link>
                    <div class="text-caption text-grey">
                      {{ formatNumber(store.stats.longest_scene.word_count) }} words
                    </div>
                  </div>
                  <div v-else class="text-grey">No scenes yet.</div>
                </q-card-section>
              </q-card>
            </div>
            <div class="col-12 col-sm-6">
              <q-card flat bordered>
                <q-card-section>
                  <div class="text-caption text-grey q-mb-xs">Shortest scene</div>
                  <div v-if="store.stats.shortest_scene">
                    <router-link
                      :to="`/projects/${projectId}/write`"
                      class="text-body1 text-primary"
                    >
                      {{ store.stats.shortest_scene.title }}
                      <q-icon name="open_in_new" size="sm" class="q-ml-xs" />
                    </router-link>
                    <div class="text-caption text-grey">
                      {{ formatNumber(store.stats.shortest_scene.word_count) }} words
                    </div>
                  </div>
                  <div v-else class="text-grey">No scenes yet.</div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </template>
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

  const primaryColor = getComputedStyle(document.documentElement)
    .getPropertyValue('--q-primary')
    .trim() || '#1976D2'

  chartInstance = new Chart(chartCanvas.value, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: values.map((v) => v > 0 ? primaryColor : '#E0E0E0'),
        borderWidth: 0,
        borderRadius: 2,
      }],
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

watch(() => store.stats, () => {
  if (store.stats?.daily_words) {
    nextTick(buildChart)
  }
})

onMounted(async () => {
  await store.fetchStatistics(projectId)
  if (store.stats?.daily_words) {
    await nextTick()
    buildChart()
  }
})
</script>
