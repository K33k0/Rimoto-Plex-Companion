<template>
  <div class="container">
    <b-table :data="info">
      <template slot-scope="props">
        <b-table-column field="id" label="ID">{{ props.row.id }}</b-table-column>
        <b-table-column field="path" label="Path">{{ props.row.path }}</b-table-column>
        <b-table-column field="downloaded_at" label="Download Time">{{ props.row.downloaded_at }}</b-table-column>
        <b-table-column field="scanned_at" label="Scanned At">{{ props.row.scanned_at }}</b-table-column>
        <b-table-column field="version_number" label="Version Number">{{ props.row.version_number }}</b-table-column>
        <b-table-column field="scan_attempts" label="Scan Attempts">{{ props.row.scan_attempts }}</b-table-column>
      </template>
    </b-table>
    <b-button @click="getQueue">Fetch</b-button>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'queue',
  data () {
    return {
      info: []
    }
  },
  methods: {
    getQueue () {
      axios.get('http://127.0.0.1:8000/queue')
      .then(response => (this.info = response.data))
    }
  }
}
</script>
