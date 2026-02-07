# Common Patterns & Best Practices

**Last Updated**: February 7, 2026

Code patterns and conventions used in the Stock Tracker project. Follow these when adding new features.

---

## 🎨 Vue 3 Component Patterns

### Component Structure (Composition API)

```vue
<template>
  <div class="component-name">
    <!-- Template content -->
    <button @click="handleAction">Action</button>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { someApi } from '@/api'

export default {
  name: 'ComponentName',
  props: {
    propName: {
      type: String,
      required: true
    }
  },
  emits: ['event-name'],
  setup(props, { emit }) {
    // Reactive state
    const data = ref(null)
    const loading = ref(false)

    // Computed values
    const computed = computed(() => {
      return props.propName.toUpperCase()
    })

    // Methods
    const handleAction = async () => {
      loading.value = true
      try {
        await someApi.doSomething()
        emit('event-name')
      } catch (error) {
        console.error(error)
      } finally {
        loading.value = false
      }
    }

    // Lifecycle
    onMounted(() => {
      // Initialize
    })

    return {
      data,
      loading,
      computed,
      handleAction
    }
  }
}
</script>

<style scoped>
.component-name {
  /* Component-specific styles */
}
</style>
```

---

## 📦 Modal Pattern (Bootstrap)

### Modal Component

```vue
<template>
  <div class="modal fade" id="myModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Modal Title</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <!-- Form fields -->
            <button type="submit" :disabled="submitting">Submit</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { someApi } from '@/api'

export default {
  name: 'MyModal',
  props: {
    resourceId: {
      type: Number,
      required: true
    }
  },
  emits: ['resource-updated'],
  setup(props, { emit }) {
    const formData = ref({
      field: ''
    })
    const submitting = ref(false)
    const errorMessage = ref('')

    const resetForm = () => {
      formData.value = { field: '' }
      errorMessage.value = ''
    }

    const handleSubmit = async () => {
      submitting.value = true
      errorMessage.value = ''

      try {
        await someApi.update(props.resourceId, formData.value)

        // Close modal
        const modal = document.getElementById('myModal')
        const modalInstance = window.bootstrap.Modal.getInstance(modal)
        modalInstance.hide()

        resetForm()
        emit('resource-updated')
      } catch (error) {
        errorMessage.value = error.response?.data?.error || 'Failed'
      } finally {
        submitting.value = false
      }
    }

    return {
      formData,
      submitting,
      errorMessage,
      handleSubmit
    }
  }
}
</script>
```

### Opening Modal from Parent

```vue
<script>
import { ref } from 'vue'
import MyModal from '@/components/MyModal.vue'

export default {
  components: { MyModal },
  setup() {
    const resourceId = ref(1)

    const showModal = () => {
      const modal = new window.bootstrap.Modal(
        document.getElementById('myModal')
      )
      modal.show()
    }

    const handleUpdate = () => {
      // Refresh data
      loadData()
    }

    return {
      resourceId,
      showModal,
      handleUpdate
    }
  }
}
</script>

<template>
  <button @click="showModal">Open Modal</button>
  <MyModal
    :resource-id="resourceId"
    @resource-updated="handleUpdate"
  />
</template>
```

---

## 🗄️ Pinia Store Pattern

```javascript
// stores/resource.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { resourceApi } from '@/api'

export const useResourceStore = defineStore('resource', () => {
  // State
  const items = ref([])
  const currentItem = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const filteredItems = computed(() => {
    return items.value.filter(item => item.active)
  })

  // Actions
  const fetchItems = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await resourceApi.getAll()
      items.value = response.data.items
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  const fetchItem = async (id) => {
    loading.value = true
    error.value = null
    try {
      const response = await resourceApi.get(id)
      currentItem.value = response.data
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  const createItem = async (data) => {
    const response = await resourceApi.create(data)
    items.value.push(response.data)
    return response.data
  }

  const deleteItem = async (id) => {
    await resourceApi.delete(id)
    items.value = items.value.filter(item => item.id !== id)
  }

  return {
    // State
    items,
    currentItem,
    loading,
    error,
    // Getters
    filteredItems,
    // Actions
    fetchItems,
    fetchItem,
    createItem,
    deleteItem
  }
})
```

### Using Store in Component

