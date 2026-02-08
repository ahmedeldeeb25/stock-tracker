import client from './client'

export const stocksApi = {
  // Get all stocks
  getAll(params = {}) {
    return client.get('/stocks', { params })
  },

  // Get single stock
  getBySymbol(symbol) {
    return client.get(`/stocks/${symbol}`)
  },

  // Create stock
  create(data) {
    return client.post('/stocks', data)
  },

  // Update stock
  update(id, data) {
    return client.put(`/stocks/${id}`, data)
  },

  // Delete stock
  delete(id) {
    return client.delete(`/stocks/${id}`)
  },

  // Fetch company info
  fetchInfo(id, force = false) {
    return client.post(`/stocks/${id}/fetch-info`, { force })
  },

  // Get stock status
  getStatus(id) {
    return client.get(`/stocks/${id}/status`)
  },

  // Get stock targets
  getTargets(id) {
    return client.get(`/stocks/${id}/targets`)
  },

  // Add target to stock
  addTarget(id, data) {
    return client.post(`/stocks/${id}/targets`, data)
  },

  // Add tag to stock
  addTag(id, tagId) {
    return client.post(`/stocks/${id}/tags`, { tag_id: tagId })
  },

  // Remove tag from stock
  removeTag(id, tagId) {
    return client.delete(`/stocks/${id}/tags/${tagId}`)
  },

  // Add timeframe to stock
  addTimeframe(id, timeframeId) {
    return client.post(`/stocks/${id}/timeframes`, { timeframe_id: timeframeId })
  },

  // Remove timeframe from stock
  removeTimeframe(id, timeframeId) {
    return client.delete(`/stocks/${id}/timeframes/${timeframeId}`)
  },

  // Get stock notes
  getNotes(id, params = {}) {
    return client.get(`/stocks/${id}/notes`, { params })
  },

  // Add note to stock
  addNote(id, data) {
    return client.post(`/stocks/${id}/notes`, data)
  }
}

export const targetsApi = {
  // Update target
  update(id, data) {
    return client.put(`/targets/${id}`, data)
  },

  // Delete target
  delete(id) {
    return client.delete(`/targets/${id}`)
  },

  // Toggle target active status
  toggle(id) {
    return client.patch(`/targets/${id}/toggle`)
  }
}

export const tagsApi = {
  // Get all tags
  getAll() {
    return client.get('/tags')
  },

  // Create tag
  create(data) {
    return client.post('/tags', data)
  },

  // Update tag
  update(id, data) {
    return client.put(`/tags/${id}`, data)
  },

  // Delete tag
  delete(id) {
    return client.delete(`/tags/${id}`)
  }
}

export const notesApi = {
  // Get note
  get(id) {
    return client.get(`/notes/${id}`)
  },

  // Update note
  update(id, data) {
    return client.put(`/notes/${id}`, data)
  },

  // Delete note
  delete(id) {
    return client.delete(`/notes/${id}`)
  }
}

export const pricesApi = {
  // Get single price
  get(symbol) {
    return client.get(`/prices/${symbol}`)
  },

  // Get batch prices
  getBatch(symbols) {
    return client.post('/prices/batch', { symbols })
  }
}

export const alertsApi = {
  // Get all alerts
  getAll(params = {}) {
    return client.get('/alerts', { params })
  },

  // Delete alert
  delete(id) {
    return client.delete(`/alerts/${id}`)
  }
}

export const timeframesApi = {
  // Get all timeframes
  getAll() {
    return client.get('/timeframes')
  },

  // Get timeframe by ID
  get(id) {
    return client.get(`/timeframes/${id}`)
  },

  // Create timeframe
  create(data) {
    return client.post('/timeframes', data)
  },

  // Update timeframe
  update(id, data) {
    return client.put(`/timeframes/${id}`, data)
  },

  // Delete timeframe
  delete(id) {
    return client.delete(`/timeframes/${id}`)
  }
}
