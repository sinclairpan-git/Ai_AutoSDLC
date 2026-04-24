<script setup lang="ts">
import { frontendDeliveryContext } from "./generated/frontend-delivery-context";
import {
  publicPrimeVueProviderComponents,
  publicPrimeVueProviderHelpers,
} from "./generated/provider-adapter";

const pageSchemas = frontendDeliveryContext.pageSchemas;
const providerMappings = frontendDeliveryContext.providerMappings;
const providerComponents = publicPrimeVueProviderComponents;
const ProviderColumn = publicPrimeVueProviderHelpers.Column;

const statusOptions = [
  { label: "Active", value: "active" },
  { label: "Draft", value: "draft" },
  { label: "Blocked", value: "blocked" },
];

const tableRows = [
  { id: "ws-001", name: "Search workspace", owner: "Growth", status: "Active" },
  { id: "ws-002", name: "Revenue dashboard", owner: "Analytics", status: "Draft" },
  { id: "ws-003", name: "Partner onboarding", owner: "Operations", status: "Blocked" },
];
</script>

<template>
  <main class="delivery-shell">
    <component :is="providerComponents.UiPageHeader.component" class="page-header">
      <template #start>
        <div>
          <p class="delivery-eyebrow">{{ frontendDeliveryContext.deliveryEntryId }}</p>
          <h1 class="delivery-title">PrimeVue adapter 已落地</h1>
          <p class="delivery-subtitle">
            下载到项目中的组件通过 generated provider adapter 进入 Kernel 语义层，不再只是包名清单。
          </p>
        </div>
      </template>
      <template #end>
        <component
          :is="providerComponents.UiButton.component"
          label="Create workspace"
          severity="contrast"
        />
      </template>
    </component>

    <section class="hero-grid">
      <component :is="providerComponents.UiCard.component" class="hero-card">
        <template #title>Kernel to Provider Mapping</template>
        <template #subtitle>
          {{ frontendDeliveryContext.effectiveProviderId }} / {{
            frontendDeliveryContext.effectiveStylePackId
          }}
        </template>
        <template #content>
          <component
            :is="providerComponents.UiResult.component"
            severity="success"
            variant="outlined"
            class="result-banner"
          >
            {{ providerMappings.length }} semantic components are now mapped to PrimeVue
            implementations.
          </component>
          <component
            :is="providerComponents.UiForm.component"
            legend="Workspace query"
            class="form-shell"
          >
            <div class="form-grid">
              <component :is="providerComponents.UiSearchBar.component" class="search-bar">
                <component
                  :is="providerComponents.UiInput.component"
                  placeholder="Search workspaces"
                />
                <component :is="providerComponents.UiButton.component" label="Search" />
              </component>
              <component
                :is="providerComponents.UiFormItem.component"
                class="field-shell"
                variant="on"
              >
                <component
                  :is="providerComponents.UiSelect.component"
                  :options="statusOptions"
                  optionLabel="label"
                  placeholder="Lifecycle status"
                  class="full-width"
                />
                <label>Status</label>
              </component>
            </div>
          </component>
        </template>
      </component>

      <component :is="providerComponents.UiCard.component" class="hero-card">
        <template #title>Page Schema Coverage</template>
        <template #content>
          <div class="schema-grid">
            <component
              :is="providerComponents.UiCard.component"
              v-for="pageSchema in pageSchemas"
              :key="pageSchema.pageSchemaId"
              class="schema-card"
            >
              <template #title>{{ pageSchema.pageSchemaId }}</template>
              <template #subtitle>{{ pageSchema.pageRecipeId }}</template>
              <template #content>
                <ul class="component-chip-list">
                  <li
                    v-for="componentId in pageSchema.componentIds"
                    :key="componentId"
                    class="component-chip"
                  >
                    {{ componentId }}
                  </li>
                </ul>
              </template>
            </component>
          </div>
        </template>
      </component>
    </section>

    <component :is="providerComponents.UiToolbar.component" class="results-toolbar">
      <template #start>
        <div>
          <p class="toolbar-kicker">Managed frontend</p>
          <strong>Mapped list recipe preview</strong>
        </div>
      </template>
      <template #end>
        <component
          :is="providerComponents.UiButton.component"
          label="Export CSV"
          severity="secondary"
          variant="outlined"
        />
      </template>
    </component>

    <component
      :is="providerComponents.UiSection.component"
      header="Search list workspace"
      class="results-panel"
    >
      <component
        :is="providerComponents.UiTable.component"
        :value="tableRows"
        stripedRows
        tableStyle="min-width: 100%"
      >
        <component :is="ProviderColumn" field="name" header="Workspace" />
        <component :is="ProviderColumn" field="owner" header="Owner" />
        <component :is="ProviderColumn" field="status" header="Status" />
      </component>
      <div class="pagination-row">
        <component
          :is="providerComponents.UiPagination.component"
          :rows="5"
          :totalRecords="tableRows.length"
          :first="0"
          template="PrevPageLink PageLinks NextPageLink"
        />
      </div>
    </component>

    <section class="state-grid">
      <component :is="providerComponents.UiCard.component" class="state-card">
        <template #title>Loading state</template>
        <template #content>
          <div class="state-preview">
            <component :is="providerComponents.UiSpinner.component" strokeWidth="6" />
            <span>PrimeVue spinner is bound to the Kernel loading semantic.</span>
          </div>
        </template>
      </component>

      <component :is="providerComponents.UiCard.component" class="state-card">
        <template #title>No results state</template>
        <template #content>
          <component
            :is="providerComponents.UiEmpty.component"
            severity="secondary"
            variant="outlined"
          >
            No workspace matched the current filters.
          </component>
        </template>
      </component>
    </section>
  </main>