```vue
<script>
import { onMounted } from 'vue'
import { useResourceStore } from '@/stores/resource'

export default {
  setup() {
    const resourceStore = useResourceStore()

    onMounted(() => {
      resourceStore.fetchItems()
    })

    const handleDelete = async (id) => {
      if (confirm('Are you sure?')) {
        await resourceStore.deleteItem(id)
      }
    }

    return {
      items: resourceStore.items,
      loading: resourceStore.loading,
      handleDelete
    }
  }
}
</script>
```

---

## 🔌 API Client Pattern

### API Client Setup

```javascript
// api/client.js
import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.DEV
    ? 'http://localhost:5555/api'
    : '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor (if needed)
client.interceptors.request.use(
  config => {
    // Add auth token, etc.
    return config
  },
  error => Promise.reject(error)
)

// Response interceptor (if needed)
client.interceptors.response.use(
  response => response,
  error => {
    // Global error handling
    return Promise.reject(error)
  }
)

export default client
```

### API Method Definitions

```javascript
// api/index.js
import client from './client'

export const resourceApi = {
  getAll(params = {}) {
    return client.get('/resource', { params })
  },

  get(id) {
    return client.get(`/resource/${id}`)
  },

  create(data) {
    return client.post('/resource', data)
  },

  update(id, data) {
    return client.put(`/resource/${id}`, data)
  },

  delete(id) {
    return client.delete(`/resource/${id}`)
  },

  // Custom action
  customAction(id, data) {
    return client.post(`/resource/${id}/action`, data)
  }
}
```

---

## 🐍 Flask Route Pattern

```python
# web/routes/resource.py
from flask import Blueprint, request, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

resource_bp = Blueprint('resource', __name__)


@resource_bp.route('', methods=['GET'])
def get_resources():
    """Get all resources.

    Query Params:
        filter: Optional filter
        limit: Number of results
    """
    try:
        filter_value = request.args.get('filter')
        limit = request.args.get('limit', type=int)

        resources = current_app.db_manager.get_resources(
            filter=filter_value,
            limit=limit
        )

        return jsonify({
            "resources": [
                {
                    "id": r.id,
                    "name": r.name,
                    "created_at": r.created_at.isoformat()
                }
                for r in resources
            ],
            "total": len(resources)
        })

    except Exception as e:
        logger.error(f"Error fetching resources: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@resource_bp.route('/<int:resource_id>', methods=['GET'])
def get_resource(resource_id):
    """Get single resource."""
    try:
        resource = current_app.db_manager.get_resource(resource_id)

        if not resource:
            return jsonify({"error": "Resource not found"}), 404

        return jsonify({
            "id": resource.id,
            "name": resource.name,
            "details": resource.details
        })

    except Exception as e:
        logger.error(f"Error fetching resource {resource_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@resource_bp.route('', methods=['POST'])
def create_resource():
    """Create a new resource.

    Body:
        {
            "name": "Resource Name",
            "details": "Optional details"
        }
    """
    try:
        data = request.get_json()

        # Validation
        if not data.get('name'):
            return jsonify({"error": "Name is required"}), 400

        # Create
        resource_id = current_app.db_manager.create_resource(
            name=data['name'],
            details=data.get('details')
        )

        return jsonify({
            "id": resource_id,
            "success": True
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating resource: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@resource_bp.route('/<int:resource_id>', methods=['PUT'])
def update_resource(resource_id):
    """Update a resource."""
    try:
        data = request.get_json()

        success = current_app.db_manager.update_resource(
            resource_id=resource_id,
            name=data.get('name'),
            details=data.get('details')
        )

        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Resource not found"}), 404

    except Exception as e:
        logger.error(f"Error updating resource {resource_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@resource_bp.route('/<int:resource_id>', methods=['DELETE'])
def delete_resource(resource_id):
    """Delete a resource."""
    try:
        success = current_app.db_manager.delete_resource(resource_id)

        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Resource not found"}), 404

    except Exception as e:
        logger.error(f"Error deleting resource {resource_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
```

### Registering Blueprint

```python
# web/app.py
from routes.resource import resource_bp

app.register_blueprint(resource_bp, url_prefix='/api/resource')
```

---

## 🎨 CSS Patterns

### Scoped Styles
```vue
<style scoped>
/* Component-specific styles */
.my-component {
  padding: 1rem;
}

/* Style child components with :deep() */
:deep(.child-class) {
  color: blue;
}

/* Quill editor styling */
:deep(.ql-editor) {
  min-height: 200px;
}
</style>
```

