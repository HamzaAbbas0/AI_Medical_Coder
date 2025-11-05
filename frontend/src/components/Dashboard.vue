<template>
  <div class="dashboard-container p-4">

    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold text-secondary mb-1">Medical Coding Dashboard</h3>
        <small class="text-muted">{{ formattedDate }}</small>
      </div>
    </div>

    <!-- Upload Box -->
    <div
      class="upload-box p-5 text-center rounded-3 border border-dashed"
      @drop.prevent="handleDrop"
      @dragover.prevent
    >
      <i class="fa-solid fa-file-arrow-up fa-3x text-teal mb-3"></i>
      <h5 class="fw-semibold mb-3">Upload Medical Document</h5>
      <p class="text-muted mb-4">
        Drop your PDF or DOCX file here, or click below to select a file.
      </p>

      <input
        id="fileInput"
        type="file"
        accept=".pdf,.doc,.docx"
        class="d-none"
        @change="handleFileSelect"
      />

      <button class="btn btn-teal px-4 py-2" @click="triggerFileInput">
        <i class="fa-solid fa-upload me-2"></i> Choose File
      </button>
    </div>

    <!-- Uploading Spinner -->
    <div v-if="loading" class="text-center my-4">
      <div class="spinner-border text-teal" role="status"></div>
      <p class="mt-2 text-muted">Processing document, please wait...</p>
    </div>

    <!-- Uploaded file list -->
    <div v-if="selectedFiles.length" class="mt-4">
      <h6 class="fw-semibold mb-3">Selected Files:</h6>
      <ul class="list-group">
        <li
          v-for="(file, index) in selectedFiles"
          :key="index"
          class="list-group-item d-flex justify-content-between align-items-center"
        >
          {{ file.name }}
          <span class="badge bg-secondary">
            {{ (file.size / 1024).toFixed(1) }} KB
          </span>
        </li>
      </ul>
    </div>

    <!-- Results Table -->
    <div v-if="groups.length" class="mt-5 table-responsive bdr">
      <table class="table table-bordered align-middle">
        <thead class="table-light">
          <tr>
            <th style="width: 20%">Type</th>
            <th style="width: 20%">Code</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody v-for="group in groups" :key="group.title">
          <tr v-for="(code, idx) in group.codes" :key="idx">
            <td
              v-if="idx === 0"
              :rowspan="group.codes.length"
              class="fw-semibold"
            >
              {{ group.title }}
            </td>
            <td>{{ code.code }}
            </td>
            <td>{{ code.description }}
              <div v-if="code.description_modifier" class="text-muted small mt-1">
              <strong>Modifier: </strong>{{ code.modifier }} <br>
            <strong>Modifier Description:</strong> {{ code.description_modifier }}
          </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script>
import { uploadDocument } from '../api/documents'

export default {
  data() {
    return {
      selectedFiles: [],
      formattedDate: '',
      groups: [], // holds ICD / CPT / HCPCS
      loading: false, // spinner control
    }
  },
  created() {
    const today = new Date()
    this.formattedDate = today.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  },
  methods: {
    // ✅ triggers hidden file input
    triggerFileInput() {
      document.getElementById('fileInput').click()
    },

    // ✅ handles manual file selection
    async handleFileSelect(e) {
      const newFiles = Array.from(e.target.files)
      await this.processFiles(newFiles)
      e.target.value = null
    },

    // ✅ handles drag-and-drop
    async handleDrop(e) {
      const newFiles = Array.from(e.dataTransfer.files)
      await this.processFiles(newFiles)
    },

    // ✅ uploads file → backend → updates results
    async processFiles(files) {
      this.selectedFiles = [...this.selectedFiles, ...files]
      const file = files[0]
      if (!file) return

      try {
        this.loading = true
        const res = await uploadDocument(file)
        this.loading = false

        if (res.status === 'success') {
          this.groups = normalizeResults(res)
        } else {
          alert('Processing failed: ' + res.message)
        }
      } catch (err) {
        this.loading = false
        console.error('❌ Upload error:', err)
        alert('Upload failed. Check console for details.')
      }
    },
  },
}

// helper to standardize display
function normalizeResults(payload) {
  const out = []
  if (payload.icd_codes?.icd10_codes) {
    out.push({ title: 'ICD-10 Codes', codes: payload.icd_codes.icd10_codes })
  }
  if (payload.cpt_codes?.cpt_codes) {
    out.push({ title: 'CPT Codes', codes: payload.cpt_codes.cpt_codes })
  }
  if (payload.cpt_codes?.hcpcs_codes) {
    out.push({ title: 'HCPCS Codes', codes: payload.cpt_codes.hcpcs_codes })
  }
  return out
}
</script>

<style scoped>
.center-highlight td {
  background-color: #f1feff !important;
}

.table tbody tr:nth-child(even) td {
  background-color: #f1feff;
}

.date-box {
  border: 1px solid #e5e5e5;
  background-color: #ffffff;
  padding: 10px 10px;
  border-radius: 15px;
  color: #3e3e3e !important;
}

.header-icon {
  border-left: 1px solid #b4bdbd;
  height: 25px;
}

.header-text {
  padding-left: 10px;
}

.cursor-pointer {
  cursor: pointer;
}

.dashboard-container {
  min-height: 100vh;
  background-color: #ffffff;
}

.fa-file {
  color: #b4bdbd !important;
}

.file-text {
  color: #959d9e !important;
}

.upload-box {
  background-color: #f1feff;
  border: 2px dashed #0a8588 !important;
}

.btn-teal {
  background-color: #0a8588;
  color: #fff;
  border: none;
}

.btn-teal:hover {
  background-color: #087375;
  color: #fff;
}

.bdr {
  border-radius: 6px;
  overflow: hidden;
}
</style>