</template>

<style scoped>
:global(:root) {
  color-scheme: light;
}

.delivery-shell {
  --surface: rgba(255, 255, 255, 0.88);
  --surface-strong: #ffffff;
  --surface-border: rgba(15, 23, 42, 0.08);
  --text-strong: #10233c;
  --text-muted: #506273;
  --brand: #0f766e;
  --brand-soft: rgba(15, 118, 110, 0.14);
  margin: 0 auto;
  min-height: 100vh;
  max-width: 1200px;
  padding: 40px 24px 72px;
  color: var(--text-strong);
  background:
    radial-gradient(circle at top left, rgba(14, 165, 233, 0.18), transparent 28%),
    radial-gradient(circle at top right, rgba(16, 185, 129, 0.14), transparent 24%),
    linear-gradient(180deg, #f4fbfb 0%, #eef4ff 48%, #f7fafc 100%);
  font-family: "Avenir Next", "Segoe UI", sans-serif;
}

.page-header {
  margin-bottom: 28px;
  padding: 18px 20px;
  border: 1px solid var(--surface-border);
  border-radius: 22px;
  background: var(--surface);
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(18px);
}

.delivery-eyebrow {
  margin: 0 0 8px;
  color: var(--brand);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.delivery-title {
  margin: 0;
  font-size: clamp(2.2rem, 4vw, 3.6rem);
  line-height: 1.02;
}

.delivery-subtitle {
  margin: 10px 0 0;
  max-width: 52rem;
  color: var(--text-muted);
  font-size: 1rem;
  line-height: 1.6;
}

.hero-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.hero-card,
.schema-card,
.state-card,
.results-panel {
  border-radius: 22px;
  border: 1px solid var(--surface-border);
  background: var(--surface-strong);
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.08);
}

.result-banner {
  margin-bottom: 18px;
}

.form-shell {
  background: linear-gradient(180deg, rgba(241, 245, 249, 0.7), rgba(255, 255, 255, 0.96));
}

.form-grid {
  display: grid;
  grid-template-columns: 1.4fr minmax(180px, 260px);
  gap: 16px;
  align-items: end;
}

.search-bar,
.field-shell {
  width: 100%;
}

.full-width {
  width: 100%;
}

.schema-grid {
  display: grid;
  gap: 14px;
}

.component-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.component-chip {
  padding: 6px 10px;
  border-radius: 999px;
  background: var(--brand-soft);
  color: var(--brand);
  font-size: 0.85rem;
  font-weight: 600;
}

.results-toolbar {
  margin-bottom: 16px;
  padding: 10px 4px;
  border-radius: 18px;
  border: 1px solid var(--surface-border);
  background: var(--surface);
}

.toolbar-kicker {
  margin: 0 0 4px;
  color: var(--text-muted);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.results-panel {
  margin-bottom: 24px;
}

.pagination-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.state-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
}

.state-preview {
  display: flex;
  align-items: center;
  gap: 14px;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .delivery-shell {
    padding: 24px 16px 48px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    padding: 16px;
  }
}
</style>