### Bootstrap Utility Classes
```html
<!-- Spacing -->
<div class="mt-3 mb-4 p-2">...</div>

<!-- Flexbox -->
<div class="d-flex justify-content-between align-items-center">...</div>

<!-- Grid -->
<div class="row">
  <div class="col-md-6">...</div>
  <div class="col-md-6">...</div>
</div>

<!-- Buttons -->
<button class="btn btn-primary btn-sm">Primary</button>
<button class="btn btn-outline-danger">Delete</button>

<!-- Badges -->
<span class="badge bg-success">Active</span>
<span class="badge bg-secondary">Inactive</span>

<!-- Cards -->
<div class="card">
  <div class="card-header">Header</div>
  <div class="card-body">Content</div>
  <div class="card-footer">Footer</div>
</div>
```

---

## ⚠️ Error Handling Patterns

### Frontend
```javascript
const handleAction = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    await someApi.action()
    // Success
  } catch (error) {
    // Extract error message
    errorMessage.value =
      error.response?.data?.error ||
      error.message ||
      'Something went wrong'

    console.error('Action failed:', error)
  } finally {
    loading.value = false
  }
}
```

### Backend
```python
try:
    # Operation
    result = do_something()
    return jsonify({"success": True, "result": result})

except ValueError as e:
    # Client error (400)
    return jsonify({"error": str(e)}), 400

except NotFoundError as e:
    # Not found (404)
    return jsonify({"error": str(e)}), 404

except Exception as e:
    # Server error (500)
    logger.error(f"Operation failed: {e}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500
```

---

## ✅ Validation Patterns

### Frontend Form Validation
```vue
<template>
  <form @submit.prevent="handleSubmit">
    <input
      v-model="formData.field"
      :class="{ 'is-invalid': errors.field }"
      required
    >
    <div class="invalid-feedback">{{ errors.field }}</div>

    <button :disabled="!isValid || submitting">Submit</button>
  </form>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  setup() {
    const formData = ref({ field: '' })
    const errors = ref({})

    const isValid = computed(() => {
      return formData.value.field.length > 0
    })

    const validate = () => {
      errors.value = {}

      if (!formData.value.field) {
        errors.value.field = 'Field is required'
        return false
      }

      if (formData.value.field.length < 3) {
        errors.value.field = 'Must be at least 3 characters'
        return false
      }

      return true
    }

    const handleSubmit = async () => {
      if (!validate()) return

      // Submit
    }

    return { formData, errors, isValid, handleSubmit }
  }
}
</script>
```

---

## 🔄 Naming Conventions

### Files
- **Components**: `PascalCase.vue` (e.g., `AddStockModal.vue`)
- **Views**: `PascalCase.vue` (e.g., `Dashboard.vue`)
- **Stores**: `camelCase.js` (e.g., `stocks.js`)
- **Utils**: `camelCase.js` (e.g., `formatters.js`)
- **Python**: `snake_case.py` (e.g., `stock_fetcher.py`)
- **Scripts**: `kebab-case.sh` (e.g., `start-all.sh`)

### Variables & Functions
- **Vue/JS**: `camelCase` (e.g., `handleSubmit`, `isValid`)
- **Python**: `snake_case` (e.g., `get_stock`, `is_active`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `API_BASE_URL`)

### CSS Classes
- **Component classes**: `kebab-case` (e.g., `.stock-card`)
- **Bootstrap classes**: Follow Bootstrap conventions
- **Custom utilities**: `kebab-case` (e.g., `.custom-badge`)

---

## 📝 Documentation Patterns

### Component JSDoc
```javascript
/**
 * Modal for adding price targets to stocks
 *
 * @component
 * @example
 * <AddTargetModal
 *   :stock-id="123"
 *   @target-added="handleAdded"
 * />
 */
export default {
  name: 'AddTargetModal',
  // ...
}
```

### Function JSDoc
```javascript
/**
 * Formats a price value as USD currency
 *
 * @param {number} price - The price to format
 * @returns {string} Formatted price (e.g., "$210.32")
 */
export function formatPrice(price) {
  return `$${price.toFixed(2)}`
}
```

---

## 🎯 Follow These Patterns!

When adding new code, reference these patterns to maintain consistency across the codebase. If you need to deviate from these patterns, document why in your session handover.
